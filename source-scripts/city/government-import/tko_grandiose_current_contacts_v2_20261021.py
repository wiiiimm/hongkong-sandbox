"""Rebind all original-child contact evidence to current four-mode inputs.
Machine ledger only: preserve roof/foundation warnings and withhold acceptance.
"""
from pathlib import Path
import json
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-grandiose-current-contacts-v2-20261021';DOC=BASE/BATCH
NAMES=dict(capture='government-xl-tko-grandiose-joint-capture-v1-20261021',foundation='government-xl-tko-grandiose-joint-foundations-v3-20261021',contacts='government-xl-tko-complete-contacts-v1-20261021',paths='government-xl-tko-complete-paths-v1-20261021',tower3='government-xl-tko-assembly-contacts-v1-20261021',popcorn='government-xl-grandiose-assembly-contacts-v1-20261021',facade='government-xl-tko-tower3a-attachment-paths-v1-20261021')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 for k,n in NAMES.items():
  _,pins[k]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
 def take(k,f):
  p=BASE/NAMES[k]/f;key=str(p.relative_to(ROOT));assert digest(p.read_bytes())==pins[k][key];used[key]=pins[k][key];refs.append(p);return read(p)
 def witnesses(rows,key=None):return sorted(json.dumps(r if key is None else r[key],sort_keys=True)for r in rows)
 rows=take('capture','selection.json.gz')['rows'];accounts=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  for row in rows:
   uid=row['uid']
   if uid in ['landsd/265489:0','landsd/246824:0']:continue
   name=uid.split('/')[1];folder=mode+'/'+name+'/'
   inp=take('foundation',folder+'input.json.gz');raw=inp['rows'][0];assert raw['uid']==uid
   tri=np.asarray(raw['position']).reshape(-1,3)[np.asarray(raw['index']).reshape(-1,3)];support=np.asarray(inp['podium']).reshape(-1,3,3)
   report=take('foundation',folder+'support.json.gz')['rows'][0]['proof'];foundation=take('foundation',folder+'foundation.json')
   failures=report['unresolved'];key='tower3' if uid=='landsd/32147:0' else 'popcorn' if uid=='landsd/81731:0' else 'contacts'
   c=take(key,mode+'/'+name+'.json.gz');assert digest(tri.tobytes())==c['sourceWorldSHA256'];assert digest(support.tobytes())==c['podiumWorldSHA256'];assert c['sourceSHA256']==row['sourceSHA256']
   assert witnesses(failures)==witnesses(c['targets'],'witness')
   direct=sum(bool(x['positiveContacts'])for x in c['targets']);left=[x for x in c['targets']if not x['positiveContacts']];bounded=facade=0
   if left:
    p=take('paths',mode+'/'+name+'.json.gz');assert p['sourceWorldSHA256']==c['sourceWorldSHA256'] and p['supportWorldSHA256']==c['podiumWorldSHA256'];assert witnesses(p['rows'],'witness')==witnesses(left,'witness')
    for x in p['rows']:
     v=x['verifiedPath']
     if v:assert v['maximumResidualM']<=.001 and v['withinEndpointHeight'] and v['maximumPathHeightM']<=v['endpointHeightCeilingM']+1e-9;bounded+=1
    left=[x for x in p['rows']if not x['verifiedPath']]
   if left:
    assert uid=='landsd/32024:0';a=take('facade',mode+'.json.gz');assert a['sourceWorldSHA256']==c['sourceWorldSHA256'] and a['podiumWorldSHA256']==c['podiumWorldSHA256'];assert witnesses(a['rows'],'witness')==witnesses(left)
    for x in a['rows']:assert x['attachmentVerified'] and not x['structuralRootCredit']
    facade=len(a['rows'])
   assert direct+bounded+facade==len(failures)
   accounts.append(dict(uid=uid,mode=mode,sourceSHA256=row['sourceSHA256'],sourceWorldSHA256=c['sourceWorldSHA256'],supportWorldSHA256=c['podiumWorldSHA256'],strictContacts=report['strictContacts'],wallContacts=report['wallIntersections'],rawUnresolved=len(failures),finiteContacts=direct,boundedPaths=bounded,scopedFacadePaths=facade,unaccountedContactWarnings=0,rawFoundation={k:v for k,v in foundation.items()if k!='components'}))
 result=dict(uids=[r['uid']for r in rows],accounts=accounts,currentContactInputsMatched=True,sourceGeometryChanges=0,installationApproved=False,physicalAcceptance=False,qualification='Exact current source/support arrays and complete raw witness sets match prior contact evidence. Original roof-projection foundation warnings remain explicit; this ledger does not resolve those, approve visual appearance, or grant installation.')
 save(DOC/'ledger.json',result)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 receipt=module('joint_contact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-four-mode-original-contact-evidence-binding',refs,result);print(json.dumps(dict(jobId=receipt['jobId'],accounts=len(accounts))),flush=True)
if __name__=='__main__':main()
