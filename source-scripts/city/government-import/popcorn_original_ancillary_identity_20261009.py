"""Exact-source-only PopCorn ancillary stair identity contract, independent physical gates.

Original geometry is retained. A source-specific typed visible stair role accounts
for extent outside the basic GIS body; no generic distance padding is allowed.
"""
import importlib.util,numpy as np,shapely
from run import ROOT,HERE,read,digest
POLICY='popcorn-exact-original-two-ancillary-stairs-v1'
DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-access-ownership-20261009'
PAIR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-complete-original-current-pair-20261009'
PINS={'landsd/295538:0':('B447991877202063C0','9dc37f891dc96d8ce8be29da04138e347e7bea4924f7e709e793ad3495ac539f','70cd147ff3c2a8eca67bf96993695af399ff974022e3d4580990bca816e6262f'),'landsd/295539:0':('B448271874701063C0','6c7cc6eece6fd000ddfb6735f537841477a8ae44767aa98e410ab7de09348bdf','8e5e71a8a853e73e0a2e0b84b96ae2b429a99911fde4344eb5c4ba75ddf5e392')}
def verify_collection():
 lineage=read(ROOT/'docs/astra-city/government-import/government-xl-popcorn-current-gltf-source-lineage-20261009/fresh-current-source-asset-lineage.json');assert len(lineage['rows'])==2
 for row in lineage['rows']:
  mid,sha,worldsha=PINS[row['uid']];assert row['modelId']==mid and row['freshCurrentNativeSourceSHA256']==sha and row['currentSourceHashUnchanged'] and digest((ROOT/row['assetPath']).read_bytes())==sha
 fresh_measures=read(DOC/'fresh-current-provider-complete-collection-measures.json');assert fresh_measures['fullOriginalCoverageOfFreshCurrentProviderTarget']>=.95 and all(r['sourceProjectionCoversWholeCell'] and r['freshCurrentProviderFootprintCoversWholeCell'] for r in fresh_measures['rows'])
 proposal=read(DOC/'source-bound-ancillary-step-identity-proposal.json.gz');attachments=read(DOC/'every-far-access-component-exact-attachments.json.gz');fresh=read(DOC/'current-exact-source-and-retained-forms.json.gz');selection=read(PAIR/'selection.json.gz');assert {r['uid'] for r in selection['rows']}==set(PINS)
 spec=importlib.util.spec_from_file_location('popcorn_contract_decoder',HERE/'xl-second-pass.py');decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder);decoder.LOCAL=HERE/'local/government-xl-popcorn-complete-original-current-pair-20261009';tri=[];forms=[]
 for row in selection['rows']:
  uid=row['uid'];mid,sha,worldsha=PINS[uid];assert row['modelId']==mid and row['sourceSHA256']==sha and digest((ROOT/row['candidate']['path']).read_bytes())==sha
  assert digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())==row['source']['tileSHA256'];current=next(r for r in fresh['rows'] if r['uid']==uid);assert row['source']['building']==current['currentViewerForm'];assert current['sameGeoRefNo'] and current['sameCurrentActiveSubtype'];assert current['exactBuildingCSUID']==row['candidate']['entry']['buildingCSUID'];row['triangles']=row['native']['model']['triangles'];t=decoder.glb_triangles(row);assert digest(t.astype('<f8').tobytes())==worldsha;tri.append(t);b=row['source']['building'];forms.append(shapely.Polygon(b['rings'][0],b['rings'][1:]))
 target=shapely.union_all(forms);full=np.concatenate(tri);projection=shapely.union_all(shapely.polygons(full[:,:,[0,2]]));coverage=projection.intersection(target).area/target.area;assert coverage>=.95
 roles=proposal['rows'];assert len(roles)==2;roleids=[r['everyFarOriginalFaceIndex'] for r in roles];ids=np.concatenate([np.array(x) for x in roleids]);assert len(ids)==len(set(ids.tolist()))==311;actual=np.flatnonzero((shapely.distance(shapely.points(tri[0][:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3)>10).any(axis=1));assert set(actual.tolist())==set(ids.tolist())
 accounted=set(f for r in attachments['mainBodyFarFacesByRole'] for f in r['faceIndices'])|set(f for r in attachments['separateOriginalSourceComponents'] for f in r['farOriginalFaceIndices']);assert accounted==set(ids.tolist())
 allfar=shapely.union_all(shapely.polygons(tri[0][actual][:,:,[0,2]]));polys=[a for a in ([allfar] if allfar.geom_type=='Polygon' else allfar.geoms) if a.geom_type=='Polygon'];polys.sort(key=lambda p:-p.area);assert len(polys)==2
 for role,exact in zip(roles,polys):
  p=shapely.geometry.shape(role['originalProjectedGeometry']);assert exact.equals(p);assert role['matchedStepLineCount']>=10
 assert all(c['wholeCellInsideOriginalProjection'] and c['wholeCellInsideExactTarget'] for c in proposal['allOriginalGeoRefCells']);raw=proposal['rawCompleteMeasures'];assert raw['unrelatedExcessOverlapM2']<=1 and abs(coverage-raw['targetCoverage'])<1e-12;assert raw['maximumExtentM']>23
 # Preserve every unrelated current form; shared OSM ancestry cannot imply vertical coverage.
 retained=fresh['retained15Forms'];assert len(retained)==15;assert all(b['uid'] not in PINS for b in retained);assert fresh['exactOnlyTwoSourceTarget']['excessRetained15FormOverlapM2']==0
 expected={b['uid']:b for b in retained};actual_retained={};retained_tiles={}
 for tile in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];found=[b for b in read(path)['buildings'] if b['uid'] in expected]
  if found:retained_tiles[tile['url']]=digest(path.read_bytes());actual_retained.update({b['uid']:b for b in found})
 assert actual_retained==expected
 unproved=[r['component'] for r in attachments['separateOriginalSourceComponents'] if not r['exactDirectMainBodyContact'] and not r.get('exactContactToOtherOriginalComponent')]
 return {'policy':POLICY,'identityAccepted':True,'sourceIdentityReviewed':True,'sourceIdentityReviewUsedAI':True,'sourceSpecificAncillaryRoleFaces':roleids,'sourceSpecificAncillaryRolePolygons':[r['originalProjectedGeometry'] for r in roles],'completeOriginalCells':proposal['allOriginalGeoRefCells'],'rawCompleteMeasures':raw,'freshCurrentProviderCollectionMeasures':fresh_measures,'freshCurrentNativeArchiveLineage':lineage,'bodyExtentMaximumM':10,'rawGISMaximumExtentIsPreserved':True,'originalUnprovedAttachmentComponents':unproved,'currentProviderRevisionDifferences':[{'uid':r['uid'],'providerObjectId':r['currentProviderObjectId'],'viewerObjectId':r['viewerObjectId'],'boundaryHausdorffM':r['hausdorffDistanceM'],'symmetricDifferenceM2':r['symmetricDifferenceM2']} for r in fresh['rows']],'retainedOtherFormUids':[b['uid'] for b in retained],'retainedOtherTileSHA256s':retained_tiles,'sourceGeometryChanges':0,'installationApproved':False,'physicalAcceptance':False,'runtimeAccepted':False,'qualification':'Source identity interpretation only for the two pinned original models. Exact original stair surfaces account for raw GIS extent and remain fully rendered; no generic spatial padding or hidden faces. Physical attachment/terrain/support, current runtime source footprint, all retained forms, staged/live browser and fenced publication remain independent and mandatory.'}
if __name__=='__main__':
 from run import save
 p=verify_collection();save(DOC/'deterministic-source-bound-identity-contract.json.gz',p);print({k:p[k] for k in ['policy','identityAccepted','rawCompleteMeasures','originalUnprovedAttachmentComponents','retainedOtherFormUids']},flush=True)
