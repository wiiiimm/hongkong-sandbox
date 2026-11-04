"""Fresh full original source-local terrain/foundation diagnostics, no acceptance or edits."""
import sys,json,uuid,importlib.util,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from terrain_source_preflight import SourceSheetIndex
BATCH='government-xl-popcorn-complete-original-source-terrain-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;PAIR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-complete-original-current-pair-20261009'
def module(name,filename):
 sp=importlib.util.spec_from_file_location(name,HERE/filename);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not (DOC/'result.json').exists();selection=read(PAIR/'selection.json.gz');uidset={r['uid'] for r in selection['rows']};manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes())
 for r in selection['rows']:assert digest((ROOT/r['candidate']['path']).read_bytes())==r['sourceSHA256'];assert digest((ROOT/'3d-viewer'/r['source']['tile']).read_bytes())==r['source']['tileSHA256']
 claim=reservations.claim('popcorn-source-terrain-'+str(uuid.uuid4()),['building:'+u for u in sorted(uidset)]+['terrain-patch:'+u for u in sorted(uidset)],batch=BATCH,ttl=1800);assert claim['ok'],claim;lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:
  index=SourceSheetIndex(read(ROOT/'source-scripts/city/landmark-acquisition/index.json'));sheets=sorted({x['sheet'] for r in selection['rows'] for x in index.covering_sheets(r['native']['model']['worldBounds'])});recovery=module('popcorn_source_terrain','xl-routed-cell-indexed-terrain-continuation.py');second=module('popcorn_triangle_decode','xl-second-pass.py');second.LOCAL=HERE/'local/government-xl-popcorn-complete-original-current-pair-20261009';final=module('popcorn_full_foundation','xl-final-script-pass.py');terrain=[];sources=[]
  for sheet in sheets:
   folder,proof=recovery.terrain_sheet(sheet,LOCAL);paths=sorted((folder/'terrain').rglob('*.gltf'));assert paths
   for p in paths:terrain.append(second.terrain_triangles(p))
   proof['terrainPaths']=[str(p.relative_to(ROOT)) for p in paths];sources.append(proof)
  terrain=np.concatenate(terrain);out=[]
  for r in selection['rows']:
   r['triangles']=r['native']['model']['triangles'];tri=second.glb_triangles(r);b=r['source']['building'];target=shapely.Polygon(b['rings'][0],b['rings'][1:]);metrics=final.foundation_context(tri,terrain,target);out.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'allOriginalTriangles':len(tri),'foundation':metrics,'strictRawFoundationDiagnosticPass':metrics['completeTerrainTriangles']==len(tri) and metrics['fullyBuriedUpwardTriangles']==0 and metrics['fullyBuriedAreaFraction']<=.001,'identityAccepted':False,'installationApproved':False});print({'uid':r['uid'],'foundation':{k:v for k,v in metrics.items() if k!='components'}},flush=True)
  save(DOC/'all-original-source-terrain-foundation.json.gz',{'rows':out,'sourceSheets':sources,'terrainOriginalTriangles':len(terrain),'currentManifestSHA256':mh,'sourceGeometryChanges':0,'terrainGeometryChanges':0,'installationApproved':False});paths=[p for p in DOC.rglob('*') if p.is_file()]+[PAIR/'selection.json.gz',PAIR/'independent-native-fbx-collection-check.json',PAIR/'exact-only-two-source-target-context.json.gz',manifest,HERE/'xl-popcorn-complete-original-source-terrain-20261009.py',HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py',HERE/'xl-routed-cell-indexed-terrain-continuation.py']+[ROOT/r['candidate']['path'] for r in selection['rows']]+[ROOT/'3d-viewer'/r['source']['tile'] for r in selection['rows']]
  for source in sources:
   base=ROOT/source['cache'];paths+=[base/'original/download.json',base/'directory/result.json']+[base/'terrain'/f['name'] for f in source['terrainFiles']]
  refs=[ref(p) for p in sorted(set(paths))];stage='full-original-source-local-terrain-foundation-v1';payload={'uids':sorted(uidset),'evidenceRefs':refs};jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
  result={**payload,'jobId':jid,'batch':BATCH,'rows':out,'installationApproved':False,'identityAccepted':False,'scriptFullAcceptancePassed':False,'newlyInstalled':0,'publication':False,'geometryChanges':0,'aiGeometryModelling':False,'scriptExternalAICalls':0,'qualification':'Fresh whole original source terrain/foundation diagnostic. Raw spatial extent/access role still independently reviewed; whole pair source-local support/contact/runtime/browser gates remain. No edited mesh/pose/terrain or hidden faces.'}
  with connect() as c:
   c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
   for x in refs:assert ref(ROOT/x['path'])==x
   assert digest(manifest.read_bytes())==mh
   assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print({'jobId':jid,'rawFoundationPasses':sum(r['strictRawFoundationDiagnosticPass'] for r in out),'neonVerified':True},flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
