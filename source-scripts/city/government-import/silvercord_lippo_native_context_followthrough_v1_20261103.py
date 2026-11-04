"""Wait for this exact finite checks process, then run the prepared native context."""
import sys,time,subprocess
from pathlib import Path
from run import ROOT,HERE,read
from china_ferry_current_foundations_v1_20261020 import authenticate
PID=1823146
EXPECTED='silvercord_lippo_complete_floor_checks_sequence_v1_20261103.py'
STATE=HERE/'local/government-xl-silvercord-lippo-complete-floor-checks-sequence-v1-20261103/progress.json'
proc=Path('/proc')/str(PID)
def identity():
 try:return (proc/'cmdline').read_bytes(),(proc/'stat').read_text().split(') ',1)[1].split()[19]
 except FileNotFoundError:return None
initial=identity();assert initial and EXPECTED.encode()in initial[0]
deadline=time.monotonic()+3600
while identity()is not None:
 assert identity()==initial,'Predecessor PID reused; do not follow another process'
 assert time.monotonic()<deadline,'Finite predecessor observation ended; no retry or approval'
 time.sleep(5)
progress=read(STATE);assert progress['complete']is True and [r['phase']for r in progress['completed']]==['scope','runtime','forms']
for row in progress['completed']:
 result,_=authenticate(ROOT/'docs/astra-city/government-import'/row['batch']);assert result['jobId']==row['jobId']
print(dict(exactFinitePredecessorCompleted=True,starting='all-native-terrain-context'),flush=True)
subprocess.run([sys.executable,str(HERE/'silvercord_lippo_all_native_terrain_context_v1_20261103.py')],cwd=ROOT,check=True)
