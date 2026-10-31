"""Bounded source-specific interpretation of the four original Harbour City joins."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from ocean_four_original_identity_review_v1_20261027 import SOURCES,P
BATCH='government-xl-ocean-native-junction-role-review-v1-20261027'
PAIRS={('landsd/234188:0','landsd/21915:0'):148,('landsd/234188:0','landsd/205767:0'):119,('landsd/210743:0','landsd/21915:0'):485,('landsd/231469:0','landsd/215934:0'):23}
MODES={'original','literal','leftF32','balancedF32'}
def verify_scope(roles,lineage,sources):
 assert sources==SOURCES and len(roles)==36 and len(lineage)==9
 assert len({(r['uid'],r['nativeUid'],r['mode'])for r in roles})==36
 assert {r['mode']for r in roles}==MODES
 assert {tuple((r['uid'],r['nativeUid']))for r in roles if r['contactCount']and r['mode']=='original'}==set(PAIRS)
 for pair,count in PAIRS.items():
  rows=[r for r in roles if(r['uid'],r['nativeUid'])==pair];assert len(rows)==4 and {r['mode']for r in rows}==MODES
  assert next(r for r in rows if r['mode']=='original')['contactCount']==count
 for r in roles:assert r['sourceSHA256']==SOURCES[r['uid']] and r['contactCount']==sum(r['roles'].values())
 for r in lineage:
  assert {m['mode']for m in r['modes']}==MODES and len(r['modes'])==4
  assert all(m['allRepresentedCrossingsHaveOriginalFacetPairContacts']for m in r['modes'])
 return True

def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();pins={};refs=[Path(__file__)];seen={}
 def take(name,file):
  if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
  path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selection=take(P+'runtime-v1-20261027','selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};roles=take(P+'native-roles-v1-20261027','summary.json')['rows'];lineage=take(P+'native-lineage-v1-20261027','summary.json')['rows'];assert verify_scope(roles,lineage,sources)
 identity=take(P+'identity-review-v1-20261027','summary.json') if (base/(P+'identity-review-v1-20261027')/'summary.json').exists() else take(P+'identity-review-v1-20261027','result.json')
 assert identity['identityAccepted'] and identity['sourceSHA256ByUid']==SOURCES
 forms={r['uid']:r['source']['building']for r in selection['rows']}
 for uid in SOURCES:
  for r in take(P+'model-scope-v1-20261027',uid.split('/')[1]+'-forms.json.gz'):forms.setdefault(r['building']['uid'],r['building'])
 native=take(P+'native-contacts-v1-20261027','native-input.json.gz');entries={r['uid']:r['entry']for r in native['rows']}
 for r in roles:assert r['nativeSHA256']==entries[r['nativeUid']]['sha256']
 for r in native['currentCatalogueRefs']:
  path=ROOT/r['path'];assert digest(path.read_bytes())==r['sha256'];refs.append(path)
 images=take(P+'native-junction-views-v1-20261027','summary.json')['exports'];assert {(i['uid'],i['nativeUid'])for i in images}==set(PAIRS)
 inspected=[]
 for item in images:
  ref=item['image'];path=ROOT/ref['path'];assert digest(path.read_bytes())==ref['sha256'];refs.append(path);inspected.append(ref)
 whole=take(P+'original-visual-v1-20261027','summary.json')['views'][0]['image'];assert digest((ROOT/whole['path']).read_bytes())==whole['sha256'];refs.append(ROOT/whole['path']);inspected.append(whole)
 primary=HERE/'local/government-xl-ocean-harbour-city-primary-v1-20261027';pdf=primary/'official-floor-plan-2023.pdf';request=read(primary/'official-floor-plan-2023.pdf.request.json');assert request['requestedURL']=='https://www.harbourcity.com.hk/media/HC_FloorPlans_Web_Mar2023.pdf'and digest(pdf.read_bytes())==request['sha256'];image=primary/'floorplan-full.png';assert image.exists();refs.extend([pdf,primary/'official-floor-plan-2023.pdf.request.json',image]);primary_ref=dict(**request,sourcePath=str(pdf.relative_to(ROOT)),pageActuallyViewed=1,renderActuallyViewed=dict(path=str(image.relative_to(ROOT)),sha256=digest(image.read_bytes())),contextOnly=True,notSurveyedRegistration=True)
 metrics=[]
 for pair in PAIRS:
  uid,nuid=pair;file=uid.split('/')[1]+'--'+nuid.split('/')[1]+'--original.json.gz';contacts=take(P+'native-roles-v1-20261027',file);assert len(contacts)==PAIRS[pair]
  polygons=[shapely.Polygon(forms[u]['rings'][0],forms[u]['rings'][1:])for u in pair];assert all(p.is_valid for p in polygons)
  points=shapely.points([(float(F(p[0])),float(F(p[2])))for c in contacts for p in c['exactPoints']])
  metrics.append(dict(uid=uid,nativeUid=nuid,sourceLabel=forms[uid]['name'],nativeLabel=forms[nuid]['name'],originalContactCount=len(contacts),originalRoles=dict(Counter(c['contactRole']for c in contacts)),footprintOverlapM2=float(polygons[0].intersection(polygons[1]).area),maximumContactVertexDistanceToSourceBoundaryM=float(max(shapely.distance(points,polygons[0].boundary))),maximumContactVertexDistanceToNativeBoundaryM=float(max(shapely.distance(points,polygons[1].boundary))),footprintNumbersDiagnosticOnly=True,allFourWorlds=[r for r in roles if(r['uid'],r['nativeUid'])==pair]))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 review=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,retainedNativeEntries=entries,currentManifestSHA256=selection['manifestSHA256'],sourceSpecificArchitecturalInterfaceInterpretationAccepted=True,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,nativeMetadataChanges=0,physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,rawWarningsPreserved=True,primaryContext=primary_ref,imagesActuallyViewed=inspected,pairs=metrics,basis=[
 'The official operator floor plan shows Ocean Centre, Ocean Terminal, Gateway Arcade and Marco Polo Hongkong Hotel Arcade as adjoining shopping zones, with connecting circulation on Levels2/3. This is qualitative architectural context, not precise registration, source revision equivalence, legal ownership or a floor-by-floor geometric match.',
 'The complete original assembly and all four original/native junction plots were inspected. The contacts lie at the authored lower arcade boundaries and projecting connector/roof interfaces between these adjoining zones. They are not all subgrade and are not collision-clear. The separate upper Ocean Centre source has no contacts with these installed neighbours.',
 'The ground-footprint overlap is zero for both main-source joins and very small for the two companion joins; contact vertices also extend metres away from footprint boundaries. Thus a narrow coincident-wall or occupied-ground-footprint exemption would be inaccurate. The role accepted here is an original above-grade connecting arcade/overhang interface, including original shared-plane and transverse surfaces.',
 'All nine scoped source/native pairs retain their complete four-world classifications. Every represented transverse crossing has an original finite facet-pair contact; no untraced new facet-pair crossing is accepted. Original point-contact to represented crossing changes remain explicit. Corresponding vertex deltas are retained in the lineage receipt, not misreported as finite penetration depths.',
 'Accept only this bounded source-role interpretation for the four listed original junctions. It neither declares a universal acceptable overlap distance nor waives collision, source support, retained-terrain, source appearance, atomic fallback or publication checks. No meshes are welded, clipped, simplified, moved or rescaled.'],remaining=['Current original-source physical qualification, including exact five-face vertical-seam evidence and upper-source support paths','Fresh current-runtime desktop/mobile source and retained-native visuals, picking, collision, atomic group failure/retry','Separately guarded supported-coimport retained-terrain publication; no installed support metadata rewrite'])
 save(out/'ROOT-JUNCTION-ROLE-REVIEW.json',review);save(out/'primary-provenance.json',primary_ref)
 result=dict(uids=list(SOURCES),sourceSpecificArchitecturalInterfaceInterpretationAccepted=True,sourceSHA256ByUid=SOURCES,currentManifestSHA256=selection['manifestSHA256'],pairs=list(PAIRS),physicalAcceptance=False,visualAcceptance=False,installationApproved=False,primaryContextOnly=True)
 module('ocean_junction_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-harbour-city-native-junction-source-role-review-v1',refs,result)
if __name__=='__main__':main()
