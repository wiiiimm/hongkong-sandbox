"""Exact-source lower-facade interpretation; all physical acceptance remains separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-source-interpretation-v1-20261019';DOC=BASE/BATCH;PAIR=BASE/'government-xl-pacifica-original-assembly-v1-20261019'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)];folders=[PAIR];decisions=[]
 for uid in ['77826','75351']:
  folders.extend([BASE/f'government-xl-pacifica-{uid}-failed-face-context-v1-20261019',BASE/f'government-xl-pacifica-{uid}-original-views-v2-20261019'])
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in folders:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 stricts={r['uid']:r['proof']for r in read(PAIR/'support.json.gz')['rows']}
 for uid,count,faces_count in [('77826',23,33),('75351',7,4)]:
  facepath=BASE/f'government-xl-pacifica-{uid}-failed-face-context-v1-20261019/faces.json';faces=read(facepath);strict=stricts['landsd/'+uid+':0'];views=BASE/f'government-xl-pacifica-{uid}-original-views-v2-20261019'
  assert len(faces['failedSamples'])==count and len(faces['incidentFaces'])==faces_count and strict['passed']is False and len(strict['unresolved'])==count
  if uid=='77826':
   assert strict['strictContacts']==0 and all(abs(f['normal'][1])<.008 for f in faces['incidentFaces'])
   assert all(22.5572<f['minimumY']<22.5573 and 23.6169<f['maximumY']<23.6171 for f in faces['incidentFaces'])
   interpretation='All 23 minimum-rim samples are on a narrow 33-face near-vertical lower facade band, not a sample of the full tower-to-podium interface. Front and reverse solid source views locate that band along an authored lower projection beside the podium colonnade. Zero of these 23 points has proven strict support; this review does not replace that zero with a pass or establish independent support elsewhere. Whole-assembly physical acceptance still requires applicable complete-source evidence.'
  else:
   assert strict['strictContacts']==140 and [f['faceId']for f in faces['incidentFaces']]==[6680,6681,6682,8442]
   interpretation='The seven failed rim samples lie on four near-vertical lower facade faces beside an adjoining podium wall. Front and reverse source views show interleaved lower facade/podium features, rather than seven independent support feet. The existing 140 strict contacts remain valid, and all seven failures remain failed. The separate two upward buried faces must still be inspected and resolved; this observation does not approve them.'
  images=[ref(views/(name+'.png'))for name in ['whole-reverse','lower-front','lower-reverse']]+[ref(facepath.parent/'failed-faces.png')]
  decisions.append(dict(uid='landsd/'+uid+':0',sourceSHA256=faces['sourceSHA256'],supportSHA256=faces['supportSHA256'],reviewer='Codex ROOT',reviewType='exact-original-source-functional-interpretation',interpretation=interpretation,sourceFunctionalInterpretationAccepted=True,rawStrictInterfaceVerbatim=strict,strictInterfacePassed=False,sourceFaceIds=[f['faceId']for f in faces['incidentFaces']],faceEvidence=ref(facepath),imagesActuallyInspected=images,installationApproved=False,publicationApproved=False,physicalAccepted=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,modelGeometryChanges=0))
 remaining=['Exact current original/literal/two-Float32 geometry bindings and complete compound foundation checks','Inspect Tower 3 two upward compound-burial faces without hiding raw failures','Resolve podium and Tower 2/Tower 5 identity reasons with exact-source evidence','Demonstrate appropriate independent assembly contact and collision evidence, especially Tower 1 beyond its lowest facade band','Full staged/live browser and guarded publication checks']
 save(DOC/'ROOT-SOURCE-INTERPRETATION.json',dict(rows=decisions,qualification='Interpretation only, bound to exact original hashes and listed faces. No threshold, source geometry, pose or approval flags changed; no generic exception introduced.',remainingRequiredWork=remaining,installationApproved=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('pacifica_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-lower-facade-interpretation',list(dict.fromkeys(refs)),dict(uids=['landsd/283036:0','landsd/77826:0','landsd/75351:0'],interpretationAccepted=True,strictInterfacePassed=False,installationApproved=False,remainingRequiredWork=remaining))
if __name__=='__main__':main()
