import sys,json,uuid,subprocess
from pathlib import Path
ROOT=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
from run import read,save,reservations,digest
from evangel_college_whole_current_role_bound_20261011 import verify_files,UID
BASE=ROOT/'docs/astra-city/government-import';ROLE=BASE/'government-xl-evangel-college-91306-whole-current-role-acceptance-v1-20261011';OUT=BASE/'government-xl-evangel-college-91306-private-stage-v1-serialization-diagnosis-20261011';LOCAL=HERE/'local'/OUT.name;LEASE=LOCAL/'reservation.json'
if '--owned' not in sys.argv:
 assert not OUT.exists();c=reservations.claim('evangel-stage-json-diagnosis-'+str(uuid.uuid4()),['building:'+UID],batch=OUT.name,ttl=3600);assert c['ok'];save(LEASE,json.loads(json.dumps(c['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);sys.exit()
assert reservations.owns(read(LEASE));role,entry=verify_files(LOCAL/'current-replay');saved=read(ROLE/'acceptance.json');saved_entry=read(ROLE/'staged-original-entry.json');differences=[]
def visit(a,b,p=''):
 if isinstance(a,dict)and isinstance(b,dict):
  ak=set(a);bk=set(b)
  if ak!=bk:differences.append(dict(pointer=p,runtimeKeys=[dict(type=type(k).__name__,value=k)for k in a],savedKeys=[dict(type=type(k).__name__,value=k)for k in b]))
  for k in a:
   if str(k)in b:visit(a[k],b[str(k)],p+'/'+str(k))
 elif isinstance(a,list)and isinstance(b,list):
  assert len(a)==len(b),(p,len(a),len(b))
  for i,(x,y)in enumerate(zip(a,b)):visit(x,y,p+'/'+str(i))
 else:assert a==b,(p,a,b)
visit(role,saved);assert entry==saved_entry;normalized=json.loads(json.dumps(role));assert normalized==saved
assert len(differences)==4 and all(d['pointer'].endswith('/completeActualEnvelopeGradeRoots')for d in differences)
assert all(d['runtimeKeys']==[dict(type='int',value=k)for k in [13,68,69,223]]and d['savedKeys']==[dict(type='str',value=str(k))for k in [13,68,69,223]]for d in differences)
assert reservations.owns(read(LEASE));save(OUT/'exact-difference.json',dict(differences=differences,soleDifference='Four grade-root mapping key types: int runtime keys to JSON string keys',wholeEntryExactlyEqual=True,serializedRoleExactlyEqual=True,noNumericOrSourceDifferences=True,newlyInstalled=0,publication=False,currentAcceptance=False,sourceGeometryChanges=0));print(json.dumps(read(OUT/'exact-difference.json')))
