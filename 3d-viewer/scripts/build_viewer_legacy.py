#!/usr/bin/env python3
"""
build_viewer.py
---------------
Embed data/heightmap.json into template.html (replacing the __DATA__ placeholder)
and write a single self-contained index.html. No server or build tools needed.
"""
import json, os
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(here, "template.html")).read()
data = open(os.path.join(here, "data", "heightmap.json")).read()
html = tpl.replace("__DATA__", data)
open(os.path.join(here, "index.html"), "w").write(html)
print("wrote index.html  (%d bytes)" % len(html))
