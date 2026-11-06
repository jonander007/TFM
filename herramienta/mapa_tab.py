#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mapa_tab.py — "Mapa de zonas" tab of the RADTRAD interface (RADTRAD_GUI.py)

The tab draws the map itself on a Tk canvas: OpenStreetMap, Esri street or satellite tiles
(Web Mercator, as Leaflet), downloaded in the background and cached in cache_teselas/, with the
ship hull, the reactor and the zone circles of Table 4 to scale, a latitude/longitude grid and
the coordinates under the cursor (wheel = zoom, drag = pan, right click = place the ship,
double click = fit). Without internet the zones are drawn on a plain background.
The full Leaflet viewer can still be opened in the browser (served on http://localhost).

Results: zonas_emergencia.json of every run, RUN_N/OUTPUT (base case, E1 + E2) and
RUN_N/OUTPUT/SENS_F1 (meteorological sensitivity), plus psf_batch*/postprocess (console).
"Guardar" writes the ship and the criteria back to the json and regenerates mapa_zonas.html
and mapa_zonas.png in that folder.
"""
from __future__ import annotations

import functools
import http.server
import json
import math
import socketserver
import threading
import webbrowser
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox

import zonas_emergencia as ZE

# Palette of RADTRAD_GUI.py
BG_APP, BG_CARD, BG_INPUT = "#F3F4F6", "#FFFFFF", "#E9EBEE"
BLUE, TEXT, MUTED, BORDER, WHITE, RED = "#1A6FD4", "#1F2328", "#57606A", "#D0D7DE", "#FFFFFF", "#CF222E"
SEA, HULL, REACTOR = "#E4EDF5", "#1F4E79", "#F1C40F"
FONT_UI, FONT_SM, FONT_BOLD = ("Segoe UI", 10), ("Segoe UI", 9), ("Segoe UI Semibold", 10)
FONT_MONO = ("Consolas", 10)

VISIBLES_DEFECTO = ["EAB", "LPZ", "EVAC", "CONF", "PLAN"]     # as visor_zonas.html
ZMAX = 19
_ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/"
CAPAS = {   # base maps (the same as the browser viewer); None = no map
    "OpenStreetMap": dict(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png", jpg=False,
                          atrib="© colaboradores de OpenStreetMap"),
    "Callejero (Esri)": dict(url=_ESRI + "World_Street_Map/MapServer/tile/{z}/{y}/{x}", jpg=True,
                             atrib="© Esri, HERE, Garmin, © OpenStreetMap"),
    "Satélite (Esri)": dict(url=_ESRI + "World_Imagery/MapServer/tile/{z}/{y}/{x}", jpg=True,
                            atrib="© Esri, Maxar, Earthstar Geographics"),
    "Sin mapa": None,
}
# OpenStreetMap's tile policy asks applications to identify themselves and to cache tiles
USER_AGENT = "TFM-ZonasEmergencia-KPFHR/1.0 (herramienta academica, EHU)"


class Teselas:
    """Map tiles: memory + disk cache (cache_teselas/<capa>/<z>/<x>/<y>), downloaded in background
    threads; `aviso` is called on the Tk thread when new tiles are ready."""
    try:                       # JPEG tiles (Esri) are converted to PNG with Pillow; ImageTk is not needed
        from PIL import Image as _Image
        PIL = True
    except ImportError:
        PIL = False

    def __init__(self, widget, carpeta: Path, aviso):
        import concurrent.futures
        self.w, self.dir, self.aviso = widget, carpeta, aviso
        self.mem, self.pend, self.fallos = {}, set(), 0
        self.sin_conexion = False
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self.lock = threading.Lock()
        self.listos = []

    def _ruta(self, capa, z, x, y):
        return self.dir / capa.split(" ")[0] / str(z) / str(x) / f"{y}.{'jpg' if CAPAS[capa]['jpg'] else 'png'}"

    def get(self, capa, z, x, y):
        key = (capa, z, x, y)
        if key in self.mem:
            return self.mem[key]
        f = self._ruta(capa, z, x, y)
        if f.exists():
            img = self._imagen(capa, f.read_bytes())
            if img is not None:
                self._guardar(key, img)
                return img
        if key not in self.pend and not (self.sin_conexion and self.fallos > 20):
            self.pend.add(key)
            self.pool.submit(self._descargar, key, f)
        return None

    def _imagen(self, capa, data):
        try:
            import base64
            if CAPAS[capa]["jpg"]:
                if not self.PIL:
                    return None
                import io
                buf = io.BytesIO()
                self._Image.open(io.BytesIO(data)).convert("RGB").save(buf, "PNG")
                data = buf.getvalue()
            return tk.PhotoImage(data=base64.b64encode(data))
        except Exception:
            return None

    def _guardar(self, key, img):
        self.mem[key] = img
        if len(self.mem) > 600:                       # keep memory bounded
            for k in list(self.mem)[:200]:
                del self.mem[k]

    def _descargar(self, key, f):
        import urllib.request
        capa, z, x, y = key
        url = CAPAS[capa]["url"].format(z=z, x=x, y=y)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
            self.sin_conexion, self.fallos = False, 0
        except Exception:
            self.fallos += 1
            self.sin_conexion = True
            data = None
        with self.lock:
            self.listos.append((key, data))
        try:
            self.w.after(0, self._entregar)
        except Exception:
            pass

    def _entregar(self):                               # Tk thread: PhotoImage must be created here
        with self.lock:
            listos, self.listos = self.listos, []
        nuevo = False
        for key, data in listos:
            self.pend.discard(key)
            if data:
                img = self._imagen(key[0], data)
                if img is not None:
                    self._guardar(key, img); nuevo = True
        if nuevo or listos:
            self.aviso()


ESTADOS = {"menor_que_minimo": "≤ ", "mayor_que_maximo": "> ", "interpolado": "", "sin_datos": ""}


def buscar_resultados(base: Path):
    """[(label, folder)] of the folders with zonas_emergencia.json, newest first."""
    found = []
    for js in list(base.glob("RUN_*/OUTPUT/zonas_emergencia.json")) + \
              list(base.glob("RUN_*/OUTPUT/SENS_F1/zonas_emergencia.json")) + \
              list(base.glob("psf_batch*/postprocess/zonas_emergencia.json")):
        folder = js.parent
        rel = folder.relative_to(base).parts
        if rel[0].startswith("RUN_"):
            label = rel[0] + (" · sensibilidad clase F, 1 m/s" if "SENS_F1" in rel else " · caso base")
        else:
            label = rel[0] + (" · sensibilidad clase F, 1 m/s" if rel[0].endswith("_F1") else " · caso base") + " (consola)"
        found.append((js.stat().st_mtime, label, folder))
    found.sort(key=lambda t: -t[0])
    return [(lbl, f) for _, lbl, f in found]


class _Servidor:
    """One local HTTP server per results folder, alive while the interface is open."""
    def __init__(self):
        self._srv = {}

    def url(self, folder: Path, page: str = "mapa_zonas.html") -> str:
        key = str(folder.resolve())
        if key not in self._srv:
            handler = functools.partial(_QuietHandler, directory=key)
            httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
            httpd.daemon_threads = True
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            self._srv[key] = httpd
        return f"http://localhost:{self._srv[key].server_address[1]}/{page}"


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


SERVIDOR = _Servidor()


class MapaZonasTab(tk.Frame):
    def __init__(self, parent, base_dir: Path):
        super().__init__(parent, bg=BG_APP)
        self.base = Path(base_dir)
        self.data = None            # contents of zonas_emergencia.json
        self.folder = None
        self.sources = []
        self.zone_vars = {}         # clave -> (show BooleanVar, limit StringVar, radius Label)
        self._drag = None
        self.v = {k: tk.StringVar() for k in ("lat", "lon", "rumbo", "eslora", "manga", "popa")}
        self._build()
        self.refrescar()

    # ------------------------------------------------------------------ layout
    def _build(self):
        paned = tk.PanedWindow(self, orient="horizontal", bg=BG_APP, sashwidth=6, bd=0)
        paned.pack(fill="both", expand=True, padx=8, pady=8)
        left = tk.Frame(paned, bg=BG_APP)
        right = tk.Frame(paned, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        paned.add(left, minsize=360, width=420)
        paned.add(right, minsize=360)

        # source
        card = self._card(left, "Resultados")
        row = tk.Frame(card, bg=BG_CARD); row.pack(fill="x")
        self.combo = ttk.Combobox(row, state="readonly", font=FONT_SM)
        self.combo.pack(side="left", fill="x", expand=True)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self._cargar_sel())
        self._btn(row, "⟳", self.refrescar, small=True).pack(side="left", padx=(6, 0))
        self._btn(row, "Abrir…", self._abrir_json, small=True).pack(side="left", padx=(6, 0))
        self.src_info = tk.Label(card, text="", bg=BG_CARD, fg=MUTED, font=FONT_SM, justify="left",
                                 anchor="w", wraplength=380)
        self.src_info.pack(fill="x", pady=(6, 0))

        # zones
        card = self._card(left, "Zonas (Tabla 4)")
        hdr = tk.Frame(card, bg=BG_CARD); hdr.pack(fill="x")
        for txt, w in (("", 3), ("Zona", 7), ("Criterio", 20), ("Límite mSv", 9), ("Radio", 8)):
            tk.Label(hdr, text=txt, bg=BG_CARD, fg=MUTED, font=FONT_SM, width=w, anchor="w").pack(side="left")
        self.zones_box = tk.Frame(card, bg=BG_CARD); self.zones_box.pack(fill="x")
        tk.Label(card, text="Radio: menor distancia a partir de la cual la envolvente de los juegos de fracciones de "
                            "yodo no supera el límite. Cambia el límite para recalcularlo.",
                 bg=BG_CARD, fg=MUTED, font=FONT_SM, wraplength=380, justify="left").pack(fill="x", pady=(6, 0))

        # ship
        card = self._card(left, "Buque")
        grid = tk.Frame(card, bg=BG_CARD); grid.pack(fill="x")
        fields = (("lat", "Latitud"), ("lon", "Longitud"), ("rumbo", "Rumbo (°)"),
                  ("eslora", "Eslora (m)"), ("manga", "Manga (m)"), ("popa", "Reactor a popa (m)"))
        for i, (k, txt) in enumerate(fields):
            tk.Label(grid, text=txt, bg=BG_CARD, fg=MUTED, font=FONT_SM).grid(row=(i // 3) * 2, column=i % 3, sticky="w", padx=3)
            e = tk.Entry(grid, textvariable=self.v[k], width=12, bg=BG_INPUT, relief="flat", font=FONT_MONO)
            e.grid(row=(i // 3) * 2 + 1, column=i % 3, sticky="we", padx=3, pady=(0, 6), ipady=3)
            e.bind("<Return>", lambda ev: self.dibujar())
            e.bind("<FocusOut>", lambda ev: self.dibujar())
        for c in range(3):
            grid.columnconfigure(c, weight=1)
        row = tk.Frame(card, bg=BG_CARD); row.pack(fill="x", pady=(2, 0))
        self._btn(row, "Atraque por defecto (BBG)", self._atraque_defecto, small=True).pack(side="left")
        tk.Label(card, text="Rumbo = dirección de la proa. Las zonas se centran en el reactor. La posición por defecto "
                            "es aproximada: ajústala sobre el satélite en el mapa del navegador.",
                 bg=BG_CARD, fg=MUTED, font=FONT_SM, wraplength=380, justify="left").pack(fill="x", pady=(6, 0))

        # actions
        card = self._card(left, "Mapa")
        self._btn(card, "🌍  Abrir mapa en el navegador (OpenStreetMap / satélite)", self.abrir_navegador).pack(fill="x")
        row = tk.Frame(card, bg=BG_CARD); row.pack(fill="x", pady=(6, 0))
        self._btn(row, "Guardar buque y criterios", self.guardar, small=True).pack(side="left", fill="x", expand=True)
        self._btn(row, "Exportar PNG…", self.exportar_png, small=True).pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.msg = tk.Label(card, text="", bg=BG_CARD, fg=MUTED, font=FONT_SM, wraplength=380, justify="left")
        self.msg.pack(fill="x", pady=(6, 0))

        # map
        top = tk.Frame(right, bg=BG_CARD); top.pack(fill="x")
        tk.Label(top, text="Mapa", bg=BG_CARD, fg=TEXT, font=FONT_BOLD).pack(side="left", padx=(10, 6), pady=6)
        self.capa = tk.StringVar(value="OpenStreetMap")
        cb = ttk.Combobox(top, state="readonly", width=17, textvariable=self.capa, values=list(CAPAS), font=FONT_SM)
        cb.pack(side="left", pady=4)
        cb.bind("<<ComboboxSelected>>", lambda e: (setattr(self.teselas, "fallos", 0), self.dibujar()))
        self._btn(top, "Ajustar", self._ajustar, small=True).pack(side="right", padx=8, pady=4)
        tk.Label(top, text="rueda: zoom · arrastrar: mover · clic derecho: situar el buque",
                 bg=BG_CARD, fg=MUTED, font=FONT_SM).pack(side="right")
        self.cv = tk.Canvas(right, bg=SEA, highlightthickness=0)
        self.cv.pack(fill="both", expand=True)
        bot = tk.Frame(right, bg=BG_CARD); bot.pack(fill="x")
        self.cursor = tk.Label(bot, text="", bg=BG_CARD, fg=TEXT, font=FONT_MONO, anchor="w")
        self.cursor.pack(side="left", padx=10, pady=3)
        self.attrib = tk.Label(bot, text="", bg=BG_CARD, fg=MUTED, font=("Segoe UI", 8), anchor="e")
        self.attrib.pack(side="right", padx=10)
        self.cv.bind("<Configure>", lambda e: self.dibujar())
        self.cv.bind("<MouseWheel>", lambda e: self._zoom_at(e, 1 if e.delta > 0 else -1))
        self.cv.bind("<Button-4>", lambda e: self._zoom_at(e, 1))
        self.cv.bind("<Button-5>", lambda e: self._zoom_at(e, -1))
        self.cv.bind("<ButtonPress-1>", self._drag_start)
        self.cv.bind("<B1-Motion>", self._drag_move)
        self.cv.bind("<ButtonRelease-1>", lambda e: setattr(self, "_drag", None))
        self.cv.bind("<Double-Button-1>", lambda e: self._ajustar())
        self.cv.bind("<Button-3>", self._situar_buque)
        self.cv.bind("<Motion>", self._mostrar_cursor)
        self.cv.bind("<Leave>", lambda e: self.cursor.config(text=""))
        self.teselas = Teselas(self, Path(self.base) / "cache_teselas", self._redibujar_pronto)

    def _card(self, parent, title):
        outer = tk.Frame(parent, bg=BG_CARD, highlightthickness=1, highlightbackground=BORDER)
        outer.pack(fill="x", pady=(0, 8))
        tk.Label(outer, text=title.upper(), bg=BG_CARD, fg=MUTED, font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=10, pady=(8, 2))
        inner = tk.Frame(outer, bg=BG_CARD); inner.pack(fill="x", padx=10, pady=(0, 10))
        return inner

    def _btn(self, parent, text, cmd, small=False):
        return tk.Button(parent, text=text, command=cmd, bg=BG_INPUT if small else BLUE, fg=BLUE if small else WHITE,
                         activebackground=BLUE, activeforeground=WHITE, relief="flat", bd=0, cursor="hand2",
                         font=FONT_SM if small else FONT_BOLD, padx=10, pady=4 if small else 8)

    # ------------------------------------------------------------------ data
    def refrescar(self, seleccionar_ultimo=False):
        """Rescan the results folders (also called when a run finishes)."""
        prev = self.folder
        self.sources = buscar_resultados(self.base)
        self.combo["values"] = [lbl for lbl, _ in self.sources]
        if not self.sources:
            self.src_info.config(text="Sin resultados todavía: ejecuta el pipeline (pestaña 1) o abre un "
                                      "zonas_emergencia.json.")
            if self.data is None:
                self.dibujar()
            return
        idx = 0
        if prev is not None and not seleccionar_ultimo:
            idx = next((i for i, (_, f) in enumerate(self.sources) if f == prev), 0)
        self.combo.current(idx)
        self._cargar_sel()

    def _cargar_sel(self):
        i = self.combo.current()
        if 0 <= i < len(self.sources):
            self.cargar(self.sources[i][1] / "zonas_emergencia.json")

    def _abrir_json(self):
        f = filedialog.askopenfilename(title="zonas_emergencia.json", initialdir=str(self.base),
                                       filetypes=[("zonas_emergencia.json", "*.json")])
        if f:
            self.cargar(Path(f))

    def cargar(self, js: Path):
        try:
            data = json.loads(js.read_text(encoding="utf-8"))
            if "zonas" not in data or "envolventes" not in data:
                raise ValueError("falta «zonas» o «envolventes»")
        except Exception as e:
            messagebox.showerror("Mapa de zonas", f"No se puede leer {js}:\n{e}")
            return
        self.data, self.folder = data, js.parent
        self.v["lat"].set(f"{data.get('lat', ZE.DEFAULT_LAT):.5f}")
        self.v["lon"].set(f"{data.get('lon', ZE.DEFAULT_LON):.5f}")
        self.v["rumbo"].set(f"{data.get('rumbo', ZE.DEFAULT_HEADING):g}")
        self.v["eslora"].set(f"{data.get('eslora_m', ZE.SHIP_LENGTH_M):g}")
        self.v["manga"].set(f"{data.get('manga_m', ZE.SHIP_BEAM_M):g}")
        self.v["popa"].set(f"{data.get('reactor_desde_popa_m', ZE.REACTOR_FROM_STERN_M):g}")
        info = [str(js.parent)]
        if data.get("n_sets"):
            info.append(f"{data['n_sets']} juegos de fracciones de yodo")
        if data.get("escenarios"):
            info.append("escenarios " + " y ".join(data["escenarios"]))
        info += data.get("avisos", [])
        self.src_info.config(text=" · ".join(info))
        self._zonas_ui()
        self.msg.config(text="")
        self._ajustar()

    def _zonas_ui(self):
        for w in self.zones_box.winfo_children():
            w.destroy()
        self.zone_vars = {}
        for z in self.data["zonas"]:
            k = z["clave"]
            show = tk.BooleanVar(value=k in self.data.get("_visibles", VISIBLES_DEFECTO))
            lim = tk.StringVar(value=f"{z['limite_msv']:g}")
            row = tk.Frame(self.zones_box, bg=BG_CARD); row.pack(fill="x", pady=1)
            tk.Checkbutton(row, variable=show, bg=BG_CARD, activebackground=BG_CARD,
                           command=self.dibujar).pack(side="left")
            tk.Label(row, text="●", fg=z.get("color", BLUE), bg=BG_CARD, font=FONT_UI).pack(side="left")
            tk.Label(row, text=k, bg=BG_CARD, fg=TEXT, font=FONT_BOLD, width=5, anchor="w").pack(side="left")
            crit = f"{z.get('magnitud', 'TEDE')}, {z.get('periodo', '')}, {z.get('escenarios', 'E1')}"
            tk.Label(row, text=crit, bg=BG_CARD, fg=MUTED, font=FONT_SM, width=22, anchor="w").pack(side="left")
            e = tk.Entry(row, textvariable=lim, width=8, bg=BG_INPUT, relief="flat", font=FONT_MONO, justify="right")
            e.pack(side="left", padx=4, ipady=2)
            e.bind("<Return>", lambda ev: self.dibujar()); e.bind("<FocusOut>", lambda ev: self.dibujar())
            rl = tk.Label(row, text="", bg=BG_CARD, fg=TEXT, font=FONT_UI, width=9, anchor="e")
            rl.pack(side="left")
            self.zone_vars[k] = (show, lim, rl)
            tip = z.get("nombre", k)
            for w in row.winfo_children():
                w.bind("<Enter>", lambda ev, t=tip: self.msg.config(text=t))

    # ------------------------------------------------------------------ model
    def _num(self, k, default):
        try:
            return float(self.v[k].get().replace(",", "."))
        except ValueError:
            return default

    def buque(self):
        return dict(lat=self._num("lat", ZE.DEFAULT_LAT), lon=self._num("lon", ZE.DEFAULT_LON),
                    rumbo=self._num("rumbo", ZE.DEFAULT_HEADING) % 360,
                    eslora=max(1.0, self._num("eslora", ZE.SHIP_LENGTH_M)),
                    manga=max(1.0, self._num("manga", ZE.SHIP_BEAM_M)),
                    popa=self._num("popa", ZE.REACTOR_FROM_STERN_M))

    def zonas(self):
        """[(zone dict, radius, state, visible)] with the limits typed in the tab."""
        out = []
        if not self.data:
            return out
        for z in self.data["zonas"]:
            show, lim, rl = self.zone_vars[z["clave"]]
            try:
                L = float(lim.get().replace(",", "."))
            except ValueError:
                L = z["limite_msv"]
            r, est = ZE.radio_registros(self.data["envolventes"].get(z["clave"], []), L)
            rl.config(text=("—" if r is None and est == "sin_datos" else
                            f"> máx." if r is None else f"{ESTADOS.get(est, '')}{r:.0f} m"),
                      fg=RED if est == "mayor_que_maximo" else TEXT)
            out.append((dict(z, limite_msv=L), r, est, show.get()))
        return out

    def _atraque_defecto(self):
        self.v["lat"].set(f"{ZE.DEFAULT_LAT:.5f}"); self.v["lon"].set(f"{ZE.DEFAULT_LON:.5f}")
        self.v["rumbo"].set(f"{ZE.DEFAULT_HEADING:g}")
        self.dibujar()

    # ------------------------------------------------------------------ drawing
    # Web Mercator: world pixel coordinates at zoom z (256-px tiles), as Leaflet / OpenStreetMap
    @staticmethod
    def _merc(lat, lon, z):
        n = 256 * 2 ** z
        lat = max(-85.0, min(85.0, lat))
        x = (lon + 180.0) / 360.0 * n
        y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
        return x, y

    @staticmethod
    def _inv(x, y, z):
        n = 256 * 2 ** z
        lon = x / n * 360.0 - 180.0
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
        return lat, lon

    def _screen(self, lat, lon):
        x, y = self._merc(lat, lon, self.z)
        cx, cy = self._merc(self.centro[0], self.centro[1], self.z)
        return x - cx + self.cv.winfo_width() / 2, y - cy + self.cv.winfo_height() / 2

    def _latlon(self, sx, sy):
        cx, cy = self._merc(self.centro[0], self.centro[1], self.z)
        return self._inv(cx + sx - self.cv.winfo_width() / 2, cy + sy - self.cv.winfo_height() / 2, self.z)

    def _rango(self, zs, b):
        return max([b["eslora"]] + [r for _, r, _, s in zs if r and s]) * 1.1

    def _ajustar(self):
        """Centre on the reactor with the ship and the visible zones in view."""
        b = self.buque()
        W, H = max(self.cv.winfo_width(), 200), max(self.cv.winfo_height(), 200)
        R = self._rango(self.zonas(), b)
        rl, ro = ZE.posicion_reactor(b["lat"], b["lon"], b["rumbo"], b["eslora"], b["popa"])
        mpp = 2 * R / (min(W, H) - 40)                         # metres per pixel needed
        z = math.log2(156543.03392 * math.cos(math.radians(rl)) / mpp)
        self.z = int(max(3, min(ZMAX, math.floor(z))))
        self.centro = [rl, ro]
        self.dibujar()

    def _zoom_at(self, ev, dz):
        z = max(3, min(ZMAX, self.z + dz))
        if z == self.z:
            return
        lat, lon = self._latlon(ev.x, ev.y)                    # keep the point under the cursor
        self.z = z
        sx, sy = self._screen(lat, lon)
        clat, clon = self._latlon(self.cv.winfo_width() / 2 + sx - ev.x, self.cv.winfo_height() / 2 + sy - ev.y)
        self.centro = [clat, clon]
        self.dibujar()

    def _drag_start(self, ev):
        self._drag = (ev.x, ev.y)

    def _drag_move(self, ev):
        if self._drag:
            W, H = self.cv.winfo_width(), self.cv.winfo_height()
            self.centro = list(self._latlon(W / 2 - (ev.x - self._drag[0]), H / 2 - (ev.y - self._drag[1])))
            self._drag = (ev.x, ev.y)
            self.dibujar()

    def _situar_buque(self, ev):
        lat, lon = self._latlon(ev.x, ev.y)
        self.v["lat"].set(f"{lat:.5f}"); self.v["lon"].set(f"{lon:.5f}")
        self.msg.config(text=f"Centro del buque situado en {lat:.5f}, {lon:.5f}. Ajusta el rumbo y pulsa "
                             "«Guardar buque y criterios».")
        self.dibujar()

    @staticmethod
    def _gms(v, pos, neg):
        h = pos if v >= 0 else neg
        v = abs(v); g = int(v); m = (v - g) * 60
        return f"{g}°{int(m):02d}′{(m - int(m)) * 60:04.1f}″ {h}"

    def _mostrar_cursor(self, ev):
        lat, lon = self._latlon(ev.x, ev.y)
        b = self.buque()
        rl, ro = ZE.posicion_reactor(b["lat"], b["lon"], b["rumbo"], b["eslora"], b["popa"])
        d = math.hypot((lat - rl) * 111320, (lon - ro) * 111320 * math.cos(math.radians(rl)))
        dist = f"{d:,.0f}".replace(",", ".")
        self.cursor.config(text=f"{lat:.5f}, {lon:.5f}   ({self._gms(lat, 'N', 'S')}  {self._gms(lon, 'E', 'O')})"
                                f"   a {dist} m del reactor")

    def _redibujar_pronto(self):
        if not getattr(self, "_pend", False):
            self._pend = True
            self.after(60, lambda: (setattr(self, "_pend", False), self.dibujar()))

    def _cuadricula(self, W, H):
        """Latitude / longitude lines with labels at the edges (decimal degrees)."""
        lat0, lon0 = self._latlon(0, H)
        lat1, lon1 = self._latlon(W, 0)
        span = max(lon1 - lon0, 1e-9)
        raw = span / 5
        p10 = 10 ** math.floor(math.log10(raw))
        step = next(m * p10 for m in (1, 2, 2.5, 5, 10) if m * p10 >= raw)
        dec = max(0, -int(math.floor(math.log10(step))) + (1 if step / p10 == 2.5 else 0))
        col = "#5f6b7a"
        v = math.ceil(lon0 / step) * step
        while v <= lon1:
            x, _ = self._screen(lat0, v)
            self.cv.create_line(x, 0, x, H, fill=col, dash=(2, 4), tags="grid")
            t = self.cv.create_text(x + 3, H - 4, text=f"{v:.{dec}f}°", anchor="sw", font=("Segoe UI", 8),
                                    fill=TEXT, tags="grid")
            self._fondo(t)
            v += step
        v = math.ceil(lat0 / step) * step
        while v <= lat1:
            _, y = self._screen(v, lon0)
            self.cv.create_line(0, y, W, y, fill=col, dash=(2, 4), tags="grid")
            t = self.cv.create_text(W - 4, y - 2, text=f"{v:.{dec}f}°", anchor="se", font=("Segoe UI", 8),
                                    fill=TEXT, tags="grid")
            self._fondo(t)
            v += step

    def _fondo(self, item, pad=2):
        x1, y1, x2, y2 = self.cv.bbox(item)
        r = self.cv.create_rectangle(x1 - pad, y1 - pad, x2 + pad, y2 + pad, fill=BG_CARD, outline="")
        self.cv.tag_lower(r, item)

    def dibujar(self):
        cv = self.cv
        cv.delete("all")
        W, H = cv.winfo_width(), cv.winfo_height()
        if W < 20 or H < 20:
            return
        if not hasattr(self, "z"):
            self._ajustar()
            return
        b = self.buque()
        zs = self.zonas()
        a = math.radians(b["rumbo"])
        yr = ZE.reactor_y(b["eslora"], b["popa"])
        rl, ro = ZE.posicion_reactor(b["lat"], b["lon"], b["rumbo"], b["eslora"], b["popa"])
        mpp = 156543.03392 * math.cos(math.radians(rl)) / 2 ** self.z    # metres per pixel
        k = 1 / mpp

        # base map tiles
        capa = CAPAS.get(self.capa.get())
        self.attrib.config(text=capa["atrib"] if capa else "")
        faltan = 0
        if capa:
            cx, cy = self._merc(self.centro[0], self.centro[1], self.z)
            x0w, y0w = cx - W / 2, cy - H / 2
            n = 2 ** self.z
            for tx in range(int(x0w // 256), int((x0w + W) // 256) + 1):
                for ty in range(int(y0w // 256), int((y0w + H) // 256) + 1):
                    if not (0 <= ty < n):
                        continue
                    img = self.teselas.get(self.capa.get(), self.z, tx % n, ty)
                    if img is not None:
                        cv.create_image(tx * 256 - x0w, ty * 256 - y0w, image=img, anchor="nw")
                    else:
                        faltan += 1
            self._cuadricula(W, H)
        ox, oy = self._screen(rl, ro)

        def scr(x, y):          # ship axes (m, origin amidships) -> screen
            yy = y - yr
            e, nn = x * math.cos(a) + yy * math.sin(a), -x * math.sin(a) + yy * math.cos(a)
            return ox + e * k, oy - nn * k

        # hull under the zones
        if b["eslora"] * k >= 6:
            pts = [c for p in ZE.casco(b["eslora"], b["manga"]) for c in scr(*p)]
            cv.create_polygon(pts, fill=HULL, outline=WHITE, width=1)
            mid = scr(0, 0)
            cv.create_oval(mid[0] - 3, mid[1] - 3, mid[0] + 3, mid[1] + 3, fill=WHITE, outline=HULL)
        # zones, largest first (semi-transparent look with a stipple, as Tk has no alpha)
        vis = sorted([t for t in zs if t[3] and t[1]], key=lambda t: -t[1])
        for z, r, est, _ in vis:
            c = z.get("color", BLUE)
            cv.create_oval(ox - r * k, oy - r * k, ox + r * k, oy + r * k, outline=c, width=2.5,
                           fill=c, stipple="gray12")
        cv.create_oval(ox - 5, oy - 5, ox + 5, oy + 5, fill=REACTOR, outline="#000", width=1.5)
        # legend
        y = 12
        for z, r, est, _ in sorted([t for t in zs if t[3]], key=lambda t: -(t[1] or 1e9)):
            c = z.get("color", BLUE)
            txt = (f"{z['clave']}: > distancia máxima" if r is None else
                   f"{z['clave']}: {ESTADOS.get(est, '')}{r:.0f} m  ({z['limite_msv']:g} mSv, {z.get('periodo', '')})")
            cv.create_rectangle(10, y, 26, y + 10, outline=c, width=2, tags="ley")
            cv.create_text(32, y + 5, text=txt, anchor="w", font=FONT_SM, fill=TEXT, tags="ley")
            y += 18
        cv.create_oval(12, y + 1, 22, y + 11, fill=REACTOR, outline="#000", tags="ley")
        cv.create_text(32, y + 6, text=f"Reactor ({b['popa']:g} m de la popa): {rl:.5f}, {ro:.5f}",
                       anchor="w", font=FONT_SM, fill=TEXT, tags="ley")
        y += 18
        cv.create_rectangle(10, y + 1, 26, y + 9, fill=HULL, outline=HULL, tags="ley")
        cv.create_text(32, y + 5, text=f"Buque {b['eslora']:g} × {b['manga']:g} m, rumbo {b['rumbo']:g}°: "
                                       f"{b['lat']:.5f}, {b['lon']:.5f}",
                       anchor="w", font=FONT_SM, fill=TEXT, tags="ley")
        x1, y1, x2, y2 = cv.bbox("ley")
        bg = cv.create_rectangle(x1 - 6, y1 - 5, x2 + 8, y2 + 5, fill=BG_CARD, outline=BORDER)
        cv.tag_lower(bg, "ley")
        # scale bar (above the longitude labels)
        raw = (W / 4) / k
        p10 = 10 ** math.floor(math.log10(raw))
        step = next(m * p10 for m in (1, 2, 5, 10) if m * p10 >= raw)
        x0, y0 = 16, H - 36
        cv.create_rectangle(x0 - 6, y0 - 22, x0 + step * k + 8, y0 + 9, fill=BG_CARD, outline=BORDER)
        cv.create_line(x0, y0, x0 + step * k, y0, width=3, fill=TEXT)
        for x in (x0, x0 + step * k):
            cv.create_line(x, y0 - 5, x, y0 + 5, width=2, fill=TEXT)
        lbl = f"{step / 1000:g} km" if step >= 1000 else f"{step:g} m"
        cv.create_text(x0, y0 - 12, text=lbl, anchor="w", font=FONT_SM, fill=TEXT)
        # north arrow
        cv.create_oval(W - 52, 12, W - 8, 62, fill=BG_CARD, outline=BORDER)
        cv.create_polygon(W - 30, 18, W - 22, 44, W - 30, 37, W - 38, 44, fill=TEXT)
        cv.create_text(W - 30, 53, text="N", font=FONT_BOLD, fill=TEXT)
        aviso = []
        if not self.data:
            aviso.append("Sin resultados cargados: se muestra solo el buque")
        if capa and faltan and self.teselas.sin_conexion:
            aviso.append("Sin conexión con el servidor de mapas: se muestran solo las zonas a escala")
        elif capa and capa.get("jpg") and not Teselas.PIL:
            aviso.append("Para esta capa hace falta Pillow (pip install pillow)")
        if aviso:
            t = cv.create_text(W / 2, H - 70, text="\n".join(aviso), font=FONT_SM, fill=TEXT, justify="center")
            self._fondo(t, 6)

    # ------------------------------------------------------------------ outputs
    def _resultado(self):
        """json contents with the ship and the criteria of the tab (radii recomputed)."""
        b = self.buque()
        rl, ro = ZE.posicion_reactor(b["lat"], b["lon"], b["rumbo"], b["eslora"], b["popa"])
        res = dict(self.data, lat=b["lat"], lon=b["lon"], rumbo=b["rumbo"], eslora_m=b["eslora"],
                   manga_m=b["manga"], reactor_desde_popa_m=b["popa"], reactor_lat=rl, reactor_lon=ro)
        zonas, visibles = [], []
        for z, r, est, show in self.zonas():
            zonas.append(dict(z, radio_m=r, estado=est))
            if show:
                visibles.append(z["clave"])
        res["zonas"], res["_visibles"] = zonas, visibles
        return res

    def guardar(self, quiet=False):
        if not self.data:
            messagebox.showinfo("Mapa de zonas", "Carga primero unos resultados.")
            return None
        res = self._resultado()
        try:
            (self.folder / "zonas_emergencia.json").write_text(json.dumps(res, indent=2, ensure_ascii=False),
                                                                encoding="utf-8")
            ZE.escribir_mapa(res, self.folder / "mapa_zonas.html", self.folder.name)
            png = ZE.escribir_png({**res, "zonas": [z for z in res["zonas"] if z["clave"] in res["_visibles"]]},
                                  self.folder / "mapa_zonas.png")
        except OSError as e:
            messagebox.showerror("Mapa de zonas", f"No se pudo guardar en {self.folder}:\n{e}")
            return None
        self.data = res
        if not quiet:
            self.msg.config(text=f"Guardado en {self.folder}: zonas_emergencia.json, mapa_zonas.html"
                                 + (" y mapa_zonas.png" if png else " (PNG no: falta matplotlib)"))
        return res

    def abrir_navegador(self):
        if not self.guardar(quiet=True):
            return
        url = SERVIDOR.url(self.folder)
        webbrowser.open(url)
        self.msg.config(text=f"Mapa abierto en el navegador: {url}\nSe sirve mientras la interfaz esté abierta. "
                             "En el selector de capas elige «Satélite (Esri)» para encajar el buque en el atraque y "
                             "copia la posición con «Copiar posición del buque».")

    def exportar_png(self):
        if not self.data:
            messagebox.showinfo("Mapa de zonas", "Carga primero unos resultados.")
            return
        f = filedialog.asksaveasfilename(title="Exportar mapa", defaultextension=".png",
                                         initialdir=str(self.folder), initialfile="mapa_zonas.png",
                                         filetypes=[("PNG", "*.png")])
        if not f:
            return
        res = self._resultado()
        res["zonas"] = [z for z in res["zonas"] if z["clave"] in res["_visibles"]]
        out = ZE.escribir_png(res, Path(f))
        self.msg.config(text=f"PNG guardado: {f}" if out else "No se pudo: falta matplotlib (pip install matplotlib).")
