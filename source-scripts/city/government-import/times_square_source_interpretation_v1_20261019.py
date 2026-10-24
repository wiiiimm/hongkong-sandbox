"""Hash-bound interpretation of Times Square original facade seams; not installation approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-times-square-source-interpretation-v1-20261019'
DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 refs=[Path(__file__)];pins={};decisions=[]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for uid,count,nfaces in [('254824',94,20),('266146',74,8)]:
   context=BASE/f'government-xl-times-square-{uid}-failed-face-context-v1-20261019'
   views=BASE/f'government-xl-times-square-{uid}-original-views-v3-20261019'
   for folder in [context,views]:
    r=read(folder/'result.json')
    assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
    refs.append(folder/'result.json')
    for e in r['evidenceRefs']:
     assert e['path'] not in pins or pins[e['path']]==e['sha256']
     pins[e['path']]=e['sha256']
   f=read(context/'faces.json')
   assert len(f['failedSamples'])==count and len(f['incidentFaces'])==nfaces
   assert all(abs(x['normal'][1])<.01 for x in f['incidentFaces'])
   images=[views/(n+'.png')for n in ['whole-reverse','lower-front','lower-reverse']]+[context/'failed-faces.png']
   decisions.append(dict(uid=f['uid'],sourceSHA256=f['sourceSHA256'],supportSHA256=f['supportSHA256'],failedSamples=count,sourceFaceIds=[x['faceId']for x in f['incidentFaces']],reviewer='Codex ROOT',interpretation='Unchanged original tower walls meet the original podium at facade seams. Failed rim samples belong exclusively to vertical facade faces, rather than upward support surfaces. Solid front/reverse views show the authored tower/podium assembly; no visible large separation at the reviewed scale. This is source interpretation only: near-face distances are not strict support contacts, and all failed samples remain failed.',imagesActuallyInspected=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],sourceFunctionalInterpretationAccepted=True,strictInterfacePassed=False,physicalAccepted=False,installationApproved=False))
 for p,h in pins.items():
  assert digest((ROOT/p).read_bytes())==h,p
  refs.append(ROOT/p)
 remaining=['Refresh whole affected terrain and installed-neighbour scope against current manifest','Bind complete original/literal/Float32 source coordinates and check all foundations','Attribute the single non-upward buried Tower254824 face without changing source geometry','Reconcile ordinary checks and exact-source applicability','Staged/live viewer checks, guarded publication, Neon installed verification, commit and push']
 save(DOC/'ROOT-SOURCE-INTERPRETATION.json',dict(rows=decisions,remainingRequiredWork=remaining,aiGeometryModelling=False,sourceGeometryChanges=0,installationApproved=False))
 module('times_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'times-square-exact-original-facade-seam-interpretation',list(dict.fromkeys(refs)),dict(uids=['landsd/233901:0','landsd/254824:0','landsd/266146:0'],interpretationAccepted=True,rawFailedSamples=168,installationApproved=False,remainingRequiredWork=remaining))
if __name__=='__main__':main()
