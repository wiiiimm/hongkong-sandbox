"""Bounded independently owned five-source identity; no physical/runtime waivers.

All five current actors receive their own complete unchanged original. The
Miami OP family and distinct neighbouring permit are never merged as ownership.
Raw previous single/eight-source failures are preserved. The complete source
collection passes every current coverage/extent/foreign guard independently.
"""
import importlib.util,json,numpy as np,shapely
from run import ROOT,HERE,read,digest,connect,NATIVE_RUN
from original_source_ownership import document
from miami_original_yaw_root_20261009 import verify_original_root
from government_georef_cell_identity import geographic_cell
from georef_projection_coverage import whole_cell_coverage
DOC=ROOT/'docs/astra-city/government-import/government-xl-miami-five-grounded-originals-20261009'
UIDS={'landsd/232089:0','landsd/259038:0','landsd/202994:0','landsd/203433:0','landsd/231147:0'}
POLICY='exact-five-independent-original-miami-current-collection-v1'
def verify_collection():
 sel=read(DOC/'selection.json.gz');assert {r['uid'] for r in sel['rows']}==UIDS
 sourceinputs=read(DOC.parent/'government-xl-miami-nine-original-contact-20261009/all-original-source-contact-inputs.json.gz')
 provider=read(DOC.parent/'government-xl-miami-op-complete-family-20261009/fresh-nine-exact-provider-outlines.json')
 assert len(provider['features'])==9 and not provider.get('exceededTransferLimit')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';current={};allforms=[];tiles={}
 for tile in read(manifest)['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];forms=read(p)['buildings'];allforms+=forms
  for b in forms:
   if b['uid'] in UIDS:
    assert b['uid'] not in current;current[b['uid']]=b;tiles[tile['url']]=digest(p.read_bytes())
 assert set(current)==UIDS;tri=[];rows=[]
 spec=importlib.util.spec_from_file_location('miami_collection_original_decode',HERE/'xl-second-pass.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);d.LOCAL=HERE/'local/government-xl-miami-nine-original-source-foundation-20261009'
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in sel['rows']:
   assert r['source']['building']==current[r['uid']];assert digest((ROOT/'3d-viewer'/r['source']['tile']).read_bytes())==r['source']['tileSHA256'];raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256']==r['native']['model']['asset']['sha256'];assert r['candidate']['entry']['rootTranslation']==[-834500,0,816500]
   native=c.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone();assert native[0]==r['native']['resultSha'];assert [m for m in native[1]['models'] if m['modelId']==r['modelId']]==[r['native']['model']]
   b=current[r['uid']]
   for key in ['officialCandidates','officialMatches','viewerMatches']:
    matches=r['native']['model']['matching'][key];assert len(matches)==1 and matches[0]['buildingCSUID']==b['buildingCSUID'] and matches[0]['objectId']==b['objectId'];assert key!='viewerMatches' or matches[0]['uid']==r['uid']
   fresh=[f for f in provider['features'] if f['attributes']['BuildingCSUID']==b['buildingCSUID']];assert len(fresh)==1;attrs=fresh[0]['attributes'];assert str(attrs['GeoRefNo'])==r['modelId'][1:11] and attrs['Status']=='Active' and attrs['BuildingBlockType']==b['structureType'];fp=shapely.symmetric_difference_all([shapely.Polygon([(p[0]-834500,816500-p[1]) for p in ring]) for ring in fresh[0]['geometry']['rings']])
   r['triangles']=r['native']['model']['triangles'];t=d.glb_triangles(r);g=next(g for g in sourceinputs['rows'] if g['uid']==r['uid']);assert digest(t.astype('<f8').tobytes())==g['worldTriangleSHA256'];root=verify_original_root(raw,r,t);assert root['passed'];cell=geographic_cell(r['modelId'],b['buildingCSUID'],b['structureType']);projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));cp=whole_cell_coverage(t,cell,projection);assert cp['coversWholeCell'] and fp.covers(cell) and shapely.Polygon(b['rings'][0],b['rings'][1:]).covers(cell);tri.append(t);rows.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'worldTriangleSHA256':g['worldTriangleSHA256'],'completeSourceRoot':root,'wholeGeoRefCell':cp,'viewerObjectId':b['objectId'],'currentProviderObjectId':attrs['OBJECTID'],'providerIdentityRevisionExplicit':True,'exactCurrentCSUID':b['buildingCSUID'],'allOriginalFaces':len(t),'cachedMatchingPreserved':r['native']['model']['matching']})
 t=np.concatenate(tri);projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]));target=shapely.union_all([shapely.Polygon(current[u]['rings'][0],current[u]['rings'][1:]) for u in UIDS]);excess=projection.difference(target);other=[b for b in allforms if b['uid'] not in UIDS and shapely.Polygon(b['rings'][0],b['rings'][1:]).intersects(projection.envelope)];foreign=shapely.union_all([shapely.Polygon(b['rings'][0],b['rings'][1:]) for b in other]);coverage=projection.intersection(target).area/target.area;extent=float(shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),target).max());foreignarea=excess.intersection(foreign).area;assert coverage>=.95 and extent<=10 and foreignarea<=1
 return {'policy':POLICY,'rows':rows,'uids':sorted(UIDS),'coverage':coverage,'maximumExtentM':extent,'foreignExcessM2':foreignarea,'allOtherCurrentFormsRetained':other,'currentTargetTileSHA256s':tiles,'currentManifestSHA256':digest(manifest.read_bytes()),'distinctOwnershipGroups':[{'uids':sorted(UIDS-{'landsd/231147:0'}),'permits':['NT73/91','NT166/91']},{'uids':['landsd/231147:0'],'permits':['NT161/91']}],'sourceIdentityPassed':True,'physicalAccepted':False,'installationApproved':False,'geometryChanges':0,'qualification':'Identity only: exact complete individually named original roots/bytes and unique stable current identities, original authored horizontal yaw explicitly preserved, whole source/current/provider cells, complete current collection spatial guards and all foreign actors. Distinct permits not merged. Full physical/external interfaces and runtime/publication remain independent.'}

def verify_files(row,context,local):
 """Fresh source-bound adapter for the existing independent physical pipeline."""
 proof=verify_collection();item=next(r for r in proof['rows'] if r['uid']==row['uid']);assert row['uid'] in UIDS and row['sourceSHA256']==item['sourceSHA256'];assert context['sourceSHA256']==row['sourceSHA256'];assert digest((ROOT/row['candidate']['path']).read_bytes())==item['sourceSHA256']
 assert context['neighbourTileHashes'] and all(digest((ROOT/'3d-viewer'/u).read_bytes())==sha for u,sha in context['neighbourTileHashes'].items())
 return {'policy':POLICY,'uid':row['uid'],'sourceSHA256':item['sourceSHA256'],'passed':True,'reasons':[],'proof':{'exactObjectId':True,'exactBuildingCSUID':True,'uniqueViewerMatch':True,'identityAccepted':True},'completeIndependentCollection':proof,'sourceIdentityRow':item,'installationApproved':False,'sourceGeometryChanges':0}
