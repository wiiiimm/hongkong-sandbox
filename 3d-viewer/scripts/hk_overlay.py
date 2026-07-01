import json, zipfile
import xml.etree.ElementTree as ET
G="{http://www.opengis.net/gml}"; F="{http://www.safe.com/gml/fme}"
g=json.load(open("hk_georef.json")); GW,GH=g["W"],g["H"]; aE,bE,aN,bN=g["aE"],g["bE"],g["aN"],g["bN"]
E0=bE;E1=aE*(GW-1)+bE;N1=bN;N0=aN*(GH-1)+bN
def uv(seg,step):
    o=[[round((e-E0)/(E1-E0),4),round((N1-n)/(N1-N0),4)] for i,(e,n) in enumerate(seg) if i%step==0]
    return o
z=zipfile.ZipFile("iB50000GML.zip")
def L(n): return [x for x in z.namelist() if x.endswith(n+".gml")][0]
def feats(name,fields):
    with z.open(L(name)) as fh:
        for ev,el in ET.iterparse(fh,events=("end",)):
            if el.tag==G+"featureMember":
                ft=el[0]; a={k:(ft.findtext(F+k) or "") for k in fields}
                pl=ft.find(".//"+G+"posList"); pts=[]
                if pl is not None and pl.text:
                    v=pl.text.split(); pts=[(float(v[i]),float(v[i+1])) for i in range(0,len(v)-1,2)]
                yield a,pts; el.clear()
contour=[uv(p,3) for a,p in feats("ELEVLINE",["HEIGHT"]) if len(p)>1 and float(a["HEIGHT"] or 0)%200==0]
coast=[uv(p,2) for a,p in feats("HYDRLINE",["TYPE"]) if len(p)>1 and a["TYPE"]=="COA"]
json.dump({"contour":contour,"coast":coast,"trail":[]},open("hk_overlay.json","w"),separators=(",",":"))
import os; print("contours200",len(contour),"coast",len(coast),"%.0f KB"%(os.path.getsize("hk_overlay.json")/1024))
