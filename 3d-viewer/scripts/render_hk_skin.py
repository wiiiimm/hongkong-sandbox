import sys, json, numpy as np, zipfile
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
G="{http://www.opengis.net/gml}"; F="{http://www.safe.com/gml/fme}"
g=json.load(open("hk_georef.json")); GW,GH=g["W"],g["H"]; aE,bE,aN,bN=g["aE"],g["bE"],g["aN"],g["bN"]
E0=bE; E1=aE*(GW-1)+bE; N1=bN; N0=aN*(GH-1)+bN
TW=3400; TH=int(round(TW*(N1-N0)/(E1-E0)))
def X(e): return (e-E0)/(E1-E0)*TW
def Y(n): return (N1-n)/(N1-N0)*TH
def xy(seg): return [(X(e),Y(n)) for e,n in seg]
z=zipfile.ZipFile("iB50000GML.zip")
def layer(n): return [x for x in z.namelist() if x.endswith(n+".gml")][0]
def feats(name, fields):
    with z.open(layer(name)) as fh:
        for ev,el in ET.iterparse(fh,events=("end",)):
            if el.tag==G+"featureMember":
                ft=el[0]; attr={k:(ft.findtext(F+k) or "") for k in fields}
                pl=ft.find(".//"+G+"posList"); pts=[]
                if pl is not None and pl.text:
                    v=pl.text.split(); pts=[(float(v[i]),float(v[i+1])) for i in range(0,len(v)-1,2)]
                yield attr,pts; el.clear()
stage=sys.argv[1]
if stage=="init":
    dtm=np.load("hk5m_grid.npy"); land=dtm>1.0
    ys=(np.arange(TH)/TH*GH).astype(int).clip(0,GH-1); xs=(np.arange(TW)/TW*GW).astype(int).clip(0,GW-1)
    landT=land[ys][:,xs]
    img=np.zeros((TH,TW,4),np.uint8); img[landT]=(244,239,226,255)
    Image.fromarray(img,"RGBA").save("hk_topo.png")
    # contours
    im=Image.open("hk_topo.png"); d=ImageDraw.Draw(im,"RGBA"); n=0
    for a,pts in feats("ELEVLINE",["HEIGHT"]):
        if len(pts)<2: continue
        h=float(a["HEIGHT"] or 0); idx=(h%100==0)
        d.line(xy(pts),fill=(150,108,66,255) if idx else (185,150,108,190),width=2 if idx else 1,joint="curve"); n+=1
    im.save("hk_topo.png"); print("contours drawn",n,"tex",im.size)
elif stage=="hydro":
    im=Image.open("hk_topo.png"); d=ImageDraw.Draw(im,"RGBA"); nc=ns=0
    for a,pts in feats("HYDRLINE",["TYPE"]):
        if len(pts)<2: continue
        if a["TYPE"]=="COA": d.line(xy(pts),fill=(40,80,120,255),width=2); nc+=1
        else: d.line(xy(pts),fill=(80,130,185,150),width=1); ns+=1
    im.save("hk_topo.png"); print("coast",nc,"stream",ns)
elif stage=="transport":
    im=Image.open("hk_topo.png"); d=ImageDraw.Draw(im,"RGBA"); nr=nt=0
    for a,pts in feats("TSPTLINE",["CLASS","TYPE"]):
        if len(pts)<2: continue
        p=xy(pts)
        if a["CLASS"]=="LTF" or a["TYPE"].startswith("F"):
            d.line(p,fill=(190,80,64,220),width=1); nt+=1
        else:
            d.line(p,fill=(255,255,255,210),width=2); d.line(p,fill=(120,120,124,255),width=1); nr+=1
    im.save("hk_topo.png"); print("roads",nr,"trails",nt)

elif stage=="labels":
    import pyproj
    im=Image.open("hk_topo.png"); d=ImageDraw.Draw(im,"RGBA")
    CJK="/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"; SER="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    fp_en=ImageFont.truetype(SER,22); fp_zh=ImageFont.truetype(CJK,21); fd=ImageFont.truetype(SER,17); fdz=ImageFont.truetype(CJK,16)
    t2=pyproj.Transformer.from_crs(4326,2326,always_xy=True)
    def txt(lo,la,en,zh,fe,fz,fill,mark=False):
        e,n=t2.transform(lo,la); x,y=X(e),Y(n)
        if mark: d.polygon([(x,y-7),(x-6,y+5),(x+6,y+5)],fill=(90,60,30,255))
        b=d.textbbox((0,0),en,font=fe); d.text((x-(b[2]-b[0])/2,y+(8 if mark else -8)),en,font=fe,fill=fill,stroke_width=3,stroke_fill=(255,255,255,235))
        if zh:
            b=d.textbbox((0,0),zh,font=fz); d.text((x-(b[2]-b[0])/2,y+(8 if mark else -8)+ (b[3]-b[1])+22),zh,font=fz,fill=fill,stroke_width=3,stroke_fill=(255,255,255,235))
    PEAKS=[("Tai Mo Shan","大帽山",114.1242,22.4108),("Lantau Peak","鳳凰山",113.9201,22.2492),
           ("Sunset Peak","大東山",113.9529,22.2572),("Ma On Shan","馬鞍山",114.2486,22.4017),
           ("Pat Sin Leng","八仙嶺",114.2200,22.4767),("Kowloon Peak","飛鵝山",114.2206,22.3367),
           ("Castle Peak","青山",113.9572,22.3869),("Victoria Peak","太平山",114.1455,22.2759),
           ("Sharp Peak","蚺蛇尖",114.3667,22.4358)]
    for en,zh,lo,la in PEAKS: txt(lo,la,en,zh,fp_en,fp_zh,(60,40,20,255),mark=True)
    DIST=[("Central","中環",114.158,22.281),("Tsuen Wan","荃灣",114.115,22.371),("Sha Tin","沙田",114.188,22.383),
          ("Tuen Mun","屯門",113.977,22.391),("Sai Kung","西貢",114.274,22.381),("Tai Po","大埔",114.171,22.450),
          ("Yuen Long","元朗",114.022,22.444),("Tung Chung","東涌",113.943,22.289),("Tsim Sha Tsui","尖沙咀",114.172,22.297)]
    for en,zh,lo,la in DIST: txt(lo,la,en,zh,fd,fdz,(70,60,52,255))
    im.save("hk_topo.png"); print("labels drawn")

print("stage",stage,"done")
