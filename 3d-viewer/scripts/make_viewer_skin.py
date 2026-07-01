import json, base64, os
base="/sessions/gallant-sweet-fermat/mnt/map-of-lantau/claude/3d-viewer/data/"
hk5m=json.load(open(base+"lantau-hk5m.json")); srtm=json.load(open(base+"lantau-srtm30.json"))
gr=json.load(open("georefs.json")); bb=json.load(open("lantau_georef.json"))["bbox"]
ov=json.load(open("lantau_overlay.json"))
tex="data:image/png;base64,"+base64.b64encode(open("lantau_topo_texture.png","rb").read()).decode()
DATASETS={
 "hk5m":{"label":"HK 5 m LiDAR — Lands Dept","note":"5 m grid · ±5 m · 2020 LiDAR (EPSG:2326)","data":hk5m,"georef":gr["hk5m"]},
 "srtm30":{"label":"SRTM ~30 m — AWS Terrarium","note":"~30 m global composite · Mapzen/Tilezen","data":srtm,"georef":gr["srtm30"]},
}
TEXBB={"E0":bb[0],"E1":bb[1],"N0":bb[2],"N1":bb[3]}
tpl=open("/tmp/b50k/template_skin.html").read()
html=(tpl.replace("__DATASETS__",json.dumps(DATASETS))
         .replace("__TEXBB__",json.dumps(TEXBB))
         .replace("__OVERLAY__",json.dumps(ov,separators=(",",":")))
         .replace("__TEX__",tex))
open("/tmp/b50k/index_skin.html","w").write(html)
print("viewer bytes %.1f MB"%(len(html)/1e6))
