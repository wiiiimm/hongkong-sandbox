"""Record bounded source-role interpretation; never global placement approval."""
from pathlib import Path
import numpy as np,shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-villa-podium-wall-review-v2-20261015';DOC=B/NAME
W=B/'government-xl-villa-five-original-and-rendered-finite-wall-contexts-v3-20261010';P=B/'government-xl-villa-premiere-five-original-primary-relationships-20261010';R=B/'government-xl-villa-current-geometry-rebind-v1-20261015';I=B/'government-xl-villa-five-current-identity-v1-20261015'
EXPECTED=[6717,6718,6721,6722,6725,6726,6729,6730,6739,6740,6745,6746,7030,14697,14698,14701,14702,14707,14708,14713,14714,14732,14733,14997]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not (DOC/'result.json').exists();pins={};receipts=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [W,P,R,I]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);receipts.append(folder/'result.json')
   # Old receipts keep historical live-map hashes. Only the archived files used
   # here are reused; the current geometry rebind and identity bind current inputs.
   for q in r['evidenceRefs']:
    p=ROOT/q['path']
    if folder in [R,I] or p.is_relative_to(folder):
     assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 assert read(R/'result.json')['currentSourceAndGroundArraysExactlyEqualHistorical']
 identity=read(I/'result.json')['rows'];assert len(identity)==5 and all(r['passed']and not r['reasons']for r in identity)
 source=read(DOC/'face-review-inputs.json');assert source['sourceSHA256']=='4407cbd52574f50e6b6bdddc6e581c96bbd0653426f89df0e490ae0b2096935d'and source['sourceFaces']==16669;assert [f['face']for f in source['affectedFaces']]==EXPECTED
 for q in source['inputRefs']:assert ref(ROOT/q['path'])==q
 primary=next(f['attributes']for f in read(P/'exact-current-primary.json')['features']if f['attributes']['BuildingCSUID']==source['primaryCSUID']);assert primary['BuildingBlockType']=='Podium'and primary['Storeys']==2 and primary['StoreysInBasement']==1 and primary['BaseHeight']==3.7 and primary['TopHeight']==11.9
 contexts=read(W/'diagnostic.json.gz')['rows'];podium=next(r for r in contexts if r['uid']=='landsd/89917:0')
 for row in contexts:
  for mode in ['completeOriginal','actualRendered']:
   c=row[mode];assert not c['unresolvedWallConditions']and not c['buriedUpwardFaces']
   if row['uid']=='landsd/89917:0':
    assert c['affectedFaces']==EXPECTED and not c['unexposedIndividualWallFaces'];assert c['wallPaths']['allAffectedWallsHaveRoles'];assert sorted(f['sourceFace']for f in c['wallPaths']['faces'])==EXPECTED;assert all(f['verifiedRoleNecessaryConditions']and not f['reasons']for f in c['wallPaths']['faces'])
   else:assert c['affectedFaces']==[]
 reviewed=DOC/'complete-podium-wall-views-2700x1800.png';prior=B/'government-xl-villa-podium-wall-review-v1-20261015/complete-podium-wall-views-2700x1800.png';assert reviewed.read_bytes()==prior.read_bytes()
 review=dict(uid='landsd/89917:0',sourceSHA256=source['sourceSHA256'],sourceRoleInterpretationAccepted=True,affectedFaces=EXPECTED,exactlyVerticalFaces=[f['face']for f in source['affectedFaces']if f['vertical']],authoredSlightlySlopedWallFaces=[f['face']for f in source['affectedFaces']if not f['vertical']],primaryRecord=dict(BuildingCSUID=source['primaryCSUID'],BuildingBlockType='Podium',Storeys=2,StoreysInBasement=1,BaseHeight=3.7,TopHeight=11.9),reviewedImage=ref(reviewed),interpretation='These exact lower podium side-wall records continue to exposed source roof edges; their lower portions intersect terrain around an officially recorded podium with basement. Source diagrams show peripheral and recessed courtyard walls, not an entire buried roof/floor. Preserve all original duplicate, slightly sloped and zero-projection records. The named source role resolves interpretation of these24 wall records only.',rawStrictClearanceFailuresRetained=True,scope='Exact original/literal source faces and ground bound by current numeric rebind; not a generic wall tolerance.',rootOrContactCredit=False,closedSolidClaim=False,structuralEngineeringClaim=False,foreignCollisionExemption=False,sourceGeometryChanges=0,fullAcceptance=False,installationApproved=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False)
 save(DOC/'ROOT-SOURCE-REVIEW.json',review);shutil.copyfile('/tmp/villa-podium-wall-views-v1-20261015.log',DOC/'prior-export-failure.log')
 paths=[ROOT/p for p in pins]+receipts+[Path(__file__),HERE/'villa_podium_wall_views_v1_20261015.py',HERE/'villa_podium_wall_views_v2_20261015.py',prior]+[ROOT/q['path']for q in source['inputRefs']]
 module('villa_role_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(NAME,'named-podium-source-wall-role-review',paths,dict(uids=['landsd/89917:0'],sourceRoleInterpretationAccepted=True,reviewedWallFaces=24,rawStrictFailuresRetained=True,fullAcceptance=False,installationApproved=False,sourceGeometryChanges=0))
if __name__=='__main__':main()
