"""Diagnose coherent alternative diagonals of unchanged original DTM grid cells.

All original grid corners retain their elevations. A diagonal must satisfy every
source sample assigned to its cell; independent per-point choices are forbidden.
Positive diagnostics grant no source, whole-foundation or publication acceptance.
"""
import math,importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,read,save,digest
DIR=ROOT/'source-scripts/city/government-import';BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-original-dtm-diagonal-preview-20261007'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 doc=BASE/BATCH;assert not doc.exists();local=DIR/'local'/BATCH;refs=[];memo={}
 def pinned(p):
  if p not in memo:memo[p]=read(p);refs.append(ref(p))
  return memo[p]
 oldpath=BASE/'government-xl-original-dtm-contact-preview-20261007/result.json';old=pinned(oldpath)
 freshpath=BASE/'government-xl-refreshed-current-tin-preview-20261007-inputs/result.json';fresh=pinned(freshpath)
 pool={r['uid']:r for r in old['rows']};pool.update({r['uid']:r for r in fresh['rows']})
 allowed={r['uid'] for r in pinned(BASE/'government-xl-remaining-historical-current-tin-preview-20261007/result.json')['rows']}|{r['uid'] for r in fresh['rows']}
 manifest=pinned(ROOT/'3d-viewer/city/data/manifest.json');installed={m['uid'] for u in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models']}
 assert ref(ROOT/old['source']['path'])==old['source']
 spec=importlib.util.spec_from_file_location('diagonal_source_grid',DIR/'xl-original-dtm-contact-preview.py');dtm=importlib.util.module_from_spec(spec);spec.loader.exec_module(dtm)
 rows=[]
 for uid in sorted(allowed-installed):
  prior=pool[uid];path=ROOT/prior['geometry']['path'];data=pinned(path);assert ref(path)==prior['geometry']
  for p,sha in data['inputHashes'].items():
   if digest((ROOT/p).read_bytes())!=sha:assert p=='3d-viewer/city/data/manifest.json' or p.startswith(('3d-viewer/city/data/terrain','3d-viewer/city/data/government-native-'))
  model=next(r for r in data['rows'] if r['uid']==uid);source=next(r for r in pinned(BASE/prior['priorBatch']/'selection.json.gz')['rows'] if r['uid']==uid)
  assert source['sourceSHA256']==model['sourceSHA256']==prior['sourceSHA256']==digest((ROOT/source['candidate']['path']).read_bytes())
  pos=np.asarray(model['position']).reshape(-1,3);faces=pos[np.asarray(model['index']).reshape(-1,3)];bottom=float(pos[:,1].min());points=[pos,faces.mean(axis=1)];edges=[]
  for face in faces:
   for k in range(3):
    a,b=face[k],face[(k+1)%3]
    if max(a[1],b[1])>bottom+.35:continue
    n=math.ceil(np.linalg.norm((a-b)[[0,2]]));edges.extend(a+(b-a)*i/n for i in range(1,n))
  if edges:points.append(np.array(edges))
  points=np.concatenate(points);low=points[:,1]<=bottom+.35
  gridpath=ROOT/prior['grid']['path'];assert ref(gridpath)==prior['grid'];grid=pinned(gridpath);values=np.asarray(grid['heights']);coords=dtm.grid_coordinates(points);cell=np.floor(coords).astype(int);u,v=(coords-cell).T;c,r=(cell-np.array(grid['bounds'][:2])).T
  a,b,d,e=values[r,c],values[r,c+1],values[r+1,c],values[r+1,c+1]
  first=np.where(u+v<=1,a+(b-a)*u+(d-a)*v,e+(d-e)*(1-u)+(b-e)*(1-v))
  second=np.where(v<=u,a+(b-a)*u+(e-b)*v,a+(e-d)*u+(d-a)*v)
  gap=np.stack([points[:,1]-first,points[:,1]-second],axis=1);ok=(gap>=-.5)&(~low[:,None]|(gap<=1))
  keys=cell[:,0]*9601+cell[:,1];unique,inverse=np.unique(keys,return_inverse=True);percell=np.ones((len(unique),2),bool)
  np.logical_and.at(percell,inverse,ok);coherent=percell.any(axis=1);choice=np.where(percell[:,0],0,1)
  contact=low[:,None]&(gap<=.1)&ok;possible_contact=contact&percell[inverse]
  possible=bool(coherent.all() and possible_contact.any())
  if possible and not contact[np.arange(len(points)),choice[inverse]].any():
   sample,diagonal=np.argwhere(possible_contact)[0];choice[inverse[sample]]=diagonal
  if possible:
   measured=gap[np.arange(len(points)),choice[inverse]];assert (measured>=-.5).all() and (measured[low]<=1).all() and measured[low].min()<=.1
   save(doc/(uid.split('/')[1].replace(':','-')+'-cells.json.gz'),{'grid':prior['grid'],'geometry':prior['geometry'],'cells':[[int(key//9601),int(key%9601),int(diagonal)] for key,diagonal in zip(unique,choice)],'sourceSHA256':prior['sourceSHA256'],'diagnosticOnly':True})
  row={'uid':uid,'name':source['name'],'historicalPriorBatch':prior['priorBatch'],'sourceSHA256':prior['sourceSHA256'],'geometry':prior['geometry'],'grid':prior['grid'],'checks':len(points),'lowChecks':int(low.sum()),'uniformOtherDiagonalUnresolved':int((~ok[:,1]).sum()),'coherentCellDiagonalUnresolvedCells':int((~coherent).sum()),'coherentCellDiagonalPositive':possible,'changedCellDiagonals':int(choice.sum()) if possible else None}
  rows.append(row);print(json.dumps({k:row[k] for k in ['uid','coherentCellDiagonalPositive','coherentCellDiagonalUnresolvedCells','uniformOtherDiagonalUnresolved']}),flush=True)
 for e in refs:assert ref(ROOT/e['path'])==e
 refs.extend([ref(Path(__file__)),ref(DIR/'xl-original-dtm-contact-preview.py')]);save(doc/'result.json',{'rows':rows,'evidenceRefs':refs,'source':old['source'],'newlyInstalled':0,'publication':False,'diagnosticOnly':True,'modelGeometryChanges':0,'scriptExternalAICalls':0,'qualification':'Original 5 m elevation samples unchanged; coherent per-cell diagonal diagnostics only. All fresh identity, full terrain/foundation, neighbors and staged/live browser gates remain mandatory.'})
 print({'models':len(rows),'positive':[r['uid'] for r in rows if r['coherentCellDiagonalPositive']]},flush=True)
if __name__=='__main__':main()
