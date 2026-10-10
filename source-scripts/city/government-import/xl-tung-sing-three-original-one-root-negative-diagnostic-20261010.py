"""Read-only capture of the strict sole-platform-root checker failure.

The original strict assertion is not removed or modified. This wrapper captures
its raw complete graph before the assertion and saves zero acceptance credit.
"""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BATCH='government-xl-tung-sing-three-original-one-root-negative-diagnostic-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 assert not DOC.exists();p=HERE/'xl-tung-sing-three-original-current-root-graph-20261010.py';s=importlib.util.spec_from_file_location('tung_sing_strict_one_root_unchanged',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);real=m.verify_graph;captured={}
 def capture(*args,**kwargs):
  result=real(*args,**kwargs);captured.update({'rawCompleteGraph':result,'completeOriginalActors':args[1],'completeOriginalComponents':args[2],'currentGroundInterfaces':args[3],'exactContactWitnesses':args[4],'binding':kwargs['current_binding']});return result
 m.verify_graph=capture
 try:m.main();raise RuntimeError('Historical strict-negative changed unexpectedly')
 except AssertionError as error:
  assert captured and captured['rawCompleteGraph']['genuineGroundAnchorComponents']==[365] and captured['rawCompleteGraph']['reasons']==['unresolved-original-component:343','unresolved-original-component:344','unresolved-original-component:361'];captured['originalStrictFailure']=str(error)
 save(DOC/'diagnostic.json.gz',{**captured,'strictSourceCheckerSHA256':digest(p.read_bytes()),'sourceGeometryChanges':0,'physicalAccepted':False,'installationApproved':False,'publication':False,'qualification':'The unchanged strict soleP0-root checker failed because raw343/344visual components and361separatefooting remained unresolved. Complete original graph kept, no guard removal or acceptance relaxation. Independent fresh original361footing may be separately investigated; no credit here.'})
 print({'strictAssertionPreserved':True,'rawUnresolved':[343,344,361],'physicalAccepted':False},flush=True)
if __name__=='__main__':main()
