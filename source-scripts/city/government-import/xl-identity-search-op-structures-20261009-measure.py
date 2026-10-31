"""Measure unchanged originals against explicit provider occupation-structure groups.
No existing forms removed, no source pose/geometry/ownership acceptance modified.
"""
import importlib.util,sys,json,uuid,shutil
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from original_source_ownership import graph_reasons,document
from government_georef_cell_identity import geographic_cell
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-op-structures-20261009';LOCAL=HERE/'local/government-xl-identity-search-op-structures-20261009'
def module(n,file):
 s=importlib.util.spec_from_file_location(n,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 rows=[r for r in read(DOC/'official-op-relationship-research.json.gz')['rows'] if r['candidateForFullOriginalDiagnostic']];assert len(rows)==12;claim=reservations.claim('xl-official-op-measure-'+str(uuid.uuid4()),['native-model:'+r['sourceKey'] for r in rows],batch='government-xl-identity-search-op-structures-20261009',ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');native={k+'/'+m['modelId']:m for k,m in c.execute("SELECT cache_key,m FROM astra_modelling.native_stage_results,LATERAL jsonb_array_elements(result->'models') m WHERE cache_key=ANY(%s) AND m->>'modelId'=ANY(%s)",(list({r['sourceKey'].split('/')[0] for r in rows}),[r['modelId'] for r in rows])).fetchall()}
  cache={p.name[:-7]:p for p in (HERE/'local').rglob('*.glb.gz')};decoder=module('op_unchanged_original_decode','xl-second-pass.py');decoder.LOCAL=LOCAL;final=module('op_current_forms','xl-final-script-pass.py');out=[];tiles={}
  for r in rows:
   m=native[r['sourceKey']];sha=r['sourceSHA256'];p=cache[sha];raw=p.read_bytes();assert digest(raw)==sha==m['asset']['sha256'];asset=LOCAL/'assets'/(sha+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,asset)
   tri=decoder.glb_triangles({'sourceSHA256':sha,'modelId':r['modelId'],'triangles':m['triangles'],'native':{'model':m}});projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));lo,hi=m['worldBounds'];forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);target=next(b for b,_,_ in forms if b['uid']==r['uid']);group=r['currentGroupForms'];assert r['uid'] in {b['uid'] for b in group}
   for b,_,tile in forms:tiles[tile]=digest((ROOT/'3d-viewer'/tile).read_bytes())
   # Complete provider relationship group retained even when outside mesh bounds.
   for tile in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
    if any(b['uid'] in {g['uid'] for g in group} for b in read(ROOT/'3d-viewer'/tile['url'])['buildings']):tiles[tile['url']]=digest((ROOT/'3d-viewer'/tile['url']).read_bytes())
   for g in group:
    match=next((b for b,_,_ in forms if b['uid']==g['uid']),None)
    if match is not None:assert match==g
   groupuids={b['uid'] for b in group};shape=shapely.union_all([Polygon(b['rings'][0],b['rings'][1:]) for b in group]);others=shapely.union_all([s for b,s,_ in forms if b['uid'] not in groupuids]);cell=geographic_cell(r['modelId'],target['buildingCSUID'],target['structureType']);measures={'targetCoveredBySourceProjection':float(shape.intersection(projection).area/shape.area),'sourceExcessMaximumDistanceFromTargetM':float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),shape).max()),'sourceExcessCoveredByUnrelatedFormsM2':float(projection.difference(shape).intersection(others).area),'originalTargetCoversWholeGeoRefCell':bool(Polygon(target['rings'][0],target['rings'][1:]).covers(cell)),'originalSourceCoversWholeGeoRefCell':bool(projection.covers(cell))}
   reasons=graph_reasons(document(raw),r['modelId'],m['triangles'])
   if measures['targetCoveredBySourceProjection']<.95:reasons.append('provider-complete-structure-coverage-below-0.95')
   if measures['sourceExcessMaximumDistanceFromTargetM']>10:reasons.append('provider-complete-structure-extent-over-10m')
   if measures['sourceExcessCoveredByUnrelatedFormsM2']>1:reasons.append('provider-complete-structure-unrelated-overlap-over-1m2')
   if not measures['originalTargetCoversWholeGeoRefCell']:reasons.append('original-target-whole-georef-cell')
   if not measures['originalSourceCoversWholeGeoRefCell']:reasons.append('original-source-whole-georef-cell')
   item={k:r[k] for k in ('uid','sourceKey','sourceSHA256','modelId','structureIds','relatedCSUIDs','opStructureDetails','additionalBeyondDirectOSMUids')};item.update(name=target.get('name'),groupForms=group,measures=measures,reasons=sorted(set(reasons)),diagnosticCandidate=not reasons,identityAccepted=False,installationApproved=False,originalPath=str(p.relative_to(ROOT)),originalSourceFileSHA256=digest(raw),worldTrianglesSHA256=digest(tri.astype('<f8').tobytes()),modelGeometryChanges=0);out.append(item);save(DOC/'measure-progress.json',{'checked':len(out),'total':12});print(json.dumps({'uid':r['uid'],'name':target.get('name'),'candidate':not reasons,'measures':measures,'reasons':reasons}),flush=True)
  for tile,h in tiles.items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==h
  save(DOC/'full-original-op-group-measures.json.gz',{'rows':out,'sourceTileHashes':tiles,'qualification':'Complete provider BuildingCSUID↔BuildingStructureID relationship groups, all unchanged originals/poses, every surrounding form retained. Full projected triangles/vertices and strict existing identity bounds. A diagnostic positive needs dedicated official ownership policy and fresh physical/neighbour/runtime/browser acceptance; no model/source/manifest changes.'})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
