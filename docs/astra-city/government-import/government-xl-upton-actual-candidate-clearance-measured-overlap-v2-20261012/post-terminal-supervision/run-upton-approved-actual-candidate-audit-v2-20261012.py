from pathlib import Path
import subprocess,sys,hashlib,json,os,time,threading
r=Path.cwd();h=r/'source-scripts/city/government-import';p=r/'docs/astra-city/government-import/government-xl-upton-actual-candidate-clearance-measured-overlap-v2-20261012-proposal'
for f,s in [(h/'upton_actual_candidate_clearance_audit_draft_v2_20261012.py','82f4cd30a08238dfcfc1b1f1f2015c5b1666cee237563d4944e754788b34bab3'),(h/'upton_actual_candidate_clearance_audit_v1_20261012.py','24c9f55ff1030230ea6e8ab03c9d52fee87f449c6c2b2e82c711f8b993d27e16'),(h/'upton_actual_candidate_clearance_audit_runtime_draft_v1_20261012.mjs','ddbb2e148fd539531b24cf751e1838e3cf4c16be655d2b752370dd106c6d927d'),(p/'preflight.json','798d11eebe6a6524ad6846c2588c0e9c2b948b629202b70fa5332476dcc0c53d'),(p/'every-configured-receipt-preflight.json','4192acd56619629342724b86143e5dfebb4d3e6e21268e7ad462895841640845')]:assert hashlib.sha256(f.read_bytes()).hexdigest()==s
assert json.loads((p/'preflight.json').read_text())['passed']and hashlib.sha256((r/'3d-viewer/city/data/manifest.json').read_bytes()).hexdigest()=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
log=Path('/tmp/upton-approved-actual-candidate-audit-v2-20261012.log');assert not log.exists();start=time.time();statepath=Path('/tmp/upton-approved-actual-candidate-audit-v2-processes-20261012.json')
with log.open('wb')as out:
 child=subprocess.Popen([sys.executable,str(h/'upton_actual_candidate_clearance_audit_draft_v2_20261012.py'),'--check-private-candidate-only'],cwd=r,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 state={'launcherPID':os.getpid(),'callerPID':child.pid,'startedUnix':start,'log':str(log),'mutableLogOutsideFrozenDirectories':True,'observedDescendantProcesses':[]};statepath.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state),flush=True)
 def observe():
  observed={};known={child.pid}
  while child.poll()is None:
   rows=[]
   for line in subprocess.check_output(['ps','-eo','pid=,ppid=,args='],text=True).splitlines():
    parts=line.strip().split(None,2)
    if len(parts)==3:rows.append((int(parts[0]),int(parts[1]),parts[2]))
   for _ in range(5):
    for pid,parent,args in rows:
     if parent in known and pid not in known:
      known.add(pid);observed[pid]={'pid':pid,'parentPID':parent,'args':args,'observedUnix':time.time()}
   state['observedDescendantProcesses']=list(observed.values());statepath.write_text(json.dumps(state,indent=2)+'\n')
   if any('--owned' in x['args']for x in observed.values())and any('reservations.py' in x['args']for x in observed.values()):return
   time.sleep(.5)
 watcher=threading.Thread(target=observe,daemon=True);watcher.start()
 for line in child.stdout:out.write(line);out.flush();sys.stdout.buffer.write(line);sys.stdout.buffer.flush()
 code=child.wait();watcher.join(timeout=2);terminal={**state,'exitCode':code,'elapsedSeconds':time.time()-start};Path('/tmp/upton-approved-actual-candidate-audit-v2-terminal-20261012.json').write_text(json.dumps(terminal,indent=2)+'\n');print(json.dumps(terminal),flush=True);sys.exit(code)
