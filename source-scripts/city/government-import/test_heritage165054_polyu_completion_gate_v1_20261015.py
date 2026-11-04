import ast,json
from pathlib import Path
from unittest.mock import Mock
root=Path.cwd(); source=root/'source-scripts/city/government-import/heritage165054_original_live_install_v1_20261015.py'
module=ast.parse(source.read_text()); fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='polyu_ready')
class Proc:
 def __init__(self,p): self.p=str(p)
 def __truediv__(self,p): return Proc(self.p+'/'+str(p))
 def exists(self): return live
 def read_bytes(self): return b'polyu_complete_saved_actor_finite_v2_draft_20261014.py'
class DB:
 def __enter__(self): return self
 def __exit__(self,*a): pass
 def execute(self,*a): return self
 def fetchone(self): return dbrow
result={'jobId':'exact','evidenceRefs':[{'path':'proof','sha256':'expected'}]}
lease={'token':'test'}; checked=[]
def read(p):
 if p.name=='reservation.json': return lease
 if missing: raise FileNotFoundError('missing terminal result')
 return result
def check(q):
 if stale: raise AssertionError('changed proof')
 checked.append(q)
r=Mock();ns={'Path':Proc,'HERE':root,'BASE':root,'POLYU':'test','read':read,'reservations':r,'connect':DB,'check':check}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),ns)
cases=[]
for name,live,owned,missing,stale,dbrow,expected in [
 ('active-process',True,False,False,False,('complete',result),False),
 ('active-lease',False,True,False,False,('complete',result),False),
 ('missing-result',False,False,True,False,('complete',result),'error'),
 ('failed-neon-job',False,False,False,False,('failed',result),'error'),
 ('mismatched-neon-result',False,False,False,False,('complete',{}),'error'),
 ('changed-evidence',False,False,False,True,('complete',result),'error'),
 ('verified-complete-released',False,False,False,False,('complete',result),True)]:
 r.owns.return_value=owned; checked.clear()
 try: actual=ns['polyu_ready']()
 except (AssertionError,FileNotFoundError): actual='error'
 assert actual==expected,(name,actual)
 if actual is True: assert checked==result['evidenceRefs']
 cases.append(name)
print(json.dumps({'passed':True,'cases':cases,'databaseWrites':0}))
