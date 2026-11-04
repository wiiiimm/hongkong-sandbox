"""Bind five historical positive identity receipts to exact current source/forms.
Separates completed identity from unresolved physical acceptance; no re-approval.
"""
import json
from run import ROOT,HERE,read,save,digest,connect
DOC=ROOT/'docs/astra-city/government-import/government-xl-identity-search-20261009'
def formsha(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def main():
 candidates=read(HERE/'local/government-xl-identity-search-20261009/positive-proof-candidates.json.gz')['rows'];assert len(candidates)==5
 scope={r['uid']:r for r in read(DOC/'live-georef-research.json.gz')['rows']};forms={}
 for t in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
  for b in read(ROOT/'3d-viewer'/t['url'])['buildings']:forms[b['uid']]=b
 out=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in candidates:
   p=ROOT/r['path'];proof=read(p);uid=proof['uid'];parent=read(p.parent/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(parent['jobId'],)).fetchone()==('complete',parent)
   assert proof['passed'] and proof['sourceSHA256']==scope[uid]['sourceSHA256'] and proof['sourceFormSHA256']==formsha(forms[uid])
   groups=proof.get('completeGroupForms',[]);assert all(forms[x['uid']]==x for x in groups)
   binding=next(x for x in parent['evidenceRefs'] if (ROOT/x['path']).resolve()==p.resolve());assert digest(p.read_bytes())==binding['sha256']
   native=c.execute("SELECT m FROM astra_modelling.native_stage_results,LATERAL jsonb_array_elements(result->'models') m WHERE cache_key=%s AND m->>'modelId'=%s",scope[uid]['sourceKey'].split('/')).fetchall();assert len(native)==1 and native[0][0]['asset']['sha256']==proof['sourceSHA256']
   out.append({'uid':uid,'name':forms[uid].get('name'),'sourceKey':scope[uid]['sourceKey'],'sourceSHA256':proof['sourceSHA256'],'modelId':scope[uid]['modelId'],'identityPreviouslyPassed':True,'targetFormMatchesCurrent':True,'completeGroupFormsMatchCurrent':True,'groupFormCount':len(groups),'proofRef':binding,'parentJobId':parent['jobId'],'parentJobVerified':True,'policy':proof['policy'],'currentPhysicalAcceptance':False,'installed':False,'physicalReasons':parent.get('reasons',[]),'qualification':'Completed exact-source identity receipt binds to current target and all complete-group forms. Historical raw identity failure remains immutable; this row has unresolved physical/runtime acceptance, not an unresolved identity check.'})
 save(DOC/'current-positive-proof-bindings.json.gz',{'rows':out,'verified':len(out),'identityFamilyHistoricalCount':190,'identityFamilyUnresolvedCurrentCount':185,'newlyInstalled':0,'publication':False})
 print(json.dumps({'verified':[r['uid'] for r in out],'remainingIdentity':185}),flush=True)
if __name__=='__main__':main()
