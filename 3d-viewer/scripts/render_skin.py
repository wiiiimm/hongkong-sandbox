import json, numpy as np
from PIL import Image, ImageDraw, ImageFont
gr=json.load(open("lantau_georef.json")); E0,E1,N0,N1=gr["bbox"]
hm=json.load(open("/sessions/gallant-sweet-fermat/mnt/map-of-lantau/claude/3d-viewer/data/lantau-hk5m.json"))
W,H=hm["w"],hm["h"]; elev=np.array(hm["elev"],dtype=np.float32).reshape(H,W)
spanE=E1-E0; spanN=N1-N0
TW=2600; TH=int(round(TW*spanN/spanE))
def X(e): return (e-E0)/spanE*TW
def Y(n): return (N1-n)/spanN*TH
def xy(seg): return [(X(e),Y(n)) for e,n in seg]
# land fill from heightmap (nearest upsample)
land=(elev>0.5)
ys=(np.arange(TH)/TH*H).astype(int).clip(0,H-1); xs=(np.arange(TW)/TW*W).astype(int).clip(0,W-1)
landT=land[ys][:,xs]
img=np.zeros((TH,TW,4),np.uint8)
img[landT]=(244,239,226,255)        # cream land
im=Image.fromarray(img,"RGBA"); d=ImageDraw.Draw(im,"RGBA")
S=TW/2600.0
contours=json.load(open("b50_contours.json"))
hydro=json.load(open("b50_hydro.json"))
trans=json.load(open("b50_transport.json"))
names=json.load(open("b50_names.json"))
# contours (brown); index every 100m darker/thicker
for c in sorted(contours,key=lambda c:c["h"]):
    idx = (c["h"]%100==0)
    col=(150,108,66,255) if idx else (181,146,102,210)
    d.line(xy(c["p"]),fill=col,width=int((1.7 if idx else 1.0)*S),joint="curve")
# streams (blue) + coastline (teal/dark)
for s in hydro["stream"]:
    d.line(xy(s),fill=(70,120,180,200),width=int(1.0*S),joint="curve")
for s in hydro["coast"]:
    d.line(xy(s),fill=(40,80,120,255),width=int(2.0*S),joint="curve")
# roads (white casing + grey) and trails (red dashed)
for r in trans["road"]:
    p=xy(r); d.line(p,fill=(255,255,255,235),width=int(2.6*S)); d.line(p,fill=(120,120,124,255),width=int(1.2*S))
def dashed(p,fill,w,dash=7,gap=5):
    for i in range(len(p)-1):
        (x0,y0),(x1,y1)=p[i],p[i+1]; L=np.hypot(x1-x0,y1-y0)
        if L<1: continue
        n=int(L/(dash+gap))+1; ux,uy=(x1-x0)/L,(y1-y0)/L; t=0
        while t<L:
            a=min(t+dash,L); d.line([(x0+ux*t,y0+uy*t),(x0+ux*a,y0+uy*a)],fill=fill,width=w); t+=dash+gap
for r in trans["trail"]:
    dashed(xy(r),(190,70,60,255),max(1,int(1.4*S)))
# labels
CJK="/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"; SER="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
def font(f,s): return ImageFont.truetype(f,int(s*S))
hill_en=font(SER,15); hill_zh=font(CJK,15); vil=font(SER,9); bay=font(SER,10)
def text(e,n,s,fnt,fill,dy=0):
    x,y=X(e),Y(n); b=d.textbbox((0,0),s,font=fnt); w=b[2]-b[0]
    d.text((x-w/2,y+dy-(b[3]-b[1])/2),s,font=fnt,fill=fill,stroke_width=max(1,int(2*S)),stroke_fill=(255,255,255,230))
for nm in names:
    t=nm["typ"]; e,n=nm["E"],nm["N"]
    if t=="HIL":
        text(e,n,nm["en"],hill_en,(60,40,20,255),dy=-9*S)
        if nm["zh"]: text(e,n,nm["zh"],hill_zh,(60,40,20,255),dy=7*S)
    elif t in("VIL","EST"): text(e,n,nm["en"],vil,(70,60,50,255))
    elif t=="BAY": text(e,n,nm["en"],bay,(50,80,120,255))
# clip everything to the Lantau landmass (dilated) so neighbouring islands drop out
from scipy.ndimage import binary_dilation
landmask_big=binary_dilation(land, iterations=2)
ysb=(np.arange(TH)/TH*H).astype(int).clip(0,H-1); xsb=(np.arange(TW)/TW*W).astype(int).clip(0,W-1)
keep=landmask_big[ysb][:,xsb]
arr=np.array(im); arr[~keep,3]=0
im=Image.fromarray(arr,"RGBA")
im.save("lantau_topo_texture.png")
print("texture",im.size)
# preview composited on dark bg for visibility
bg=Image.new("RGBA",im.size,(20,24,30,255)); bg.alpha_composite(im); bg.convert("RGB").resize((1500,int(1500*TH/TW))).save("skin_preview.png")
