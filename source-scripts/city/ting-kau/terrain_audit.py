"""Verify the inherited Ting Kau ridge against original 5m DTM block samples."""
import hashlib,json,pathlib,sys,zipfile,numpy as np
from shapely.geometry import Polygon,Point
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/ting-kau'
sys.path.insert(0,str(HERE.parent/'tai-o-completion'));from hydro_terrain import height
SOURCE=ROOT/'references/codex/hongkong-3d-model/data/hk-landsd-5m/Whole_HK_DTM_5m.zip'
def audit():
 coarse=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());original=json.loads((ROOT/'3d-viewer/data/hk-dtm5m.json').read_text());fine=json.loads((HERE/'terrain-ting-kau.json').read_text());hydro=json.loads((HERE/'hydro-ting-kau.json').read_text());water=[Polygon(w['rings'][0],w['rings'][1:]) for w in hydro['water']];g=coarse['meta']['georef'];rows=[]
 for x,z in [(-8427.765,-8887.478),(-8340,-8710),(-8290,-8610),(-8229.83,-8485.528),(-8180,-8380),(-8140,-8300),(-8019.633,-8059.256)]:
  i=round((x+834500-g['bE'])/70);j=round((816500-z-g['bN'])/-70);rows.append({'world':[x,z],'coarseColumn':i,'coarseRow':j,'coarseOriginalRaw':original['elev'][j*coarse['w']+i],'coarseCityRaw':coarse['elev'][j*coarse['w']+i],'coarseRenderedAtPoint':height(coarse,x,z),'sourceFineRenderedBeforeWaterCut':height(fine,x,z),'mappedWater':any(w.covers(Point(x,z)) for w in water)})
 with zipfile.ZipFile(SOURCE) as archive,archive.open('Whole_HK_DTM_5m.asc') as f:
  header={}
  for _ in range(6):k,v=f.readline().decode().split();header[k]=float(v)
  need={r for p in rows for r in range(p['coarseRow']*14,(p['coarseRow']+1)*14)};data={}
  for r,line in enumerate(f):
   if r in need:data[r]=np.fromstring(line.decode(),sep=' ',dtype=np.float32)
   if r>max(need):break
  for p in rows:
   i,j=p['coarseColumn'],p['coarseRow'];a=np.stack([data[r][i*14:(i+1)*14] for r in range(j*14,(j+1)*14)]);a=np.where(a<=-100,0,a);p.update(native14x14Mean=float(a.mean()),sourceRawRange=[float(a.min()),float(a.max())],nativePositiveSamples=int((a>1).sum()));assert round(float(a.mean()))==p['coarseOriginalRaw']==p['coarseCityRaw']
 report={'source':str(SOURCE.relative_to(ROOT)),'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'sourceHeader':header,'samples':rows,'cause':'Inherited 70m cells exactly reproduce 14x14 averages of the original 5m DTM, including elevated bridge samples. The original DTM>1m land heuristic turns these into a channel ridge. Source-mapped water, not a guessed bridge-width cut, determines removal.','sourceUnchanged':True,'note':'At-point triangle heights are distinguished from nearest coarse node values. Mapped tower foundation sites remain land.'};(DOC/'terrain-source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':audit()
