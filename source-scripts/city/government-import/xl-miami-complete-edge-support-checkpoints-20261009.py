"""Fence complete original component diagnostics and independently grounded paths."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,digest
BASE=ROOT/'docs/astra-city/government-import'
UIDS=['landsd/202599:0','landsd/203438:0','landsd/203441:0','landsd/203462:0']
def main():
 spec=importlib.util.spec_from_file_location('miami_edge_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
 original=BASE/'government-xl-miami-fourteen-original-current-diagnostic-20261009';selected=read(original/'selection.json.gz');assets=[]
 for row in selected['rows']:
  if row['uid'] in set(UIDS)|{'landsd/232089:0'}:
   p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];assets.append(p)
 inputs=[original/'result.json',original/'selection.json.gz',original/'complete-fourteen-original-contact-inputs.json.gz',BASE/'government-xl-miami-nine-original-contact-20261009/all-original-source-contact-inputs.json.gz',HERE/'source_closed_components.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'support-interface.mjs',HERE/'support-contact.mjs',HERE/'triangle-point-index.mjs',Path(__file__)]+assets
 batches=[('government-xl-miami-original-roof-attachment-20261009',['xl-miami-original-roof-attachment-20261009.py','xl-miami-original-roof-support-20261009.mjs'],'complete-original-roof-contact-and-unmodified-complement-diagnostic-v1'),('government-xl-miami-original-edge-anchor-20261009',['xl-miami-original-edge-anchor-inputs-20261009.py','xl-miami-original-edge-anchor-20261009.mjs'],'complete-original-edge-component-ordinary-rim-diagnostic-v1'),('government-xl-miami-complete-edge-attachment-20261009',['xl-miami-complete-edge-attachment-20261009.py'],'complete-original-positive-dimensional-component-paths-v1'),('government-xl-miami-complete-edge-footing-20261009',['xl-miami-complete-edge-footing-inputs-20261009.py','xl-miami-complete-edge-footing-20261009.mjs'],'independent-complete-reached-original-podium-footing-v1')]
 previous=[]
 for batch,names,stage in batches:
  paths=inputs+[HERE/n for n in names]+previous
  if 'edge-attachment' in batch:paths +=[BASE/'government-xl-miami-original-edge-anchor-20261009/complete-edge-anchor-inputs.json.gz']
  if 'edge-footing' in batch:paths +=[BASE/'government-xl-miami-complete-edge-attachment-20261009/complete-original-podium-edge-components.json.gz']+[p for p in (BASE/'government-xl-miami-complete-edge-attachment-20261009').glob('*-complete-edge-attachment.json.gz')]+[BASE/'government-xl-miami-original-edge-anchor-20261009/complete-edge-anchor-inputs.json.gz']
  result={'uids':UIDS,'sourceSHA256s':{r['uid']:r['sourceSHA256'] for r in selected['rows'] if r['uid'] in set(UIDS)|{'landsd/232089:0'}},'physicalSupportAccepted':False,'scriptFullAcceptancePassed':False,'allOriginalFacesAccountedExactlyOnce':True,'sourceGeometryChanges':0,'remainingReason':'current-full-face-physical-and-source-specific-role-contract-required','nextStep':'Three complete tower graphs reach independently grounded podium edge component0. Carry exact ownership and every source face through fresh full physical/current-actor/runtime gates. Fourth tower keeps29 disconnected components pending.'}
  if 'edge-attachment' in batch:result['componentPathCounts']=read(BASE/batch/'summary.json')['rows']
  if 'edge-footing' in batch:
   x=read(BASE/batch/'complete-reached-original-podium-footing-interfaces.json.gz');main=next(r for r in x['rows'] if r['component']==0);assert main['strictOriginalGroundAnchor'];result['independentlyGroundedPodiumComponent']={'component':0,'originalFaces':len(main['originalFaceIds']),'strictContacts':main['ground']['strictContacts'],'samples':main['ground']['samples'],'wallIntersections':main['ground']['wallIntersections'],'minGapM':main['ground']['strictLowRim']['minGap'],'maxGapM':main['ground']['strictLowRim']['maxGap']};result['completeGraphFootingCandidates']=UIDS[:3]
  f.freeze(batch,stage,paths,result);previous.append(BASE/batch/'result.json')
if __name__=='__main__':main()
