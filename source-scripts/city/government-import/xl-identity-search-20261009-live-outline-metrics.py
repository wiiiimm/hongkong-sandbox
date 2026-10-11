"""Measure freshly changed provider polygons against complete unchanged originals.
Diagnostic only; no footprint, source or acceptance changes.
"""
import sys,importlib.util,uuid,shutil,json
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from government_georef_cell_identity import geographic_cell
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009'
LOCAL=HERE/'local/government-xl-identity-search-20261009/live-outline-metrics'
def module(n,file):
 s=importlib.util.spec_from_file_location(n,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 rows=[r for r in read(DOC/'live-georef-research.json.gz')['rows'] if any(c.get('hausdorffDistanceM',0)>.002 for c in r['officialCandidates'])]
 assert len(rows)==20;claim=reservations.claim('xl-identity-live-outline-'+str(uuid.uuid4()),['native-model:'+r['sourceKey'] for r in rows],batch='government-xl-identity-search-20261009',ttl=1800);assert claim['ok'],claim
 lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');native={k+'/'+m['modelId']:m for k,m in c.execute("SELECT cache_key,m FROM astra_modelling.native_stage_results,LATERAL jsonb_array_elements(result->'models') m WHERE cache_key=ANY(%s) AND m->>'modelId'=ANY(%s)",(list({r['sourceKey'].split('/')[0] for r in rows}),[r['modelId'] for r in rows])).fetchall()}
  cache={p.name[:-7]:p for p in (HERE/'local').rglob('*.glb.gz')};decoder=module('fresh_outline_decode','xl-second-pass.py');decoder.LOCAL=LOCAL;final=module('fresh_outline_forms','xl-final-script-pass.py');out=[]
  for r in rows:
   m=native[r['sourceKey']];sha=r['sourceSHA256'];p=cache[sha];assert digest(p.read_bytes())==sha
   asset=LOCAL/'assets'/(sha+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,asset)
   tri=decoder.glb_triangles({'sourceSHA256':sha,'modelId':r['modelId'],'triangles':m['triangles'],'native':{'model':m}});projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));lo,hi=m['worldBounds'];forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);b=next(b for b,_,_ in forms if b['uid']==r['uid']);old=Polygon(b['rings'][0],b['rings'][1:]);fresh=next(c for c in r['officialCandidates'] if c['sourceCurrentExactCSUIDMatches'] and c['sourceTypeMatches']);rings=fresh['officialRings'];new=Polygon(rings[0],rings[1:]);others=shapely.union_all([shape for x,shape,_ in forms if x['uid']!=r['uid']]);cell=geographic_cell(r['modelId'],b['buildingCSUID'],b['structureType'])
   def metrics(shape):
    return {'targetCoverage':float(shape.intersection(projection).area/shape.area),'maximumSourceExtentM':float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),shape).max()),'unrelatedExcessOverlapM2':float(projection.difference(shape).intersection(others).area),'targetWholeCell':bool(shape.covers(cell)),'sourceWholeCell':bool(projection.covers(cell))}
   before=metrics(old);after=metrics(new);passed=lambda x:x['targetCoverage']>=.95 and x['maximumSourceExtentM']<=10 and x['unrelatedExcessOverlapM2']<=1 and x['targetWholeCell'] and x['sourceWholeCell'];item={k:r[k] for k in ('uid','sourceKey','sourceSHA256','modelId')};item.update(name=fresh['attributes']['BuildingNameEN'],previous=before,currentOfficial=after,previousBoundsPass=passed(before),currentOfficialBoundsPass=passed(after),newPositiveCandidate=not passed(before) and passed(after),worldTrianglesSHA256=digest(tri.astype('<f8').tobytes()),originalPath=str(p.relative_to(ROOT)),officialCSUID=fresh['attributes']['BuildingCSUID'],officialObjectId=fresh['attributes']['OBJECTID'],identityAccepted=False,installationApproved=False);out.append(item);save(DOC/'live-outline-metrics-progress.json',{'checked':len(out),'total':20});print(json.dumps({'uid':r['uid'],'newPositive':item['newPositiveCandidate'],'before':before,'after':after}),flush=True)
  save(DOC/'live-outline-metrics.json.gz',{'rows':out,'qualification':'Fresh current provider polygon alternatives measured without changing retained source or viewer form. Full unchanged source projection and all vertices, coverage>=.95, extent<=10m, unrelated overlap<=1m² and whole one-metre GeoRef cell retained. Diagnostic positives would require separately pinned source revision identity/physical acceptance.'})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
