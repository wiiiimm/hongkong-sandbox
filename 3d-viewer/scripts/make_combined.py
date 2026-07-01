import json, base64, os
L="/sessions/gallant-sweet-fermat/mnt/map-of-lantau/claude/3d-viewer/data"; HK="/sessions/gallant-sweet-fermat/mnt/map-of-lantau/claude/hk-3d-viewer/data"
def jl(p): return json.load(open(p))
lan5=jl(L+"/lantau-hk5m.json"); lan30=jl(L+"/lantau-srtm30.json")
lanGR=jl(L+"/lantau-georefs.json"); lanOv=jl(L+"/lantau-b50k-overlay.json")
hk5=jl(HK+"/hk-dtm5m.json"); hk30=jl(HK+"/hk-srtm.json")
hkGR=jl(HK+"/hk-georef.json"); hkOv=jl(HK+"/hk-b50k-overlay.json")
def bbox(g): 
    return {"E0":g["bE"],"E1":g["aE"]*(g["W"]-1)+g["bE"],"N1":g["bN"],"N0":g["aN"]*(g["H"]-1)+g["bN"]}
SKINS={"lantau":{"texbb":bbox(lanGR["hk5m"]),"overlay":lanOv},
       "hk":{"texbb":bbox(hkGR),"overlay":hkOv}}
DATASETS={
 "lan5":{"label":"Lantau — 5 m LiDAR","note":"island · 36 m mesh · Lantau Peak 934 m","data":lan5,"georef":lanGR["hk5m"],"skin":"lantau","ve":2.6},
 "lan30":{"label":"Lantau — SRTM ~30 m","note":"island · ~62 m mesh · global composite","data":lan30,"georef":lanGR["srtm30"],"skin":"lantau","ve":2.6},
 "hk5":{"label":"Hong Kong — 5 m LiDAR","note":"whole territory · 70 m mesh · Tai Mo Shan 952 m","data":hk5,"georef":hkGR,"skin":"hk","ve":4.5},
 "hk30":{"label":"Hong Kong — SRTM ~30 m","note":"whole territory · resampled to same grid","data":hk30,"georef":hkGR,"skin":"hk","ve":4.5},
}
texL="data:image/png;base64,"+base64.b64encode(open(L+"/lantau-b50k-topo-texture.png","rb").read()).decode()
texH="data:image/png;base64,"+base64.b64encode(open(HK+"/hk-b50k-topo-texture.png","rb").read()).decode()
tpl=open("template_combined.html").read()
html=(tpl.replace("__SKINS__",json.dumps(SKINS,separators=(",",":")))
        .replace("__DATASETS__",json.dumps(DATASETS,separators=(",",":")))
        .replace("__TEX_LANTAU__",texL).replace("__TEX_HK__",texH))
open("index.html","w").write(html)
print("combined viewer %.1f MB | views:"%(len(html)/1e6), list(DATASETS.keys()))
