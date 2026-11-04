"""Scientific source/GIS vector overlay on untouched, pinned government imagery."""
import math,numpy as np,matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pyproj import Transformer
from run import ROOT,read,save,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-source-authored-openings-20261009';OLD=ROOT/'docs/astra-city/government-import/government-xl-spatial-surface-roles-20261009';tx,ty=856859,457554;n=2**20;transform=Transformer.from_crs(2326,4326,always_xy=True)
r=read(DOC/'157125-0/opening-diagnostics.json.gz');fig,ax=plt.subplots(figsize=(9,9));refs=[]
for dx,dy in [(0,0),(-1,0),(0,-1)]:
 p=OLD/'157125-0'/f'raw-official-imagery-20-{tx+dx}-{ty+dy}.png';ax.imshow(plt.imread(p),extent=[dx*256,(dx+1)*256,(dy+1)*256,dy*256]);refs.append({'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes()),'request':read(p.with_suffix('.request.json'))})
def pix(ring):
 a=np.array(ring);lon,lat=transform.transform(a[:,0]+834500,816500-a[:,1]);return ((lon+180)/360*n-tx)*256,((1-np.arcsinh(np.tan(np.radians(lat)))/math.pi)/2*n-ty)*256
for b in r['groupForms']:
 for ring in b['rings']:x,y=pix(ring);ax.plot(x,y,color='cyan',linewidth=1,label='GIS exterior/interior boundary')
for h in r['sourceAuthoredOpeningDiagnostics']:
 for ring in h['geometry']['coordinates']:x,y=pix(ring);ax.plot(x,y,color='red',linewidth=1.5,label='Original source projection hole')
ax.set_xlim(-100,150);ax.set_ylim(200,-80);ax.set_aspect('equal');ax.set_title('157125 · untouched official aerial + exact source/GIS vectors\nFixed HK1980 transform; no fitted alignment or source edits');ax.set_xlabel('Tile pixel x');ax.set_ylabel('Tile pixel y');fig.tight_layout();fig.savefig(DOC/'157125-0/official-aerial-source-hole-overlay.png',dpi=200);save(DOC/'157125-0/official-aerial-source-hole-overlay-provenance.json',{'imagery':refs,'sourceDiagnosticSHA256':digest((DOC/'157125-0/opening-diagnostics.json.gz').read_bytes()),'qualification':'Scientific vector overlay: original imagery pixels, fixed projection, no edited source or fitted map alignment. Aerial dating/resolution not sufficient alone for complete-source acceptance.'})
