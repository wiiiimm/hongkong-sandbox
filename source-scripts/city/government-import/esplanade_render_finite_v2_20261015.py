"""Capture unchanged original render attributes and complete missing podium arithmetic checks."""
from pathlib import Path
import importlib.util,subprocess,uuid,shutil
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_original_paired_finite_clearance_v3_20261011 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-esplanade-render-finite-v2-20261015';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015';LOCAL=HERE/'local'/PHYSICAL.name

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 receipt=read(PHYSICAL/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 rows=read(PHYSICAL/'selection.json.gz')['rows'];rows.sort(key=lambda r:r['uid']);assert [r['uid']for r in rows]==['landsd/268828:0','landsd/309385:0']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';catalogues=[ref(ROOT/'3d-viewer'/p)for p in read(manifest)['officialModelCatalogues']]
 claim=reservations.claim('esplanade-render-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();save(DOC/'input.json.gz',dict(currentManifest=ref(manifest),currentCatalogueRefs=catalogues,evidenceRefs=receipt['evidenceRefs'],rows=[dict(uid=r['uid'],entry=r['candidate']['entry'],building=r['source']['building'],path=r['candidate']['path'])for r in rows]))
  tool=HERE/'esplanade_actual_render_attributes_v1_20261015.mjs'
  prior=BASE/'government-xl-esplanade-render-finite-v1-20261015'
  old=read(prior/'attributes.json.gz');assert old['startEndAllInputsVerified']
  for p,h in old['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  assert read(prior/'input.json.gz')==read(DOC/'input.json.gz')
  shutil.copyfile(prior/'attributes.json.gz',DOC/'attributes.json.gz');save(DOC/'reused-capture.json',dict(source=ref(prior/'attributes.json.gz'),failedCaller=ref(HERE/'esplanade_render_finite_v1_20261015.py'),reason='V1 selected wrong runtime UID after successful capture; no finite calculations completed.'))
  captured=read(DOC/'attributes.json.gz');assert captured['startEndAllInputsVerified'];r=next(r for r in captured['rows']if r['uid']=='landsd/309385:0');rt=next(q for q in read(LOCAL/'runtime-geometry.json.gz')['rows']if q['uid']==r['uid']);assert r['completeLiteralWorldPosition']==rt['position']and r['completeOriginalIndex']==rt['index'];ix=np.asarray(r['completeOriginalIndex']).reshape(-1,3);ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);summary=[]
  for mode,key in [('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:
   tri=np.asarray(r[key],float).reshape(-1,3)[ix];assert len(tri)==1476;faces=[]
   for i,face in enumerate(tri):
    faces.append(dict(sourceFace=i,proof=verify(face,ground)))
    if i%50==0:assert reservations.heartbeat(lease)['ok'];print(mode,i,len(tri),flush=True)
   save(DOC/(mode+'.json.gz'),dict(worldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),faces=faces,installationApproved=False))
   summary.append(dict(mode=mode,faces=len(faces),uncovered=[r['sourceFace']for r in faces if not r['proof']['groundProjectionCovered']],unproved=[r['sourceFace']for r in faces if not r['proof']['existingOrdinaryClearanceBoundProved']]))
  for p,h in captured['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
  paths=[Path(__file__),tool,PHYSICAL/'result.json',LOCAL/'runtime-geometry.json.gz']+[ROOT/p for p in captured['inputHashes']]+[HERE/n for n in ['exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py']]
  spec=importlib.util.spec_from_file_location('freeze_esplanade_render',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'actual-render-and-complete-podium-two-f32-finite-v1',paths,dict(uids=[r['uid']for r in rows],rows=summary,fullAcceptance=False,qualification='Actual renderer attributes for both original sources; complete podium finite checks for two explicit Float32 arithmetic orders. No universal GPU guarantee, source-role approval or publication.'));print(summary,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
