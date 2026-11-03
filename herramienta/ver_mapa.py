#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ver_mapa.py — open the emergency zone map with the OpenStreetMap background

tile.openstreetmap.org only serves map tiles to pages that send a Referer header, which a
browser does not do for a file opened from disk (file://): the tiles come back as 403
"Access blocked". This script serves the results folder on http://localhost and opens the
map in the browser, so OpenStreetMap works. Close the window (or Ctrl+C) to stop it.

Usage: python ver_mapa.py [folder with mapa_zonas.html]   (default: psf_batch/postprocess)
"""
import functools, http.server, socketserver, sys, threading, webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "psf_batch" / "postprocess"
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
