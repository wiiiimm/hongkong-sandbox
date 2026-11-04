"""Continue completed original-source clearance through qualification and installation preflight."""
import argparse,json,os,subprocess,sys,time
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';FINITE=BASE/'government-xl-tai-kwei-complete-finite-v1-20261017'
LOCAL=HERE/'local/government-xl-tai-kwei-clearance-followup-v1-20261017'
def identity(pid):
 try:
  text=Path('/proc/'+str(pid)+'/stat').read_text();fields=text[text.rfind(')')+2:].split()
  return fields[19],fields[0]
 except FileNotFoundError:return None

def verify_receipt(path):
 r=read(path)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={}
 for q in r['evidenceRefs']:
  assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256'];assert digest((ROOT/q['path']).read_bytes())==q['sha256'],q['path']
 return dict(jobId=r['jobId'],exactNeonResultVerified=True,evidenceHashesVerified=len(pins))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--pid',type=int,required=True);a=ap.parse_args()
 initial=identity(a.pid);assert initial and initial[1]!='Z','Predecessor must be live at supervisor start'
 command=Path('/proc/'+str(a.pid)+'/cmdline').read_bytes();assert b'tai_kwei_complete_finite_v1_20261017.py' in command
 assert not LOCAL.exists();LOCAL.mkdir(parents=True)
 save(LOCAL/'predecessor.json',dict(pid=a.pid,startTicks=initial[0],script='tai_kwei_complete_finite_v1_20261017.py',scope='Original-source qualification and preflight only; no live publication'))
 try:
  while True:
   current=identity(a.pid)
   if current is None or current[0]!=initial[0]or current[1]=='Z':break
   time.sleep(20)
  check=verify_receipt(FINITE/'result.json');summary=read(FINITE/'summary.json')
  assert summary['complete']and summary['ownAllStrict']and summary['neighbourNoIntroducedFailures']and summary['actors']==66
  save(LOCAL/'clearance-verified.json',check);print('Completed clearance receipt verified',check,flush=True)
  commands=[['tai_kwei_qualified_stage_v1_20261017.py'],['tai_kwei_original_live_install_v1_20261017.py','--prepare-only']]
  for i,args in enumerate(commands):
   p=subprocess.run([sys.executable,str(HERE/args[0]),*args[1:]],cwd=ROOT,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},timeout=1800)
   save(LOCAL/f'command-{i}.json',dict(args=args,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
   if i==0:save(LOCAL/'qualification-verified.json',verify_receipt(BASE/'government-xl-tai-kwei-qualified-stage-v1-20261017/result.json'))
   print('Completed',args,flush=True)
  save(LOCAL/'result.json',dict(complete=True,preflightPrepared=True,publication=False,newlyInstalled=0,nextStep='Review installation preflight, run --install, inspect live exports, commit/push verified installation.'))
 except BaseException as e:
  save(LOCAL/'failure.json',dict(error=repr(e),publication=False,newlyInstalled=0));raise
if __name__=='__main__':main()
