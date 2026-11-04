#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ver_mapa.py — open the emergency zone map with the OpenStreetMap background

tile.openstreetmap.org only serves map tiles to pages that send a Referer header, which a
browser does not do for a file opened from disk (file://): the tiles come back as 403
"Access blocked". This script serves the results folder on http://localhost and opens the
map in the browser, so OpenStreetMap works. Close the window (or Ctrl+C) to stop it.

Usage: python ver_mapa.py [folder with mapa_zonas.html]
       (default: the newest of RUN_N/OUTPUT and psf_batch/postprocess)
"""
import functools, http.server, socketserver, sys, threading, webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    if len(sys.argv) > 1:
        folder = Path(sys.argv[1])
    else:   # newest map: RUN_N/OUTPUT (graphical interface) or psf_batch/postprocess (console)
        maps = list(HERE.glob("RUN_*/OUTPUT/mapa_zonas.html")) + list(HERE.glob("psf_batch/postprocess/mapa_zonas.html"))
        folder = max(maps, key=lambda f: f.stat().st_mtime).parent if maps else HERE / "psf_batch" / "postprocess"
    page = folder / "mapa_zonas.html"
    if not page.exists():
        sys.exit(f"Not found: {page}. Run PIPELINE.py (or zonas_emergencia.py) first.")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(folder))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        url = f"http://localhost:{httpd.server_address[1]}/mapa_zonas.html"
        print(f"Map: {url}\nPress Ctrl+C to stop.")
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
