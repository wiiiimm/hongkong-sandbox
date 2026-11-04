"""Exact source-specific western-pier review; no approval for the eastern component."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
P='government-xl-disneyland-piers-after-passenger-';BATCH=P+'75642-independent-source-review-v1-20261030';UID='landsd/75642:0';SHA='49cdebceca290d6ceccf3e1891546efbafa28218ae144da7c389190773c302c0'
def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not(out/'result.json').exists();refs=[Path(__file__)];pins={}
 def take(s,n):
  b=base/(P+s)
  if s not in pins:pins[s]=authenticate(b)[1];refs.append(b/'result.json')
  p=b/n;assert digest(p.read_bytes())==pins[s][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 preview='75642-independent-private-preview-v1-20261030';selection=take('all-basic-fallback-patch-runtime-v2-20261030','selection.json.gz');row=next(r for r in selection['rows']if r['uid']==UID);assert row['sourceSHA256']==SHA
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
 cover=take('75642-fallback-lower-face-cover-v1-20261030','summary.json');assert cover['allResidualFacetsCovered']and not cover['failures']and len(cover['rows'])==104 and cover['sourceSHA256']==SHA
 foundations=take('75642-all-basic-fallback-foundations-v2-20261030','summary.json');assert len(foundations['rows'])==4 and all(r['fullyBuriedUpwardTriangles']==0 and r['completeTerrainTriangles']==18007 and r['fullyBuriedTriangles']==26 for r in foundations['rows'])
 checks=take('all-basic-fallback-form-checks-v2-20261030','neighbour-checks.json');assert len(checks['rows'])==5 and all(not r['reasons']for r in checks['rows'])
 foreign=take('joint-foreign-contacts-v1-20261030','summary.json');pairs=[r for r in foreign['rows']if r['uid']==UID];assert {r['foreignUid']for r in pairs}=={'way/334029318:0','landsd/75643:0'};assert all(m['allFiniteContactPairs']==0 for r in pairs for m in r['modes'])
 scope=take('joint-model-scope-v1-20261030','summary.json');assert not next(r for r in scope['rows']if r['uid']==UID)['nearbyNativeActors']
 for s in ['all-basic-osm-complete-ground-v2-20261030','all-basic-75642-complete-ground-v2-20261030','all-basic-75643-complete-ground-v2-20261030']:
  d=take(s,'summary.json');assert d['completeOverlayUncoveredAreaM2']==0 and d['completeOverlayMaximumAbsoluteGroundChangeM']<.000033
 take('primary-imagery-v1-20261030','provenance.json')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 images=[];reports=[]
 for v in ['390','1280']:
  p=base/(P+preview)/v/'staged-browser.json';r=take(preview,v+'/staged-browser.json');assert r['passed']and not r['errors'];reports.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
  for hour in ['1500','2200']:
   p=base/(P+preview)/v/('staged-landsd-75642-0-'+v+'-'+hour+'-canvas.png');assert p.exists();refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 identity=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True)
 physical=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},sourceSpecificPhysicalInterpretationAccepted=True,completeFourWorldFoundations=True,ordinaryBurialPolicyPassed=False,rawNumericalFailuresPreserved=True,completeCurrentNeighbourChecks=5,identityProof=identity,leaseResources=['building:landsd/75642:0','building:landsd/75643:0','building:landsd/74189:0','building:landsd/236354:0','source-form:way/334029318:0','terrain:city/data/terrain.json','server:127.0.0.1:4177'],sourceGeometryChanges=0,sourcePoseChanges=0,retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],interpretation='Only the exact western pier original: all26 residual facets lie below2.505m and have strict continuous actual-ground cover in every source stream; all upward facets remain unburied. These are lower supporting/deck-underside interfaces, below the visible pier deck. ROOT reviewed the independent original in four actual390/1280day/night exports and its unfitted official aerial correspondence. Raw0.001799buried-area fraction remains false under the generic policy; this is bounded physical source interpretation, not a threshold waiver. The separate eastern original is not installed or approved by this review. Both the OSM structure and eastern BASIC remain unchanged with preserved current ground; western original has zero finite contacts with either.',installationApproved=False)
 save(out/'ROOT-PHYSICAL-REVIEW.json',physical)
 review=dict(**physical,identityAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),imagesActuallyViewed=images,browserReports=reports,terrainEdits=True,publication=False,qualification='Eligible for guarded dry-run staging of this exact original only. Full publisher/support/ledger/lifecycle/current-readback gates remain. No approval or suppression of the disputed OSM shape.')
 save(out/'ROOT-SOURCE-REVIEW.json',review);refs += [out/'ROOT-PHYSICAL-REVIEW.json',out/'ROOT-SOURCE-REVIEW.json'];module('western_pier_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-independent-western-pier-source-physical-and-visual-review',refs,review)
if __name__=='__main__':main()
