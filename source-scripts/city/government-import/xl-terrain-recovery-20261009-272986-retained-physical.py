"""Fresh original Rooftop Garden physics with source-disjoint exact parent retention."""
import importlib.util,json,subprocess,sys,uuid
from argparse import Namespace
from run import ROOT,HERE,read,save,reservations
BATCH='government-xl-terrain-recovery-272986-retained-neighbours-20261009'
BASE='docs/astra-city/government-import/xl-terrain-recovery-20261009-272986-current-inputs'
DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
PIPELINE=HERE/'xl-terrain-recovery-20261009-272986-retained-contact.py'
FOREIGN=['landsd/298951:0','landsd/298952:0']
def main():
 if '--owned' in sys.argv:
  spec=importlib.util.spec_from_file_location('rooftop_indexed_physical',HERE/'xl-routed-cell-indexed-terrain-continuation.py');indexed=importlib.util.module_from_spec(spec);spec.loader.exec_module(indexed)
  indexed.TERRAIN_PIPELINE_PATH=PIPELINE;original=indexed.module
  def configured(name,filename):return original(name,PIPELINE.name if filename=='xl-routed-cell-contact-resolution.py' else filename)
  indexed.module=configured;indexed.owned(Namespace(uid='landsd/272986:0',batch=BATCH,base=BASE),DOC,LOCAL);return
 assert not DOC.exists() and not LOCAL.exists(),'Fresh version required'
 claim=reservations.claim('xl-terrain-recovery-272986-retained-'+str(uuid.uuid4()),['building:'+u for u in ['landsd/272986:0',*FOREIGN]]+['terrain-patch:landsd/272986:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
