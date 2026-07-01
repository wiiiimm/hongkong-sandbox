import numpy as np, geom, cairosvg
from scipy.ndimage import gaussian_filter1d
seg,(x0,x1,lonL,lonR,W)=geom.load_profile()
xn,h=geom.resample(seg,2400)
h=gaussian_filter1d(h,2.0); h[0]=0; h[-1]=0; h=np.clip(h,0,None)
PEAK=560.0; scale=PEAK/h.max()
Wv=2000.0; PAD=46.0; TOP=46.0; baseY=PEAK+TOP; Hv=baseY
X=PAD+xn*(Wv-2*PAD); Y=baseY-h*scale
dl="M "+" L ".join("%.2f %.2f"%(p,q) for p,q in zip(X,Y))
svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {Wv:.0f} {Hv:.0f}" width="{Wv:.0f}" height="{Hv:.0f}"><rect width="{Wv:.0f}" height="{Hv:.0f}" fill="#fff"/><path d="{dl}" fill="none" stroke="#000" stroke-width="1.4"/><path d="M {X[0]:.2f} {baseY:.2f} L {X[-1]:.2f} {baseY:.2f}" stroke="#000" stroke-width="1"/></svg>'
open("skyline_raw.svg","w").write(svg)
cairosvg.svg2png(bytestring=svg.encode(),write_to="skyline_raw.png",output_width=4000,background_color="#fff")
print("raw skyline svg ok")
