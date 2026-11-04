"""Review one exact native-sibling overlap under the current MAX-height renderer."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sham-shui-po-pool-';BATCH=PREFIX+'sibling-surface-review-v1-20261017';DOC=BASE/BATCH

def heights(face,points):
 a,b,c=face;u=b-a;v=c-a;d=points-a[[0,2]];det=u[0]*v[2]-u[2]*v[0];assert det!=0
 s=(d[:,0]*v[2]-d[:,1]*v[0])/det;t=(u[0]*d[:,1]-u[2]*d[:,0])/det
 bary=a[1]+s*u[1]+t*v[1];n=np.cross(u,v);plane=a[1]-(n[0]*d[:,0]+n[2]*d[:,1])/n[1]
 return bary,plane

def main():
 assert not DOC.exists();names=['installed-patch-overlap-audit-v1','native-regression-v6','basic-finite-v4','four-world-foundation-v4','original-group-browser-v6'];pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for n in names:
   p=BASE/(PREFIX+n+'-20261017')/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 audit=read(BASE/(PREFIX+names[0]+'-20261017')/'overlap-audit.json');assert audit['intersectionCells']==[481,380,482,382]
 native=read(BASE/(PREFIX+names[1]+'-20261017')/'summary.json');assert set(native['resolved'])=={'landsd/113733:0','landsd/138091:0','landsd/99395:0'} and all(r['passed']for r in native['rows'])
 assert [r['uid']for r in audit['retainedTargetActors']if r['touchesCandidateDomain']]==['landsd/99395:0'] and len(audit['retainedTargetActors'])==8
 finite=read(BASE/(PREFIX+names[2]+'-20261017')/'summary.json');assert finite['all84ActorsComplete']and finite['noIntroducedFailures']and len(finite['rows'])==84
 foundation=read(BASE/(PREFIX+names[3]+'-20261017')/'summary.json');assert foundation['allStrictPass']and len(foundation['rows'])==8
 browser=read(BASE/(PREFIX+names[4]+'-20261017')/'staged-browser.json');assert browser['passed']and not browser['errors']
 region=shapely.box(*audit['intersectionBounds']);groups=[]
 for q in [audit['candidate'],audit['retained']]:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];mesh=read(p)['nativeMesh'];tri=np.asarray(mesh['position'],dtype='<f4').astype(float).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)];polys=shapely.polygons(tri[:,:,[0,2]]);valid=(shapely.area(polys)>1e-10)&shapely.intersects(polys,region);ids=np.flatnonzero(valid);groups.append((tri[ids],polys[ids],ids));refs.append(p)
 (a,pa,ia),(b,pb,ib)=groups;pairs=shapely.STRtree(pb).query(pa,predicate='intersects');rows=[];maximum=0.;samples=0
 for x,y in zip(*pairs):
  overlap=pa[x].intersection(pb[y]).intersection(region)
  if overlap.area<=1e-10:continue
  coords=shapely.get_coordinates(overlap);ba,qa=heights(a[x],coords);bb,qb=heights(b[y],coords);error=float(np.max(np.abs(np.maximum(ba,bb)-np.maximum(qa,qb))));assert error<.004
  maximum=max(maximum,error);samples+=len(coords);rows.append(dict(candidateFace=int(ia[x]),retainedFace=int(ib[y]),areaM2=overlap.area,maxRayPlaneAgreementErrorM=error))
 assert rows and samples
 coverage=shapely.union_all(np.concatenate([pa,pb])).intersection(region);gap=region.difference(coverage).area;assert gap<=1e-8
 rendered=ROOT/'3d-viewer/city/world.js';sampler=ROOT/'3d-viewer/city/geo.js';assert 'group.add(makeNativeTerrain(patch))'in rendered.read_text() and 'Math.max(top,value)'in sampler.read_text()
 review=dict(status='reviewed-exact-native-sibling-overlap',candidate=audit['candidate'],retained=audit['retained'],replaced=audit['replaced'],intersectionCells=audit['intersectionCells'],intersectionBounds=audit['intersectionBounds'],intersectionAreaM2=region.area,combinedUncoveredAreaM2=gap,crossSourcePositiveOverlapPairs=len(rows),affineVertexSamples=samples,maxRayPlaneAgreementErrorM=maximum,completeBasicActors=84,retainedTargetActors=audit['retainedTargetActors'],completeNativeResolved=native['resolved'],retainedPatchByteUnchanged=True,buildingGeometryChanges=0,terrainGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publicationApproved=False,fullAcceptance=False,qualification='Exactly these two immutable native surface files. The renderer draws both complete surfaces and the sampler selects their maximum. Every positive cross-source overlap polygon has its independent barycentric/plane height equations checked at all vertices; affine error bounds and non-expansiveness of MAX preserve the agreement throughout. The retained native patch completely covers the overlap. Seven retained actor bounds are disjoint from the full changed domain; the eighth and both market actors passed complete native regression. All 84 basic actors pass complete finite before/after comparison. This permits preparation of a narrowly bound sibling-overlap publisher review; it is not a global overlap waiver or installation approval.')
 DOC.mkdir();save(DOC/'surface-pairs.json.gz',dict(rows=rows));save(DOC/'ROOT-SIBLING-SURFACE-REVIEW.json',review);refs += [rendered,sampler,ROOT/'3d-viewer/city/native-terrain.js',BASE/(PREFIX+names[0]+'-20261017')/'overlap-audit.json']
 out=module('pool_sibling_review_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-sibling-native-MAX-surface-review-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/265480:0','landsd/271043:0']+[r['uid']for r in audit['retainedTargetActors']],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],pairs=len(rows),samples=samples,maxErrorM=maximum,combinedGapM2=gap),flush=True)
if __name__=='__main__':main()
