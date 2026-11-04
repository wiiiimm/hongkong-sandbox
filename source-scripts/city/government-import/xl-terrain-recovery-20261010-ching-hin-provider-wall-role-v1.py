"""Freeze the actual provider's three unchanged exposed exterior wall faces."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
BATCH='xl-terrain-recovery-20261010-ching-hin-provider-wall-role-v1'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-ching-hin-original-terrain-current-v3-20261010'
CONTEXT=BASE/'xl-terrain-recovery-20261010-ching-hin-finite-wall-grade-context-v1'
UID='landsd/26653:0';SOURCE='0227d927876111d76bd70098d4e2ab0413e4f59d17f9ff9494a5f6d803523f76'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();row=read(PHYSICAL/'selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE and row['uid']==UID
 receipt=read(CONTEXT/'result.json')
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 tri=decode_original_world_triangles(raw);d=read(CONTEXT/'diagnostic.json.gz');ctx=d['completeCertifiedLowerBoundContexts'];assert len(tri)==len(ctx)==16555
 streams=source_stream_binding(raw);faces=[1161,1518,1998];assert d['originalCapPaths']['affectedOriginalWallFaces']==faces and not d['originalCapPaths']['rawExposureFailures']
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);assert all(normals[i,1]==0 and np.linalg.norm(normals[i])>0 for i in faces)
 provenance=dict(provider='Hong Kong Lands Department original government mesh',candidateSource=ref(asset),selection=ref(PHYSICAL/'selection.json.gz'),sourceSHA256=SOURCE,modelId=row['modelId'],buildingCSUID=row['source']['building']['buildingCSUID'],exactPackedSourceStreams=streams,completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),originalExteriorWallFaces=[dict(sourceFace=i,originalVertices=tri[i].tolist(),originalNormal=normals[i].tolist(),authoredOpenExteriorClearRoofPath=next(p for p in d['originalCapPaths']['paths'] if p['sourceFace']==i)) for i in faces],completeSourceFaceInventory=16555,roleBasis='Original vertical exterior faces cross complete finite ground, remain exposed, and connect through original authored faces to strict-clear original caps/roofs; no closed-solid or basement claim.',sourceGeometryChanges=0)
 role=dict(role='original-provider-exterior-ground-crossing-walls',uid=UID,sourceSHA256=SOURCE,originalFaceCount=16555,wallFaces=faces,providerExteriorProvenanceBinding=provenance)
 save(DOC/'expected-role.json',role);refs=[ref(p) for p in [Path(__file__),asset,PHYSICAL/'selection.json.gz',CONTEXT/'result.json',CONTEXT/'diagnostic.json.gz',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']];save(DOC/'original-source-provenance.json',{**provenance,'evidenceRefs':refs})
 spec=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'immutable-actual-provider-exterior-wall-role-v1',[ROOT/r['path'] for r in refs],dict(uids=[UID],sourceSHA256=SOURCE,wallFaces=faces,originalFaceCount=16555,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False))
if __name__=='__main__':main()
