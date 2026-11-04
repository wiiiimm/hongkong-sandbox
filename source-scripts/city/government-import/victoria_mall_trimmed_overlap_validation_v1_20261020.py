"""Rebind unchanged original overlap evidence to the exact trimmed terrain."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
import native_patch_resolution as repair
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-victoria-mall-trimmed-overlap-validation-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-victoria-mall-trim-unused-margin-v2-20261020'
assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
patch=read(SRC/'candidate-terrain.json');account=read(SRC/'face-account.json');oldpath=HERE/'local/government-xl-victoria-mall-candidate-terrain-v2-20261020/candidate-terrain.json';old=read(oldpath);assert str(oldpath.relative_to(ROOT))in pins
oldfaces=repair._faces(old);newfaces=repair._faces(patch);unchanged={tuple(oldfaces[i].reshape(-1)):i for i in account['retained']};polys=shapely.polygons(newfaces[:,:,[0,2]]);tree=shapely.STRtree(polys);pairs=tree.query(polys,predicate='intersects');rows=[]
for a,b in zip(*pairs):
 if a>=b:continue
 area=polys[a].intersection(polys[b]).area
 if area<=1e-10:continue
 fa=unchanged.get(tuple(newfaces[a].reshape(-1)));fb=unchanged.get(tuple(newfaces[b].reshape(-1)));assert fa is not None and fb is not None,'New overlap includes a cut/new facet'
 rows.append(dict(newFaces=[int(a),int(b)],unchangedOriginalCandidateFaces=[fa,fb],areaM2=float(area)))
assert rows
oldapproval=old['nativeMesh']['sourceOverlap'];auditpath=Path(oldapproval['evidencePath']);assert digest(auditpath.read_bytes())==oldapproval['evidenceSHA256'];refs.append(auditpath);audit=read(auditpath)
for source in audit['source']['files']:
 p=ROOT/source['path'];assert digest(p.read_bytes())==source['sha256'];refs.append(p)
DOC.mkdir();path=DOC/'candidate-terrain.json';save(path,patch);repair.approve_original_overlap(patch,path,DOC/'native-overlap.json',audit['source']['files']);repair.finalize_overlap_evidence(patch,DOC/'native-overlap.json');save(path,patch)
builder=module('victoria_trim_validate',HERE/'resolve-pass-indexed-parent-clipping.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';builder.validate_patch(patch,read(parentpath));assert len(patch['nativeMesh']['index'])//3<=25000
summary=dict(uids=r['uids'],candidateBuilt=True,validatorPassed=True,terrainTriangles=len(newfaces),terrainTriangleBudget=25000,unchangedOriginalOverlapPairs=len(rows),sourceGeometryChanges=0,installationApproved=False,bounds=r['bounds'],requiredNativeUids=r['requiredNativeUids'],installedTerrainOverlaps=r['installedTerrainOverlaps'],qualification='Every overlap pair uses two identical uncut prior source-backed facets. Fresh highest-surface audit binds the exact cropped output; no threshold changes.')
save(DOC/'unchanged-overlap-pairs.json',dict(rows=rows));save(DOC/'summary.json',summary)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
refs.extend([HERE/'native_patch_resolution.py',HERE/'resolve-pass-indexed-parent-clipping.py']);module('victoria_trim_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-trimmed-original-overlap-validation',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
