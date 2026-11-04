"""Attach all exact original assembly owners without changing rendered terrain."""
from pathlib import Path
import copy
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from lai_chi_kok_renderer_revision_20261019 import resolve
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lai-chi-kok-terrain-ownership-v2-20261019';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
prior=BASE/'government-xl-lai-chi-kok-full-terrain-metrics-v9-20261019';functional=BASE/'government-xl-lai-chi-kok-functional-applicability-v2-20261019';refs=[Path(__file__),HERE/'lai_chi_kok_renderer_revision_20261019.py'];assert not DOC.exists()
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for d in [prior,functional]:
  r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');refs.extend(resolve(e['path'],e['sha256'])for e in r['evidenceRefs'])
ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
candidate=read(prior/'terrain-candidates.json')[0];src=ROOT/candidate['path'];assert ref(src)['sha256']==candidate['sha256'];old=read(src);patch=copy.deepcopy(old)
sources=read(functional/'qualification.json')['sourceSHA256ByUid'];assert len(sources)==8
retained={'landsd/273000:0','landsd/232096:0'};assert set(old['meta']['targetUids'])==retained|{'landsd/281463:0'}
patch['meta']['targetUids']=sorted(set(sources)|retained);proof=copy.deepcopy(patch);proof['meta']['targetUids']=old['meta']['targetUids'];assert proof==old
proof_tool=module('lai_owner_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');proof_tool.DOC=DOC;proof_tool.overlap_proof(patch,[src,Path(__file__)])
check=copy.deepcopy(patch);check['meta']['targetUids']=old['meta']['targetUids'];check['nativeMesh'].pop('sourceOverlap',None);old_without_proof=copy.deepcopy(old);old_without_proof['nativeMesh'].pop('sourceOverlap',None);assert check==old_without_proof
refs.append(HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py')
pub=module('lai_owner_validate',HERE.parent/'island-detail-integration/publish.py');pub.validate_patch(patch,read(ROOT/'3d-viewer/city/data/terrain.json'))
out=LOCAL/'terrain-lai-chi-kok.json';save(out,patch);save(DOC/'terrain-candidates.json',[{**candidate,'path':str(out.relative_to(ROOT)),'sha256':digest(out.read_bytes())}]);save(DOC/'metadata-equivalence.json',dict(previousTerrain=ref(src),replacementTerrain=ref(out),allowedMetadataChanges=['meta.targetUids','nativeMesh.sourceOverlap'],sourceOverlapProofRecomputed=True,retainedTargetUids=sorted(retained),replacementTargetUids=patch['meta']['targetUids'],completeRenderedPayloadEqual=True,terrainValidationPassed=True,renderedGeometryChanges=0,installationApproved=False))
refs.extend([out,src,HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py',ROOT/'3d-viewer/city/data/terrain.json'])
module('lai_owner_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-terrain-ownership-metadata-only',list(dict.fromkeys(refs)),dict(uids=sorted(sources),completeGeometryUnchanged=True,terrainValidationPassed=True,installationApproved=False))
