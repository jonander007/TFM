"""docx -> PDF with LibreOffice: tables of contents and lists updated to the real pages, bookmarks, metadata.
Usage: python3.12 export_pdf.py in.docx out.pdf [title] [author]"""
import sys, subprocess, time, os, uno
FIG7_OFFSET = 4400000
from com.sun.star.beans import PropertyValue
src, dst = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
# Layout adjustment only for this export (LibreOffice places the floating caption of Figura 7 lower than Word)
import zipfile, tempfile, re as _re0
_tmp = os.path.join(tempfile.mkdtemp(), "pdf_build.docx")
with zipfile.ZipFile(src) as zi, zipfile.ZipFile(_tmp, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in zi.infolist():
        data = zi.read(it.filename)
        if it.filename == "word/document.xml":
            x = data.decode("utf8")
            n0 = x.count("<wp:posOffset>4752340</wp:posOffset>")
            x = x.replace("<wp:posOffset>4752340</wp:posOffset>", "<wp:posOffset>%d</wp:posOffset>" % FIG7_OFFSET)
            print("Figura 7 caption moved:", n0)
            data = x.encode("utf8")
        zo.writestr(it, data)
src = _tmp
title = sys.argv[3] if len(sys.argv) > 3 else ""
author = sys.argv[4] if len(sys.argv) > 4 else ""
proc = subprocess.Popen(["soffice", "--headless", "--norestore", "--nologo",
                         "--accept=socket,host=127.0.0.1,port=2083;urp;", "-env:UserInstallation=file:///tmp/lo_tfm"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def pv(n, v):
    p = PropertyValue(); p.Name = n; p.Value = v; return p
try:
    ctx = None
    for _ in range(60):
        try:
            local = uno.getComponentContext()
            res = local.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", local)
            ctx = res.resolve("uno:socket,host=127.0.0.1,port=2083;urp;StarOffice.ComponentContext"); break
        except Exception:
            time.sleep(1)
    desk = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desk.loadComponentFromURL(uno.systemPathToFileUrl(src), "_blank", 0, (pv("Hidden", True),))
    idx = doc.getDocumentIndexes()
    import re
    todo = [idx.getByIndex(i) for i in range(idx.getCount())
            if "Bibliography" not in idx.getByIndex(i).getServiceName()]   # the reference list is Word's: keep it
    for rnd in range(2):                      # twice: the first update can move the pages
        for x in todo:
            x.update()
    # annex pages are numbered "Anexo A - 1": show them as A-1 in the indexes instead of a bare 1
    letter, where = None, {}
    en = doc.Text.createEnumeration()
    while en.hasMoreElements():
        par = en.nextElement()
        if not par.supportsService("com.sun.star.text.Paragraph"):
            continue
        s = par.getString().strip()
        m = re.match(r"Anexo ([A-Z]):", s)
        if m and par.ParaStyleName.startswith(("Heading", "T")):
            letter = m.group(1); where[s[:8]] = letter
        m = re.match(r"((?:Tabla|Figura) \d+):", s)
        if m and letter:
            where[m.group(1) + ":"] = letter
    fixed = 0
    for x in todo:
        x.IsProtected = False
        en = x.Anchor.createEnumeration()
        while en.hasMoreElements():
            par = en.nextElement()
            if not par.supportsService("com.sun.star.text.Paragraph"):
                continue
            s = par.getString()
            m = re.match(r"\s*(Anexo [A-Z]:|(?:Tabla|Figura) \d+:)", s)
            n = re.search(r"(\d+)\s*$", s)
            if m and n and m.group(1) in where:
                cur = par.getText().createTextCursorByRange(par.getEnd())
                cur.goLeft(len(s) - n.start(1), True)
                cur.setString("%s-%s" % (where[m.group(1)], n.group(1)))
                fixed += 1
        x.IsProtected = True
    print("annex page numbers rewritten:", fixed)
    print("indexes:", idx.getCount(), [idx.getByIndex(i).getServiceName().split(".")[-1] for i in range(idx.getCount())])
    props = doc.getDocumentProperties()
    if title: props.Title = title
    if author: props.Author = author
    props.Subject = "Trabajo Fin de Máster"
    fd = uno.Any("[]com.sun.star.beans.PropertyValue", (
        pv("ExportBookmarks", True), pv("UseTaggedPDF", True), pv("ExportNotes", False),
        pv("ExportBookmarksToPDFDestination", True), pv("OpenBookmarkLevels", 1), pv("InitialView", 1),
        pv("Quality", 92), pv("ReduceImageResolution", False), pv("SelectPdfVersion", 0)))
    doc.storeToURL(uno.systemPathToFileUrl(dst), (pv("FilterName", "writer_pdf_Export"), pv("FilterData", fd)))
    doc.close(True)
finally:
    try: desk.terminate()
    except Exception: pass
    time.sleep(1); proc.terminate()
