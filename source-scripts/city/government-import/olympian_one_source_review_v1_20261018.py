"""ROOT source interpretation, exact originals only; not installation approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-olympian-one-source-review-v1-20261018';DOC=BASE/BATCH
VIEWS=BASE/'government-xl-olympian-one-original-views-v1-20261018';FACES=BASE/'government-xl-olympian-one-failed-face-context-v1-20261018';PAIR=BASE/'government-xl-olympian-one-original-assembly-v1-20261018'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [VIEWS,FACES,PAIR]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 faces=read(FACES/'faces.json');assert len(faces['failedSamples'])==47 and len(faces['incidentFaces'])==15
 assert all(f['reason']=='support-above-rim' for f in faces['failedSamples'])
 expected=[2424,2425,2426,3014,3015,3016,3017,3018,3019,4177,4178,4179,4180,4181,4182]
 assert [r['faceId']for r in faces['incidentFaces']]==expected
 report=read(VIEWS/'render.json');assert len(report['views'])==4 and not report['errors']
 images=[ref(VIEWS/(n+'.png'))for n in ['whole','whole-reverse','lower-front','lower-reverse']]+[ref(FACES/'failed-faces.png')]
 strict=read(BASE/'government-xl-olympian-one-interface-distances-v1-20261018/support-checks.json.gz')['rows'][0]['interface'];assert strict['passed']is False and strict['samples']==497 and strict['strictContacts']==450 and len(strict['unresolved'])==47
 bindings=[dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],buildingCSUID=r['candidate']['entry']['buildingCSUID'],worldBounds=r['candidate']['entry']['worldBounds'])for r in read(PAIR/'selection.json.gz')['rows']]
 decision=dict(reviewer='Codex ROOT',reviewType='exact-original-source-functional-interpretation',sourceBindings=bindings,imagesActuallyInspected=images,faceEvidence=ref(FACES/'faces.json'),rawStrictInterfaceVerbatim=strict,
 interpretation='The 47 failed samples lie on lower edges of 15 authored lower facade-band faces of the original Bank of China Centre. Solid whole-assembly and reverse/front lower-interface views show these walls continuing into the stepped Olympian City One podium. They are not 47 independent support feet. The exact original tower also contains visible lower columns; 450 strict contacts remain independently measured. This interpretation does not claim all 15 faces are mathematically vertical, certify structural adequacy, or prove contact at any of the 47 failed samples.',
 sourceFunctionalInterpretationAccepted=True,strictOriginalInterfacePassed=False,all47FailuresRemainNumericallyFailed=True,independentSupportFor47SamplesProved=False,sourceFaceIds=expected,
 proposedNarrowApplicability=['landsd/256927:0:ground-contact-unresolved','landsd/256927:0:sampled-ground-gap-below-model-bottom','original-support-interface-unresolved'],
 qualification='Interpretation of these two original source hashes and these 15 faces only. No global threshold or validation code changed. Apply only after exact current source/runtime and complete compound-foundation bindings; other identity, terrain, foreign-actor, collision, runtime and staged/live browser requirements remain independent.',
 remainingRequiredWork=['Podium extent identity review and binding','Exact source/current renderer binding for the scoped applicability adapter','Full paired-source physical and foreign-actor checks','Staged and live browser acceptance','Guarded publication and installed Neon review readback'],
 installationApproved=False,publicationApproved=False,physicalAccepted=False,modelGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False)
 save(DOC/'ROOT-SOURCE-INTERPRETATION.json',decision)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('olympian_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-lower-facade-source-interpretation',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in bindings],interpretationAccepted=True,strictInterfacePassed=False,installationApproved=False,remainingRequiredWork=decision['remainingRequiredWork']))
if __name__=='__main__':main()
