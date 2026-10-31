"""Scoped identity review of unchanged Blocks13/14 on their actual shared podium.

Retain the tower/podium-only diagnostic's failures; neither tower supports the
other. Only the independently evidenced shared support is related, not every
member of an estate or every footprint sharing an occupation permit.
"""
from pathlib import Path
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-shared-podium-pair-identity-v1-20261021';DOC=BASE/BATCH
UIDS={'landsd/253980:0','landsd/255260:0'};POD='landsd/254491:0';PODSHA='8d1de7a507bedd3b321786220569d5ff4ee279496220bd1e5c93580411c7ad77'
assert not DOC.exists();refs=[Path(__file__)];pins={}
def take(n,f):
 folder=BASE/n;_,ps=authenticate(folder);p=folder/f;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([folder/'result.json',p]);return read(p)
s=take('government-xl-parkview-four-raw-identity-v1-20261021','selection.json.gz');rows=[r for r in s['rows']if r['uid']in UIDS];assert len(rows)==2
raw=take('government-xl-parkview-13-14-pair-bounds-v1-20261021','raw-compound.json')
assert set(raw['reasons'])=={'wrong-tower-podium-types','exact-original-support-interface','compound-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2'}
primary=take('government-xl-parkview-13-14-primary-context-v1-20261021','context.json.gz')['rows']
physical=take('government-xl-parkview-four-physical-review-v1-20261021','ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted'] and physical['sourceGeometryChanges']==physical['sourcePoseChanges']==0
support=take('government-xl-parkview-12-15-shared-support-v2-20261021','support-checks.json.gz')['rows']
current=take('government-xl-parkview-12-15-shared-runtime-v2-20261021','selection.json.gz');pod=next(r for r in current['rows']if r['uid']==POD);assert pod['sourceSHA256']==PODSHA
p=ROOT/pod['candidate']['path'];assert digest(p.read_bytes())==PODSHA;refs.append(p)
final=module('parkview_shared_pair_forms',HERE/'xl-final-script-pass.py');forms={};sources=[];targets=[];verified=[]
for r in rows:
 uid=r['uid'];sha=r['sourceSHA256'];b=r['source']['building'];assert b['parent']=='way/930916577' and b['structureType']=='Tower'
 proof=take('government-xl-parkview-four-raw-identity-v1-20261021',uid.split('/')[1]+'-identity.json')
 expected={'fresh-current-spatial-bound:targetCoveredBySourceProjection','full-source-target-coverage'}if uid=='landsd/253980:0' else set()
 assert set(proof['reasons'])==expected and proof['sourceSHA256']==sha
 ctx=take('government-xl-parkview-four-raw-identity-v1-20261021',uid.split('/')[1]+'-context.json')
 p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==sha;refs.append(p);tri=decode_original_world_triangles(p.read_bytes());assert digest(tri.astype('<f8').tobytes())==proof['worldTrianglesSHA256']
 lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);assert final.identity_context(r,tri,near)==ctx['identity']
 for form,_,url in near:
  assert digest((ROOT/'3d-viewer'/url).read_bytes())==ctx['neighbourTileHashes'][url];forms[form['uid']]=form;refs.append(ROOT/'3d-viewer'/url)
 sources.append(shapely.union_all(shapely.polygons(tri[:,:,[0,2]])));targets.append(Polygon(b['rings'][0],b['rings'][1:]))
 pr=next(x for x in primary if x['uid']==uid);assert pr['sourceSHA256']==sha and len(pr['provider']['features'])==1;a=pr['provider']['features'][0]['attributes'];assert a['BuildingCSUID']==b['buildingCSUID'] and a['Status']=='Active' and a['BuildingBlockType']=='Tower'
 ids={f['attributes']['BuildingStructureID']for f in pr['opRelations']['features']};assert ids and ids=={f['attributes']['BuildingStructureID']for f in pr['opStructures']['features']};assert {f['attributes']['OPNo']for f in pr['opStructures']['features']}=={'H137/89'}
 sr=next(x for x in support if x['uid']==uid);assert sr['sourceSHA256']==sha and sr['supportUid']==POD and sr['supportSHA256']==PODSHA
 assert physical['sourceSHA256ByUid'][uid]==sha
 accounts=[x for x in physical['sampleAccounts']if x['uid']==uid];assert {x['mode']for x in accounts}=={'original','literal','explicitLeftF32','explicitBalancedF32'}
 for x in accounts:assert x['samples']==x['canonicalStrictContacts']+x['verifiedBoundedPaths']+x['additionalExactContactPaths']
 verified.append(dict(uid=uid,sourceSHA256=sha,rawIndividualReasons=proof['reasons'],proof=dict(identityAccepted=True,exactBuildingCSUID=True,exactObjectId=True,uniqueViewerMatch=True)))
assert forms[POD]['buildingCSUID']=='3860813197P20060312' and forms[POD]==pod['source']['building']
source=shapely.union_all(sources);target=shapely.union_all(targets);excess=source.difference(target)
foreign=[Polygon(b['rings'][0],b['rings'][1:])for b in forms.values()if b['uid']not in UIDS|{POD} and b.get('parent')!='way/930916577']
foreignarea=excess.intersection(shapely.union_all(foreign)).area if foreign else 0
coverage=source.intersection(target).area/target.area
assert .95<=coverage<=1.000000001 and raw['measures']['sourceExcessMaximumDistanceFromTargetM']<=10 and foreignarea<=1
manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==s['manifestSHA256']==current['manifestSHA256'];refs.append(manifest)
result=dict(uids=sorted(UIDS),rows=verified,identityAccepted=True,passed=True,reasons=[],rawCompound=raw,actualSharedSupport=dict(uid=POD,sourceSHA256=PODSHA),relatedSupportOverlapM2=excess.intersection(Polygon(forms[POD]['rings'][0],forms[POD]['rings'][1:])).area,targetCoveredBySourceProjection=coverage,remainingUnrelatedOverlapM2=foreignarea,currentManifestSHA256=s['manifestSHA256'],installationApproved=False,publicationApproved=False,sourceGeometryChanges=0,qualification='Exact original Blocks13/14 identity only. Same parent and official permit, distinct exact component IDs, unchanged complete source poses and raw hard identity checks. Both towers rest on the separately identified actual shared podium with source-specific physical review; neither rests on the other. Only that exact support is excluded from unrelated overlap. Raw pair/type/interface and individual coverage failures remain. All installation gates stay separate.')
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
save(DOC/'identity.json',result);refs.extend([HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
module('parkview_shared_pair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-shared-podium-pair-identity',list(dict.fromkeys(refs)),dict(uids=sorted(UIDS),identityAccepted=True,installationApproved=False));print('Identity reviewed; remaining foreign overlap',foreignarea,flush=True)
