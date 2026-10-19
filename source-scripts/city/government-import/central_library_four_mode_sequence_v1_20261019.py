"""Run original-source coordinate and foundation diagnostics under one lease."""
import sys,subprocess,json,uuid
from run import ROOT,HERE,read,save,reservations
BATCH='government-xl-central-library-four-mode-sequence-v1-20261019'
def main():
 path=HERE/'local'/BATCH/'reservation.json'
 if '--owned' in sys.argv:
  assert reservations.owns(read(path))
  for name in ['central_library_actual_render_attributes_v1_20261019.py','central_library_four_mode_foundations_v1_20261019.py']:
   subprocess.run([sys.executable,str(HERE/name)],cwd=ROOT,check=True)
  return
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/232240:0','terrain-patch:landsd/232240:0'],batch=BATCH,ttl=3600);assert claim['ok']
 lease=claim['reservation'];save(path,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(path),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
