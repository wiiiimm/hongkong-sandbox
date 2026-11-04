"""Exact-source lower-perimeter interpretation; browser and publication remain separate."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-ferry-lower-perimeter-review-v1-20261020';DOC=BASE/BATCH
names=['perimeter-ground-views-v2','lower-surface-context-v1','podium-rim-verification-v2','buried-face-verification-v2','six-primary-records-v1','five-four-mode-foundations-v1','podium-rim-v1'];folders={n:BASE/('government-xl-china-ferry-'+n+'-20261020')for n in names};pins={};refs=[Path(__file__)]
assert not DOC.exists()
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for f in folders.values():
  r=read(f/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(f/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
context=read(folders['lower-surface-context-v1']/'geometry-context.json');uid=context['uid'];assert uid=='landsd/285642:0';faces=context['rows'];assert len(faces)==79;up=[x for x in faces if x['upward']];assert [x['face']for x in up]==[2883,2884,2885,2886,2887,2888,2889,3779];assert all(x['minimumAltitude']<1.31 and x['bounds'][1][1]<3.32 for x in up)
p=folders['six-primary-records-v1'];relation=next(x['attributes']for x in read(p/'relations.json')['features']if x['attributes']['BuildingCSUID']=='3526717841P20050930');record=next(x['attributes']for x in read(p/'structures.json')['features']if x['attributes']['BuildingStructureID']==relation['BuildingStructureID']);assert record['OPBlockType']=='Podium'and record['Storeys']==5 and record['StoreysInBasement']==2
accounts=[]
for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
 rim=read(folders['podium-rim-verification-v2']/(mode+'.json'));face=read(folders['buried-face-verification-v2']/(mode+'.json'));foundation=read(folders['five-four-mode-foundations-v1']/('285642:0-'+mode+'.json'))
 assert len(rim['rows'])==61 and len(face['rows'])==79 and rim['sourceWorldSHA256']==face['sourceWorldSHA256']==foundation['worldSHA256']
 assert rim['supportWorldSHA256']==face['supportWorldSHA256']
 assert all(x['finitePathVerified']and x['withinEndpointHeight']for x in rim['rows']+face['rows'])
 assert {x['target']for x in face['rows']}=={x['face']for x in faces}
 assert foundation['foundation']['completeTerrainTriangles']==20464 and foundation['foundation']['fullyBuriedTriangles']==79 and foundation['foundation']['fullyBuriedUpwardTriangles']==8
 accounts.append(dict(mode=mode,worldSHA256=face['sourceWorldSHA256'],groundSHA256=face['supportWorldSHA256'],rimSamplesWithFinitePaths=61,faceCentresWithFinitePaths=79,wholeFacePhysicalAcceptance=False))
images=[folders['perimeter-ground-views-v2']/(n+'.png')for n in ['north-low-edge','south-sloping-edge']]
review=dict(uid=uid,sourceSHA256=context['sourceSHA256'],reviewer='Codex ROOT',imagesActuallyViewed=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],primaryRecord=record,accounts=accounts,sourcePerimeterInterpretation='The exact affected faces occupy two narrow lower exterior regions of the original podium. The northern region follows the low wall edge; the southern region includes eight narrow upward-sloping facets rather than a broad buried roof. Complete source placement remains at native scale and coordinates. Both regions meet the drawn terrain via finite original-face paths. Official basement metadata supplies context but does not independently approve these intersections.',sourceRoleContextResolved=True,rawStrictFailuresRetained=True,wholeFacePhysicalAcceptance=False,installationApproved=False,publicationApproved=False,sourceGeometryChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,remaining='Complete browser/collision/visible-ground evaluation of these exact perimeter intersections before physical/publication acceptance; centroid paths do not prove every point on a face clears terrain.')
save(DOC/'ROOT-LOWER-PERIMETER-REVIEW.json',review)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
module('china_lower_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-lower-perimeter-source-interpretation',list(dict.fromkeys(refs)),dict(uids=[uid],sourceRoleContextResolved=True,installationApproved=False,sourceGeometryChanges=0))
