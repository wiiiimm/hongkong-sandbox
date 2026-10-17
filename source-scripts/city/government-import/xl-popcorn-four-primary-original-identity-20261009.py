"""Fresh primary/full-source identity for four named originals; never install."""
import importlib.util,json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from popcorn_primary_original_identity_20261009 import UIDS,verify_files
BATCH='government-xl-popcorn-four-primary-original-identity-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-current-overlapping-original-recovery-20261009/selection.json.gz'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();rows=[r for r in read(INPUT)['rows'] if r['uid'] in UIDS];assert {r['uid'] for r in rows}==UIDS
 claim=reservations.claim('popcorn-primary-original-identity-'+str(uuid.uuid4()),['building:'+u for u in sorted(UIDS)],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
 decoder=module('fresh_primary_decode','xl-second-pass.py');decoder.LOCAL=LOCAL;(LOCAL/'assets').mkdir(parents=True);final=module('fresh_primary_forms','xl-final-script-pass.py');outputs=[]
 try:
  for row in rows:
   assert reservations.heartbeat(lease)['ok'];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];(LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')).write_bytes(raw);row['triangles']=row['native']['model']['triangles'];tri=decoder.glb_triangles(row);lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
   context=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,forms),neighbourTileHashes={url:digest((ROOT/'3d-viewer'/url).read_bytes()) for _,_,url in forms});stem=row['uid'].split('/')[1].replace(':','-');save(DOC/(stem+'-current-context.json.gz'),context)
   proof=verify_files(row,context,LOCAL/'identity'/stem);save(DOC/(stem+'-identity.json'),proof);outputs.append(dict(uid=row['uid'],passed=proof['passed'],reasons=proof['reasons'],rawWholeCellReasonsRetained=proof['rawWholeCellReasonsRetained'],independentPrimaryFullSourceSpatialChecks=proof['independentPrimaryFullSourceSpatialChecks']));save(DOC/'partial-summary.json',{'rows':outputs,'installationApproved':False});print(json.dumps(outputs[-1]),flush=True)
  save(DOC/'selection.json.gz',{'rows':rows,'publication':False});save(DOC/'summary.json',{'rows':outputs,'independentIdentitiesPassed':sum(r['passed'] for r in outputs),'installationApproved':False,'sourceGeometryChanges':0,'qualification':'Four named current primary/full-source identity replays. All raw whole-cell diagnostics retained. Full physical/runtime/neighbour/browser/publication gates remain pending. Freeze only after independent helper review.'})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
