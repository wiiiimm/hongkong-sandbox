"""Fenced exact installed-native then foreign-BASIC source-contact sequence."""
from pathlib import Path
import json,subprocess,sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-source-contact-sequence-v1-20261029';SCOPE='government-xl-fuying181489-complete-source-scope-v1-20261029';RUNTIME='government-xl-fuying181489-five-member-runtime-v2-20261029';ATTRS='government-xl-fuying181489-five-member-attributes-v1-20261029';INVENTORY='government-xl-after-peninsula-native-bounds-v1-20261029';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__)];cache={}
 for name in [SCOPE,RUNTIME,ATTRS,INVENTORY]:cache[name]=authenticate(BASE/name)[0];refs.append(BASE/name/'result.json')
 DOC.mkdir();names=[BATCH+'-natives',BATCH+'-foreign-basics'];common=['--scope',SCOPE,'--runtime',RUNTIME,'--attributes',ATTRS];completed=[]
 commands=[['selected_original_overlapping_native_contacts_v3_20261024.py',['--batch',names[0],*common,'--inventory',INVENTORY]],['selected_original_model_only_foreign_contacts_v3_20261024.py',['--batch',names[1],*common,'--native-contacts',names[0],'--uid','landsd/181489:0']]]
 for tool,args in commands:
  name=names[len(completed)];assert not(BASE/name).exists();assert reservations.owns(lease)
  with(DOC/(name+'.log')).open('w')as log:process=subprocess.run([sys.executable,str(HERE/tool),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
  save(DOC/(name+'-command.json'),dict(tool=tool,args=args,exitCode=process.returncode));assert process.returncode==0,(tool,process.returncode)
  receipt,pins=authenticate(BASE/name);summarypath=BASE/name/'summary.json';assert digest(summarypath.read_bytes())==pins[str(summarypath.relative_to(ROOT))];summary=read(summarypath);refs.extend([HERE/tool,BASE/name/'result.json',summarypath]);completed.append(dict(batch=name,jobId=receipt['jobId'],pairs=len(summary['rows'])));save(DOC/'progress.json',dict(uids=['landsd/181489:0'],completed=completed,running=len(completed)<2));print(completed[-1],flush=True)
 result=dict(uids=['landsd/181489:0'],completed=completed,completeSourceContactSequence=True,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Complete exact finite source/native and foreign BASIC contacts retained. Every positive needs source-role/physical interpretation; no geometry, support, identity or publication approval.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('fuying_contacts_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-fuying-original-source-native-and-basic-contact-sequence',refs,result)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();scope=read(BASE/SCOPE/'summary.json');keys={'building:landsd/181489:0','terrain:city/data/terrain.json'}|{'building:'+n['uid']for r in scope['rows']for n in r['nearbyNativeActors']};claim=reservations.claim('fuying-source-contacts-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
