"""Exact two-source identity with one explicit independently proved related podium.

Only the named original podium is classified as related. Its current primitive
is retained and still undergoes collision/terrain/coverage/runtime checks. The
raw numeric excess is retained; every other actor remains unrelated, including
same-name or same-permit actors. This is an identity contract, not full acceptance.
"""
import numpy as np,shapely
from run import ROOT,read,digest
from miami_independent_original_collection_20261009 import verify_collection as verify_five
UIDS={'landsd/202994:0','landsd/203433:0'}
RELATED='landsd/232089:0'
POLICY='exact-miami-two-original-grounded-towers-explicit-original-podium-identity-v1'
DOC=ROOT/'docs/astra-city/government-import/government-xl-miami-two-related-podium-identity-20261009'
def verify_collection():
 five=verify_five();primary=read(DOC/'related-podium-provider-context.json.gz');assert set(primary['uids'])==UIDS|{RELATED}
 for p in primary['inputHashes']:assert digest((ROOT/p['path']).read_bytes())==p['sha256']
 exact={'landsd/202994:0':('1485725911T20050430',{'NT73/91'}),'landsd/203433:0':('1496925881T20050430',{'NT166/91'}),RELATED:('1484725876P20060311',{'NT73/91','NT166/91'})}
 for r in primary['rows']:
  csuid,expected=exact[r['uid']];features=r['provider']['features'];assert len(features)==1 and features[0]['attributes']['BuildingCSUID']==csuid and features[0]['attributes']['Status']=='Active';assert {f['attributes']['OPNo'] for f in r['opStructures']['features']}==expected
  assert {f['attributes']['BuildingStructureID'] for f in r['opRelations']['features']}=={f['attributes']['BuildingStructureID'] for f in r['opStructures']['features']};assert all(f['attributes']['OPBlockType']==('Podium' if r['uid']==RELATED else 'Tower') for f in r['opStructures']['features'])
 allrows=read(DOC.parent/'government-xl-miami-five-grounded-originals-20261009/selection.json.gz')['rows'];inp=read(DOC.parent/'government-xl-miami-nine-original-contact-20261009/all-original-source-contact-inputs.json.gz');byuid={r['uid']:r for r in inp['rows']};geoms={};records=[]
 for uid in sorted(UIDS|{RELATED}):
  row=next(r for r in allrows if r['uid']==uid);proof=next(r for r in five['rows'] if r['uid']==uid);assert row['sourceSHA256']==proof['sourceSHA256'];assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256'];g=byuid[uid];t=np.asarray(g['position'],float).reshape(-1,3,3);assert digest(t.astype('<f8').tobytes())==proof['worldTriangleSHA256']==g['worldTriangleSHA256'];geoms[uid]=t;records.append(proof)
 assert next(r for r in allrows if r['uid']==RELATED)['modelId']=='B148472587602062G0'
 candidates=[r for r in allrows if r['uid'] in UIDS];t=np.concatenate([geoms[r['uid']] for r in candidates]);p=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));target=shapely.union_all([shapely.Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:]) for r in candidates]);excess=p.difference(target)
 currentothers=five['allOtherCurrentFormsRetained']+[r['source']['building'] for r in allrows if r['uid'] not in UIDS];assert len({b['uid'] for b in currentothers})==len(currentothers);other=[b for b in currentothers if b['uid']!=RELATED];foreign=shapely.union_all([shapely.Polygon(b['rings'][0],b['rings'][1:]) for b in other]);related=next(b for b in currentothers if b['uid']==RELATED);assert related['buildingCSUID']==exact[RELATED][0] and related['structureType']=='Podium';coverage=p.intersection(target).area/target.area;extent=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),target).max());foreignarea=excess.intersection(foreign).area;assert coverage>=.95 and extent<=10 and foreignarea<=1
 overlaps=[]
 for r in candidates:
  q=shapely.union_all(shapely.polygons(geoms[r['uid']][:,:,[0,2]]));own=shapely.Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:]);rp=shapely.Polygon(related['rings'][0],related['rings'][1:]);actual=shapely.union_all(shapely.polygons(geoms[RELATED][:,:,[0,2]]));overlaps.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'rawCurrentRelatedPodiumExcessM2':q.difference(own).intersection(rp).area,'actualWholeOriginalPodiumProjectionOverlapM2':q.intersection(actual).area,'currentPodiumCollisionExemption':False,'currentPodiumTerrainExemption':False})
 return {'policy':POLICY,'uids':sorted(UIDS),'sourceRows':[r for r in records if r['uid'] in UIDS],'relatedOriginalPodiumSource':next(r for r in records if r['uid']==RELATED),'explicitRelatedUID':RELATED,'explicitCurrentRelatedForm':related,'primaryProviderContextSHA256':digest((DOC/'related-podium-provider-context.json.gz').read_bytes()),'wholeTargetCoverage':coverage,'maximumFullSourceExtentM':extent,'unrelatedExcessM2':foreignarea,'rawRelatedExcessOverlaps':overlaps,'allOtherCurrentFormsRetained':currentothers,'currentManifestSHA256':five['currentManifestSHA256'],'wholeFiveCurrentEvidence':five,'identityAccepted':True,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0,'qualification':'Two independently grounded individually named complete original towers; sole explicitly related original podium has exact primary OP and complete source/root/GeoRef identity proof. Every other actor remains unrelated, even if names/permits coincide. No current primitive suppression, collision, runtime coverage, terrain or physical gate exemption.'}
def verify_files(row,context,local):
 proof=verify_collection();assert row['uid'] in UIDS;item=next(r for r in proof['sourceRows'] if r['uid']==row['uid']);assert row['sourceSHA256']==context['sourceSHA256']==item['sourceSHA256'];assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256'];assert all(digest((ROOT/'3d-viewer'/u).read_bytes())==s for u,s in context['neighbourTileHashes'].items())
 return {'policy':POLICY,'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'passed':True,'reasons':[],'proof':{'exactObjectId':True,'exactBuildingCSUID':True,'uniqueViewerMatch':True,'identityAccepted':True},'currentOriginalSourceIdentity':proof,'physicalAccepted':False,'installationApproved':False,'sourceGeometryChanges':0}
