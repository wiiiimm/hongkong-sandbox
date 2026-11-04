"""Complete original assembly projection diagnostic. No identity or installation approval."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
CAP=BASE/'government-xl-west-wing26195-complete-current-runtime-capture-v2-20261012'
OUT=BASE/'government-xl-west-wing26195-original-assembly-projection-v2-20261015'
UIDS=['landsd/26195:0','landsd/322270:0','landsd/315069:0','landsd/319534:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists()
 saved=read(CAP/'literal-source-inputs.json.gz');forms={f['uid']:f for f in saved['completeCurrentForms']}
 tile=ROOT/'3d-viewer/city/data/tiles/0_0.json';current={f['uid']:f for f in read(tile)['buildings']}
 for u in UIDS:assert forms[u]==current[u],u
 manifest=ROOT/'3d-viewer/city/data/manifest.json';entries={};refs=[ref(Path(__file__)),ref(tile),ref(manifest),ref(CAP/'literal-source-inputs.json.gz')]
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid'] in UIDS:
    assert e['uid'] not in entries;entries[e['uid']]=(p.parent/e['asset'],e['sha256']);refs.append(ref(p))
 entries['landsd/319534:0']=(ROOT/'3d-viewer/city/data/official-models/tourist-trial-001/6f085985d3ea19699c010d73d173d288107c3d3eea372bf5704a854bd2b1e2c1.glb.gz','6f085985d3ea19699c010d73d173d288107c3d3eea372bf5704a854bd2b1e2c1')
 assert set(entries)==set(UIDS),list(entries)
 projections={};targets={};vertices={};rows=[]
 for u in UIDS:
  p,sha=entries[u];assert ref(p)['sha256']==sha;refs.append(ref(p));tri=decode_original_world_triangles(p.read_bytes())
  vertices[u]=tri[:,:,[0,2]].reshape(-1,2);ps=[Polygon(t[:,[0,2]])for t in tri];proj=unary_union([p for p in ps if p.area>0]);f=forms[u];target=Polygon(f['rings'][0],f['rings'][1:]);projections[u]=proj;targets[u]=target
  rows.append(dict(uid=u,sourceSHA256=sha,completeFaces=len(tri),sourceArea=proj.area,targetArea=target.area,individualTargetCoverage=proj.intersection(target).area/target.area))
 scenarios=[]
 for ids in [UIDS[:1],UIDS[:2],UIDS[:3],UIDS]:
  p=unary_union([projections[u]for u in ids]);t=unary_union([targets[u]for u in ids]);scenarios.append(dict(uids=ids,sourceArea=p.area,targetArea=t.area,targetCoverage=p.intersection(t).area/t.area,missingTargetArea=t.difference(p).area,sourceOutsideTargetArea=p.difference(t).area,sourceExcessMaximumDistanceFromTargetM=float(shapely.distance(shapely.points(np.concatenate([vertices[u]for u in ids])),t).max()),otherCapturedFormOverlap=[dict(uid=u,area=p.intersection(Polygon(f['rings'][0],f['rings'][1:])).area)for u,f in forms.items()if u not in ids and p.intersection(Polygon(f['rings'][0],f['rings'][1:])).area>0]))
 for r in refs:assert ref(ROOT/r['path'])==r
 save(OUT/'projection.json',dict(sourceOnly=True,installationApproved=False,geometryChanges=0,newlyInstalled=0,physicalChecksPerformed=False,groupIdentityApproved=False,rows=rows,scenarios=scenarios,inputRefs=refs))
 print(scenarios)
if __name__=='__main__':main()
