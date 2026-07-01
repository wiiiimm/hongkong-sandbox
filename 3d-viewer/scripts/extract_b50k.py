import zipfile, json, sys
import xml.etree.ElementTree as ET
G="{http://www.opengis.net/gml}"; F="{http://www.safe.com/gml/fme}"
gr=json.load(open("lantau_georef.json")); bb=gr["bbox"]; M=400
E0,E1,N0,N1=bb[0]-M,bb[1]+M,bb[2]-M,bb[3]+M
z=zipfile.ZipFile("iB50000GML.zip")
def layer(name): return [x for x in z.namelist() if x.endswith(name+".gml")][0]
def parse(name, fields):
    out=[]
    with z.open(layer(name)) as f:
        for ev,el in ET.iterparse(f,events=("end",)):
            if el.tag==G+"featureMember":
                feat=el[0]
                attr={k:(feat.findtext(F+k) or "") for k in fields}
                pts=[]
                pl=feat.find(".//"+G+"posList")
                if pl is not None and pl.text:
                    v=pl.text.split(); 
                    pts=[(float(v[i]),float(v[i+1])) for i in range(0,len(v)-1,2)]
                else:
                    pe=feat.find(".//"+G+"pos")
                    if pe is not None and pe.text:
                        v=pe.text.split(); pts=[(float(v[0]),float(v[1]))]
                if pts and any(E0<=x<=E1 and N0<=y<=N1 for x,y in pts):
                    out.append((attr,pts))
                el.clear()
    return out
which=sys.argv[1]
if which=="contours":
    c=parse("ELEVLINE",["HEIGHT","TYPE"])
    data=[{"h":float(a["HEIGHT"] or 0),"p":[[round(x,1),round(y,1)] for x,y in pts]} for a,pts in c]
    json.dump(data,open("b50_contours.json","w")); print("contours",len(data))
elif which=="hydro":
    c=parse("HYDRLINE",["TYPE","CLASS"])
    coast=[]; stream=[]
    for a,pts in c:
        seg=[[round(x,1),round(y,1)] for x,y in pts]
        (coast if a["TYPE"]=="COA" else stream).append(seg)
    json.dump({"coast":coast,"stream":stream},open("b50_hydro.json","w"))
    print("coast",len(coast),"stream",len(stream))
elif which=="transport":
    c=parse("TSPTLINE",["CLASS","TYPE"])
    trail=[]; road=[]
    for a,pts in c:
        seg=[[round(x,1),round(y,1)] for x,y in pts]
        # LTF=light traffic/footpath/trail; FP*/PI footpath
        if a["CLASS"]=="LTF" or a["TYPE"].startswith("F") or a["TYPE"] in("PI","FPI","TRK"):
            trail.append(seg)
        else: road.append(seg)
    json.dump({"trail":trail,"road":road},open("b50_transport.json","w"))
    print("trail",len(trail),"road",len(road))
