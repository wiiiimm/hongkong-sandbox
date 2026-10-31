"""Persist source-specific diagnostic causes without changing any acceptance gate."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,jobs,connect,Jsonb,dict_row
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('config');args=parser.parse_args();config=ROOT/args.config;cfg=read(config)
 doc=ROOT/cfg['output'];assert doc.resolve().is_relative_to(ROOT) and not (doc/'result.json').exists()
 lease=read(cfg['lease']);assert reservations.heartbeat(lease)['ok'] and 'building:'+cfg['uid'] in lease['resources']
 d=read(ROOT/cfg['context']);assert d['uid']==cfg['uid'] and d['wholeSourceUncoveredFaces']==0
 current=read(ROOT/cfg['currentPreflight']);identity=next(r['identity'] for r in current['rows'] if r['uid']==cfg['uid'])
 reasons={}
 for f in d['originalOpenExteriorPaths']['faces']:
  for reason in f['reasons']:reasons[reason]=reasons.get(reason,0)+1
 refs=d['evidenceRefs']+current['evidenceRefs']+[ref(p) for p in [Path(__file__),config,ROOT/cfg['context'],ROOT/cfg['currentPreflight'],*[ROOT/p for p in cfg['additionalArtifacts']]]]
 for path in cfg['additionalArtifacts']:
  a=read(ROOT/path);assert a.get('uid',cfg['uid'])==cfg['uid']
  refs.extend(a.get('evidenceRefs',[]))
 refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']);payload={'uid':cfg['uid'],'sourceSHA256':d['sourceSHA256'],'evidenceRefs':refs};stage='complete-original-role-diagnosis-v1';jid=jobs.enqueue(cfg['batch'],stage,payload);job=jobs.claim(cfg['batch'],lease['owner'],[stage],lease_seconds=1800);assert job and job['id']==jid
 result={**payload,'jobId':jid,'batch':cfg['batch'],'stage':stage,'humanStatus':'held-unknown','requiresAI':False,'requiresHumanDecision':False,'needsComputeProcessing':True,'sourceGeometryChanges':0,'newlyInstalled':0,'publication':False,'installationApproved':False,'permanentRejection':False,'wholeOriginalFaces':d['wholeSourceFaces'],'wholeSourceUncoveredFaces':0,'affectedFaces':len(d['continuousAffectedFaces']),'affectedNonWalls':len(d['otherAffectedFaces']),'rawWallRoleFailureCounts':reasons,'currentIdentityPassed':identity['passed'],'currentIdentityReasons':identity['reasons'],'upwardMinimumGapM':d['upwardContinuousMinimumGapM'],'originalCollapsedFacesAccounted':d['originalZeroAreaFaces'],'originalOpenWindingConflictsPreserved':len(d['originalOpenExteriorPaths']['originalOrientationConflicts']),'heldReasons':cfg['heldReasons'],'nextStep':cfg['nextStep'],'qualification':'New exact-source continuous/topology cause diagnosis against byte-pinned historical drawn terrain, plus current identity where provided. Historical geometry is not a current physical acceptance. Raw narrow role/identity failures remain; every original face accounted. No geometry edits, tolerance welding, blanket role/threshold waiver or installation credit.'}
 try:
  with connect() as con:
   con.row_factory=dict_row;con.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(con,lease)
   for item in refs:assert ref(ROOT/item['path'])==item
   assert con.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
  save(doc/'result.json',result);save(doc/'neon-sync.json',{'jobId':jid,'resultVerified':True});print(json.dumps({'uid':cfg['uid'],'jobId':jid,'resultVerified':True,'newlyInstalled':0}),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
