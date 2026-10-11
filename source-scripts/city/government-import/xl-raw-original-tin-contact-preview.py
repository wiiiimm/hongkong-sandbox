"""Bounded original TIN/DTM/root pointwise feasibility; never acceptance."""
import argparse,importlib.util,math,json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,read,save,digest
DIR=ROOT/'source-scripts/city/government-import'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,DIR/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 p=argparse.ArgumentParser();p.add_argument('--freeze',required=True);p.add_argument('--preview',required=True);p.add_argument('--batch',required=True);a=p.parse_args()
 assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
 doc=ROOT/'docs/astra-city/government-import'/a.batch;local=DIR/'local'/a.batch;assert not doc.exists()
 base=ROOT/a.freeze;priorpath=ROOT/a.preview/'result.json';prior=read(priorpath);geompath=ROOT/prior['geometry']['path'];geometry=read(geompath)
 assert digest(geompath.read_bytes())==prior['geometry']['sha256'] and prior['diagnosticOnly'] and not prior['publication']
 changed=[]
 for path,pinned in geometry['inputHashes'].items():
  actual=digest((ROOT/path).read_bytes())
  if actual!=pinned:
   assert path=='3d-viewer/city/data/manifest.json','Changed source, pose or geometry input: '+path
   changed.append({'path':path,'previousSHA256':pinned,'currentSHA256':actual})
 selection=read(base/'check-selection.json.gz');sources={r['uid']:r for r in selection['rows']};routes={r['uid']:r for r in read(base/'preflight.json')['rows']}
 assert set(sources)=={r['uid'] for r in geometry['rows']}=={r['uid'] for r in prior['rows']} and len(sources)<=100
 previews={r['uid']:r for r in prior['rows']}
 dtm=module('tin_dtm','xl-original-dtm-contact-preview.py');parent=module('tin_parent','xl-three-original-surfaces-preview.py');indexed=module('tin_cache','xl-indexed-terrain-continuation.py');decoder=module('tin_decode','xl-second-pass.py');decoder.LOCAL=local
 rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=read(rootpath);assert digest(rootpath.read_bytes())==prior['parent']['sha256']
 assert digest((ROOT/prior['source']['path']).read_bytes())==prior['source']['sha256']
 cache={};rows=[];refs={str(geompath.relative_to(ROOT)):digest(geompath.read_bytes()),str(priorpath.relative_to(ROOT)):digest(priorpath.read_bytes()),str(rootpath.relative_to(ROOT)):digest(rootpath.read_bytes())}
 for r in geometry['rows']:
  row=sources[r['uid']];assert row['sourceSHA256']==r['sourceSHA256']
  verts=np.asarray(r['position']).reshape(-1,3);faces=verts[np.asarray(r['index']).reshape(-1,3)];bottom=float(verts[:,1].min());points=[verts,faces.mean(axis=1)];edges=[]
  for face in faces:
   for k in range(3):
    x,y=face[k],face[(k+1)%3]
    if max(x[1],y[1])>bottom+.35:continue
    n=math.ceil(np.linalg.norm((x-y)[[0,2]]));edges.extend(x+(y-x)*j/n for j in range(1,n))
  if edges:points.append(np.array(edges))
  points=np.concatenate(points);low=points[:,1]<=bottom+.35;assert len(points)==previews[r['uid']]['points']
  gridref=previews[r['uid']]['grid'];grid=read(ROOT/gridref['path']);assert digest((ROOT/gridref['path']).read_bytes())==gridref['sha256'];refs[gridref['path']]=gridref['sha256']
  dg=points[:,1]-dtm.heights(points,np.array(grid['heights']),grid['bounds']);pg=points[:,1]-parent.parent_heights(points,root)
  valid=lambda gap:(gap>=-.5)&(~low|(gap<=1))
  possible=valid(dg)|valid(pg);contact=((valid(dg)&(dg<=.1))|(valid(pg)&(pg<=.1)))&low
  tinpass=np.zeros(len(points),bool);tincontact=np.zeros(len(points),bool);sheets=sorted({row['native']['sheet'],*[x['sheet'] for x in routes[r['uid']].get('indexedSheets',[])]});unavailable=[];records=[]
  for sheet in sheets:
   if sheet not in cache:
    audit=DIR/'local/government-xl-held-current-directory-audit-20261007/sheets'/sheet/'directory/result.json'
    if not audit.exists():cache[sheet]=None
    else:
     current=read(audit);matched=None
     for folder in sorted((DIR/'local').glob('*/sheets/'+sheet)):
      proof=indexed.verified_terrain(folder)
      if proof and proof[0]['directorySHA256']==current['directorySHA256']:matched=(folder,proof);break
     if matched is None:cache[sheet]=None
     else:
      folder,(receipt,files)=matched;pieces=[]
      for f in files:
       path=folder/'terrain'/f['name'];refs[str(path.relative_to(ROOT))]=f['sha256']
       if path.suffix=='.gltf':pieces.append(decoder.terrain_triangles(path))
      tri=np.concatenate(pieces);polys=shapely.polygons(tri[:,:,[0,2]]);keep=shapely.area(polys)>1e-10;tri=tri[keep];polys=polys[keep]
      refs[str(audit.relative_to(ROOT))]=digest(audit.read_bytes());rp=folder/'original/download.json';refs[str(rp.relative_to(ROOT))]=digest(rp.read_bytes())
      cache[sheet]=(tri,shapely.STRtree(polys),{'sheet':sheet,'cache':str(folder.relative_to(ROOT)),'directorySHA256':current['directorySHA256'],'originalTriangles':len(tri)})
   if cache[sheet] is None:unavailable.append(sheet);continue
   tri,tree,record=cache[sheet];records.append(record)
   si,fi=tree.query(shapely.points(points[:,[0,2]]),predicate='dwithin',distance=1e-7);t=tri[fi];p0,p1,p2=t[:,0],t[:,1],t[:,2];v=points[si][:,[0,2]]-p2[:,[0,2]];u0=p0[:,[0,2]]-p2[:,[0,2]];u1=p1[:,[0,2]]-p2[:,[0,2]];det=u0[:,0]*u1[:,1]-u1[:,0]*u0[:,1]
   u=(v[:,0]*u1[:,1]-u1[:,0]*v[:,1])/det;v1=(u0[:,0]*v[:,1]-v[:,0]*u0[:,1])/det;inside=np.minimum(np.minimum(u,v1),1-u-v1)>=-1e-7
   heights=u*p0[:,1]+v1*p1[:,1]+(1-u-v1)*p2[:,1];gaps=points[si,1]-heights;ok=inside&(gaps>=-.5)&(~low[si]|(gaps<=1));np.logical_or.at(tinpass,si,ok);np.logical_or.at(tincontact,si,ok&(gaps<=.1)&low[si])
  only=tinpass&~possible;possible|=tinpass;contact|=tincontact
  item={'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'checks':len(points),'lowChecks':int(low.sum()),'tinOnlyRecoverablePoints':int(only.sum()),'unresolvedAcrossThreeOriginals':int((~possible).sum()),'contactPossible':bool(contact.any()),'pointwisePositive':bool(possible.all() and contact.any() and not unavailable),'unavailableCurrentTerrainSheets':unavailable,'terrainReceipts':records}
  rows.append(item);print(json.dumps({k:item[k] for k in ['uid','tinOnlyRecoverablePoints','unresolvedAcrossThreeOriginals','pointwisePositive','unavailableCurrentTerrainSheets']}),flush=True)
 for path,pinned in refs.items():assert digest((ROOT/path).read_bytes())==pinned
 refs.update({str((base/n).relative_to(ROOT)):digest((base/n).read_bytes()) for n in ['check-selection.json.gz','context.json.gz','preflight.json']})
 for file in [Path(__file__),DIR/'xl-second-pass.py',DIR/'xl-indexed-terrain-continuation.py']:refs[str(file.relative_to(ROOT))]=digest(file.read_bytes())
 save(doc/'result.json',{'rows':rows,'inputHashes':refs,'historicalManifestChanges':changed,'diagnosticOnly':True,'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0,'qualification':'Any original TIN facet plus original DTM/root sample feasibility, including all vertices, face centres and <=1m low edges. Cached current directory hashes and complete unmodified terrain members verified. Model pose inputs unchanged; a changed manifest is retained explicitly as context only. Missing current TIN sheets prevent positive credit. Pointwise positives never establish coherent terrain, physical safety, identity or installation acceptance.'})
 print(json.dumps({'models':len(rows),'positiveUids':[r['uid'] for r in rows if r['pointwisePositive']]}),flush=True)
if __name__=='__main__':main()
