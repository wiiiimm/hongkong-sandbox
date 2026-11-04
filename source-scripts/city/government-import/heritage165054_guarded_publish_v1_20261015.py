"""Guard the unchanged joint publisher with all47 original-model resource leases."""
import argparse,json,sys,hashlib
from pathlib import Path
from contextlib import contextmanager
import heritage165054_joint_private_stage_v1_20261015 as stage
from run import connect,reservations,dict_row
ROOT=stage.ROOT

def main():
 ap=argparse.ArgumentParser();ap.add_argument('plan');ap.add_argument('--receipt',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--apply',action='store_true');args=ap.parse_args()
 assert args.phase=='government-xl-heritage165054-original-installed-v1-20261015'
 assert (ROOT/args.plan).resolve()==stage.STAGE/'plan.json'
 report=stage.read(stage.DOC/'result.json');verified=stage.read(stage.DOC/'ROOT-VERIFIED.json');assert report['jobId']==verified['jobId']=='908612b5fc795b9e9751dcd383345ffb91e0b78d6f3abf964babe1ab8d9646fa'and verified['allEvidenceHashesVerified']
 plan=stage.read(ROOT/args.plan);models=stage.read(ROOT/plan['areas'][0]['catalogue'])['models'];assert len(models)==1 and models[0]['uid']==stage.UID and models[0]['sha256']==stage.original.SOURCE
 assert len(plan['areas'])==len(plan['topLevelTerrainPatches'])==1 and plan['areas'][0]['estimates']==[str((stage.STAGE/'estimated-bases.json').relative_to(ROOT))]
 assert plan['topLevelTerrainPatches'][0]['sha256']=='21216b7acafb198484957ce604fa89555df57d7f574930f7a9a28b3b7a508fc1'
 forms=stage.read(stage.shelter.capture.DOC/'input.json.gz')['currentForms'];keys=set(stage.shelter.capture.resources([f['building']['uid']for f in forms]));keys={k for k in keys if not k.startswith('immutable-source-proof:')}
 immutable=[q for q in report['evidenceRefs']if q['path'].startswith(str(stage.STAGE.relative_to(ROOT))+'/')]
 assert immutable and len(keys)==46
 @contextmanager
 def guard():
  with connect()as db:
   db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));g=reservations._current(db,json.loads(Path(args.receipt).read_text()));assert g and keys<=set(g['resources'])
   for q in immutable:stage.check(q)
   yield
 with guard():pass
 pub=stage.original.prior.module(stage.HERE.parent/'island-detail-integration/publish.py','heritage_unchanged_joint_publisher');pub.PUBLICATION_GUARD=guard;pub.DOC=ROOT/'docs/astra-city/model-integration-20260909'/args.phase
 sys.argv=['publish.py',args.plan]+(['--apply']if args.apply else[]);pub.main()
if __name__=='__main__':main()
