"""Bounded diagnostic compute pipeline; no current acceptance or publication."""
import concurrent.futures,json,subprocess,sys,time
from run import ROOT,HERE,read,save,digest,connect
BASE="docs/astra-city/government-import/"
PHYS=BASE+"government-xl-no1-garden-literal-parent-complete-current-physical-v4-20261010"
COARSE="xl-terrain-recovery-20261010-no1-garden-literal-parent-current-complete-finite-clearance-v2"
PAIRED="xl-terrain-recovery-20261010-no1-garden-literal-parent-current-complete-paired-column-v2"
GRAPH="xl-terrain-recovery-20261010-no1-garden-literal-parent-current-original-support-v2"
CONTEXT="xl-terrain-recovery-20261010-no1-garden-literal-parent-finite-wall-grade-context-v3"
GRADE="xl-terrain-recovery-20261010-no1-garden-literal-parent-current-original-wall-grade-root-v2"
def call(script,*args):
 subprocess.run([sys.executable,str(HERE/script),*args],cwd=ROOT,check=True)
def main():
 start=time.monotonic();folder=ROOT/PHYS
 while not (folder/"result.json").is_file():
  assert time.monotonic()-start<1800,"Physical prerequisite not complete; no source proof started"
  time.sleep(5)
 result=read(folder/"result.json");sync=read(folder/"neon-sync.json");assert sync["resultVerified"]
 with connect() as c:
  c.execute("SET TRANSACTION READ ONLY");assert c.execute("SELECT status,result FROM astra_modelling.jobs WHERE id=%s",(result["jobId"],)).fetchone()==("complete",result)
 selected=read(folder/"selection.json.gz");assert digest((ROOT/"3d-viewer/city/data/manifest.json").read_bytes())==selected["manifestSHA256"]
 assert all(r["strictFoundationAccepted"] for r in read(folder/"foundation.json")["rows"])
 print(json.dumps(dict(physicalComplete=result["jobId"],rawReasons=result["reasons"],sourceOnly=True)),flush=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  tasks=[pool.submit(call,"xl-terrain-recovery-20261010-coupled-complete-conservative-clearance-v4.py","--physical",PHYS,"--batch",COARSE),pool.submit(call,"xl-terrain-recovery-20261010-coupled-ordinary-original-world-support-reused-discovery-v6.py","--uid","landsd/304714:0","--physical",PHYS,"--batch",GRAPH,"--contact-reuse",BASE+"xl-terrain-recovery-20261010-no1-garden-current-original-support-v1")]
  for task in tasks:task.result()
 call("xl-terrain-recovery-20261010-coupled-coarse-paired-column-checkpoint-v1.py","--physical",PHYS,"--coarse",BASE+COARSE,"--batch",PAIRED)
 call("xl-terrain-recovery-20261010-no1-garden-literal-parent-finite-wall-grade-context-v3.py")
 call("xl-terrain-recovery-20261010-no1-garden-complete-finite-wall-grade-source-v1.py","--physical",PHYS,"--support",BASE+GRAPH,"--context",BASE+CONTEXT,"--batch",GRADE)
 print(json.dumps(dict(completeDiagnosticPipeline=True,grade=BASE+GRADE,fullAcceptance=False,installationApproved=False)),flush=True)
if __name__=="__main__":main()
