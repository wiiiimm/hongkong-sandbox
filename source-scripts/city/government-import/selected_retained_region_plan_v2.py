"""Plan exact transitive terrain retention for an explicit original source; never queue/publish."""
import numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'

def main():
 import argparse
 ap=argparse.ArgumentParser(description=__doc__)
 for key in ["batch","terrain","uid"]:ap.add_argument("--"+key,required=True)
 args=ap.parse_args();BATCH=args.batch;OLD=args.terrain
 assert BATCH.startswith("government-xl-") and "/" not in BATCH
 doc=BASE/BATCH;assert not doc.exists()
 r,pins=authenticate(BASE/OLD);refs=[Path(__file__),BASE/OLD/'result.json']
 assert r['uids']==[args.uid]
 scope=BASE/OLD/'scope.json';assert digest(scope.read_bytes())==pins[str(scope.relative_to(ROOT))]
 source=BASE/OLD/'unapproved-terrain.json';assert digest(source.read_bytes())==pins[str(source.relative_to(ROOT))]
 mp=ROOT/'3d-viewer/city/data/manifest.json';rootpath=ROOT/'3d-viewer/city/data/terrain.json';manifest=read(mp);parent=read(rootpath);refs.extend([scope,source,mp,rootpath]);builder=module('retained_region_scope_builder',HERE/'resolve-pass-indexed-parent-clipping.py');refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
 cells=read(scope)['cells'];allnodes=[]
 for entry in manifest['terrainPatches']:
  p=ROOT/'3d-viewer'/entry['url'];raw=p.read_bytes();node=read(p);extent=builder.extent(node['coarseCells'],parent)
  allnodes.append(dict(entry=entry,path=p,sha256=digest(raw),node=node,extent=extent))
 selected={};changed=True
 while changed:
  changed=False;region=shapely.box(*builder.extent(cells,parent))
  for x in allnodes:
   if x['entry']['url']in selected:continue
   if region.intersection(shapely.box(*x['extent'])).area<=0:continue
   selected[x['entry']['url']]=x;oldcells=cells[:];c=x['node']['coarseCells'];cells=[min(cells[0],c[0]),min(cells[1],c[1]),max(cells[2],c[2]),max(cells[3],c[3])];changed|=cells!=oldcells
 domain=builder.extent(cells,parent);rows=[]
 for x in selected.values():
  node=x['node'];faces=len(node['nativeMesh']['index'])//3 if node.get('nativeMesh')else None
  rows.append(dict(url=x['entry']['url'],sha256=x['sha256'],extent=x['extent'],retainedUids=node['meta'].get('targetUids',[]),drawnTriangles=faces,native=bool(node.get('nativeMesh')),nested=bool(node.get('patches'))));refs.append(x['path'])
 sampler=builder.terrain.fine.DemSampler(parent,rendered=True)
 g=parent['meta']['georef'];heights=[sampler.ground(g['bE']+c*g['aE']-834500,816500-g['bN']-rr*g['aN'])for rr in range(cells[1],cells[3]+1)for c in range(cells[0],cells[2]+1)]
 result=dict(uids=[args.uid],regionalCoarseCells=cells,regionalParentExtent=domain,retainedPatches=rows,retainedPatchCount=len(rows),retainedTriangleCount=sum(x['drawnTriangles']or 0 for x in rows),allFlatNative=all(x['native']and not x['nested']for x in rows),rootRenderedMinimumHeight=min(heights),privateInset=dict(path=str(source.relative_to(ROOT)),sha256=digest(source.read_bytes()),bounds=read(scope)['bounds']),installationApproved=False,publication=False,newlyInstalled=0,sourceGeometryChanges=0,scriptExternalAICalls=0,qualification='Source-only geometric retention closure, not production optimisation plan/queue or physical approval. Every affected current actor still requires full regression checks.')
 save(doc/'summary.json',result)
 module('retained_region_plan_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'selected-original-terrain-retention-scope',refs,result)
 print({k:result[k]for k in ['retainedPatchCount','retainedTriangleCount','regionalParentExtent','allFlatNative','rootRenderedMinimumHeight']},flush=True)
if __name__=='__main__':main()
