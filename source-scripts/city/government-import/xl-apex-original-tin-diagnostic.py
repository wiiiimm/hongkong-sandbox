"""Measure The Apex's unchanged original against all indexed government TIN sheets.

Read-only source diagnostic. No acceptance, suppression, model or viewer edits.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations,connect,jobs,Jsonb,dict_row
from terrain_source_preflight import SourceSheetIndex
BATCH='government-xl-apex-complete-original-tin-diagnostic-20261008'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
UID='landsd/227942:0'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 source=ROOT/'docs/astra-city/government-import/government-xl-22-complete-group-official-context-v2-20261008/physical-selection.json.gz'
 row=next(r for r in read(source)['rows'] if r['uid']==UID)
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
 dest=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 decoder=module('apex_original_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL
 model=decoder.glb_triangles(row)
 models=LOCAL/'original-model.json.gz';save(models,{'rows':[{'uid':UID,'triangles':model.tolist(),'worldBounds':row['native']['model']['worldBounds'],'sourceSHA256':row['sourceSHA256'],'worldTrianglesSHA256':digest(model.astype('<f8').tobytes())}]})
 index=SourceSheetIndex(read(ROOT/'source-scripts/city/landmark-acquisition/index.json'));route=module('apex_indexed_original_terrain','xl-routed-cell-indexed-terrain-continuation.py')
 sheets=index.covering_sheets(row['native']['model']['worldBounds']);pieces=[];proofs=[];inputs=[ref(source),ref(ROOT/row['candidate']['path']),ref(Path(__file__))]
 for sheet in sheets:
  folder,proof=route.terrain_sheet(sheet['sheet'],LOCAL);proofs.append(proof)
  for p in sorted((folder/'terrain').rglob('*.gltf')):
   pieces.append(decoder.terrain_triangles(p));inputs.append(ref(p))
 tri=np.concatenate(pieces);lo,hi=row['native']['model']['worldBounds']
 tri=tri[(tri[:,:,0].max(axis=1)>=lo[0]-5)&(tri[:,:,0].min(axis=1)<=hi[0]+5)&(tri[:,:,2].max(axis=1)>=lo[2]-5)&(tri[:,:,2].min(axis=1)<=hi[2]+5)]
 terrains=LOCAL/'original-terrain.json.gz';save(terrains,{'rows':[{'uid':UID,'terrainTriangles':tri.tolist()}]})
 save(DOC/'source-context.json',{'uid':UID,'sheets':sheets,'sourceProofs':proofs,'terrainTriangles':len(tri),'sourceGeometryChanges':0})
 output=DOC/'clearance.json'
 subprocess.run(['node',str(HERE/'original-terrain-clearance-diagnostic.mjs'),str(models.relative_to(ROOT)),str(terrains.relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT,check=True)
 clearance=read(output);inputs.extend(ref(p) for p in [models,terrains,output,DOC/'source-context.json'])
 inputs.extend({'path':p,'sha256':sha} for p,sha in clearance['inputHashes'].items());inputs=list({r['path']:r for r in inputs}.values())
 payload={'uid':UID,'sourceSHA256':row['sourceSHA256'],'evidenceRefs':inputs};stage='unchanged-original-complete-tin-clearance-diagnostic-v1';jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 measured=clearance['rows'][0]
 result={**payload,'jobId':jid,'batch':BATCH,'clearance':measured,'strictRimContactObserved':measured['minLowGap']<=.1,'newlyInstalled':0,'publication':False,'identityAccepted':False,'installationApproved':False,'modelGeometryChanges':0,'scriptExternalAICalls':0,'qualification':'Original government TIN compatibility only, not runtime acceptance. Preserves the existing 0.1m strict contact requirement; no suppression, terrain/publication edits or tolerance exceptions.'}
 with connect() as c:
  c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
  for item in inputs:assert ref(ROOT/item['path'])==item
  assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
 save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'jobId':jid,'minLowGap':measured['minLowGap'],'strictRimContactObserved':result['strictRimContactObserved'],'neonVerified':True}),flush=True)
if __name__=='__main__':
 if '--owned' in sys.argv:owned()
 else:
  assert not DOC.exists() and not LOCAL.exists()
  claim=reservations.claim('codex-apex-original-tin-'+str(uuid.uuid4()),['source-context:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'],claim
  save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
