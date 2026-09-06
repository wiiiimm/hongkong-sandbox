"""Reuse the retained official 5 m DTM for a fine Mui Wo terrain patch.
No buildings are moved and no elevations are inferred from their roofs.
The patch boundary follows existing 70 m cells; a 70 m border joins the old mesh.
"""
import argparse,hashlib,json,math,pathlib,zipfile
import numpy as np
from pyproj import Transformer
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=ROOT/'3d-viewer/city/data'
DEFAULT=ROOT/'references/codex/hongkong-3d-model/data/hk-landsd-5m/Whole_HK_DTM_5m.zip'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=pathlib.Path,default=DEFAULT);args=ap.parse_args()
 coarse=json.loads((OUT/'terrain.json').read_text());g=coarse['meta']['georef'];cw=coarse['w']
 bbox=json.loads((OUT/'mui-wo-buildings.json').read_text())['bboxWGS84'];project=Transformer.from_crs(4326,2326,always_xy=True)
 corners=[project.transform(x,y) for x in bbox[::2] for y in bbox[1::2]]
 c0=math.floor((min(x for x,y in corners)-g['bE'])/70)-2;c1=math.ceil((max(x for x,y in corners)-g['bE'])/70)+2
 r0=math.floor((g['bN']-max(y for x,y in corners))/70)-2;r1=math.ceil((g['bN']-min(y for x,y in corners))/70)+2
 E=g['bE']+c0*70;N=g['bN']-r0*70;w=(c1-c0)*14+1;h=(r1-r0)*14+1
 with zipfile.ZipFile(args.source) as z:
  with z.open('Whole_HK_DTM_5m.asc') as f:
   header={};
   for _ in range(6):k,v=f.readline().decode().split();header[k.lower()]=float(v)
   sourceE=header['xllcorner']+2.5;sourceN=header['yllcorner']+(header['nrows']-.5)*5
   sc0=math.floor((E-sourceE)/5);sr0=math.floor((sourceN-N)/5)
   rows=[]
   for r,line in enumerate(f):
    if r<sr0:continue
    if r>sr0+h:break
    a=np.fromstring(line.decode(),sep=' ',dtype=np.float32);rows.append(a[sc0:sc0+w+1])
 sample=np.stack(rows);sample=np.where(sample==header['nodata_value'],0,sample)
 u=((E-sourceE)/5)%1;v=((sourceN-N)/5)%1
 fine=sample[:h,:w]*(1-u)*(1-v)+sample[:h,1:w+1]*u*(1-v)+sample[1:h+1,:w]*(1-u)*v+sample[1:h+1,1:w+1]*u*v
 original=fine.copy();vegetation=[]
 for r in range(h):
  for c in range(w):
   col=c0+c/14;row=r0+r/14;i=int(col);j=int(row);a,b,d,e=[coarse['elev'][q] for q in (j*cw+i,j*cw+i+1,(j+1)*cw+i,(j+1)*cw+i+1)];u=col-i;v=row-j
   old=a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
   # Transition only outside the validation envelope, using the same triangle interpolation.
   blend=min(1,min(c,r,w-1-c,h-1-r)/14)
   fine[r,c]=fine[r,c]*blend+old*(1-blend)
   vegetation.append(coarse['vegetation'][j*cw+i])
 source={'provider':'Lands Department / Hong Kong SAR Government','url':'https://www.landsd.gov.hk/landsd_psi_data/SMO/data/Whole_HK_DTM_5m.zip','file':'references/codex/hongkong-3d-model/data/hk-landsd-5m/Whole_HK_DTM_5m.zip','sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'nativeCellSize':5,'crs':'EPSG:2326','verticalDatum':'HKPD','note':'Archival official DTM; resampled onto a 5 m grid aligned with existing 70 m cell boundaries. Boundary has a 70 m transition outside the validation area. DTM and building revisions differ.'}
 detail_sources=[]
 detail_path=ROOT/'docs/astra-city/mui-wo-buildings/review/model-sample/terrain-source-5m.json'
 if detail_path.exists():
  detail=json.loads(detail_path.read_text());dg=detail['meta']['georef'];dc=round((dg['bE']-E)/5);dr=round((N-dg['bN'])/5)
  assert dg['aE']==5 and dg['aN']==-5 and abs(E+dc*5-dg['bE'])<.001 and abs(N-dr*5-dg['bN'])<.001
  for r in range(detail['h']):
   for c in range(detail['w']):
    value=detail['elev'][r*detail['w']+c]
    if value is None:continue
    blend=min(1,min(c,r,detail['w']-1-c,detail['h']-1-r)/3)
    fine[dr+r,dc+c]=fine[dr+r,dc+c]*(1-blend)+value*blend
  detail_sources.append({'file':str(detail_path.relative_to(ROOT)),'sha256':hashlib.sha256(detail_path.read_bytes()).hexdigest(),'source':detail['source'],'policy':'Actual official 3D tile terrain sampled onto the existing 5 m grid. A 15 m edge blend joins the archival DTM; source model heights stay unchanged.'})
 patch={'w':w,'h':h,'cell':5,'elev':np.round(fine.astype(np.float64),2).flatten().tolist(),'vegetation':vegetation,'coarseCells':[c0,r0,c1,r1],'meta':{'georef':{'aE':5,'bE':E,'aN':-5,'bN':N,'W':w,'H':h},'source':source,'title':'Mui Wo · Lands Department 5 m DTM','detailSources':detail_sources}}
 (OUT/'terrain-mui-wo.json').write_text(json.dumps(patch,separators=(',',':')))
 print(json.dumps({'w':w,'h':h,'bounds':[E,N-(h-1)*5,E+(w-1)*5,N],'coarseCells':patch['coarseCells'],'source':source}))
if __name__=='__main__':main()
