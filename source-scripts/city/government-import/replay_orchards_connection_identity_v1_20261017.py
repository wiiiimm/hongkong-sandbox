import sys
from pathlib import Path
sys.path.insert(0,'source-scripts/city/government-import')
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from orchards_named_connection_identity_v1_20261017 import interpret,UID
base=ROOT/'docs/astra-city/government-import';batch='government-xl-orchards-named-connection-identity-v1-20261017';doc=base/batch;prior=base/'government-xl-three-current-originals-v1-20261017';refs=[]
assert not doc.exists()
for name in ['government-xl-orchards-primary-context-v1-20261017','government-xl-orchards-original-connection-context-v1-20261017','government-xl-orchards-lower-extension-attribution-v1-20261017']:
 d=base/name;r=read(d/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256'];refs.append(ROOT/e['path'])
 refs.append(d/'result.json')
row=next(x for x in read(prior/'selection.json.gz')['rows']if x['uid']==UID);context=next(x for x in read(prior/'context.json.gz')['rows']if x['uid']==UID)
raw=verify_files(row,context,HERE/'local'/batch/'identity');tri=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));final=module('orchards_identity_forms',HERE/'xl-final-script-pass.py');forms=[f for f,_,_ in final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])];review=read(base/'government-xl-orchards-lower-extension-attribution-v1-20261017/attribution.json.gz')
identity=interpret(raw,row,tri,forms,review);save(doc/'identity.json',identity)
# Fail closed on source changes, additional failures, changed geometry and role scope.
from copy import deepcopy
cases=[]
a=deepcopy(raw);a['reasons']+=['foreign-overlap'];cases.append((a,row,tri,forms,review))
b=deepcopy(row);b['sourceSHA256']='0'*64;cases.append((raw,b,tri,forms,review))
t=tri.copy();t[0,0,0]+=.001;cases.append((raw,row,t,forms,review))
v=deepcopy(review);v['sourceFaces']=v['sourceFaces'][:-1];cases.append((raw,row,tri,forms,v))
f=deepcopy(forms);next(x for x in f if x['uid']=='landsd/233002:0')['parent']='unrelated';cases.append((raw,row,tri,f,review))
for args in cases:
 try:interpret(*args)
 except AssertionError:pass
 else:raise AssertionError('Unsafe altered input accepted')
save(doc/'validation.json',dict(baselinePassed=True,negativeCasesRejected=len(cases),physicalAccepted=False))
refs += [HERE/'orchards_named_connection_identity_v1_20261017.py',prior/'selection.json.gz',prior/'context.json.gz',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py']
result=module('orchards_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'orchards-named-original-connection-identity-only-v1',list(set(refs)),dict(uids=[UID],identityAccepted=True,physicalAccepted=False,fullAcceptance=False,rawExtentReasonsRetained=identity['rawExtentReasonsRetained'],nextStep='Run current original terrain and full contact/foundation/neighbour/browser gates with this explicit source-bound interpretation; do not publish from identity-only evidence.'))
print(result['jobId'])
