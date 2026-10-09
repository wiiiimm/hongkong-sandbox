"""Fence complete unchanged original podium and upper-source support investigations."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,digest
BASE=ROOT/'docs/astra-city/government-import'
def main():
 s=importlib.util.spec_from_file_location('miami_podium_upper_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 original=BASE/'government-xl-miami-fourteen-original-current-diagnostic-20261009';selection=read(original/'selection.json.gz');inputs=[original/'result.json',original/'selection.json.gz',original/'complete-fourteen-original-contact-inputs.json.gz',Path(__file__),HERE/'source_closed_components.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'support-interface.mjs',HERE/'support-contact.mjs',HERE/'triangle-point-index.mjs']
 batches=[('government-xl-miami-three-original-podium-graph-20261009',['landsd/232089:0','landsd/259038:0','landsd/231147:0'],['xl-miami-three-original-podium-graph-20261009.py','xl-miami-three-original-podium-footing-20261009.mjs'],'complete-original-podium-component-ground-roles-v1'),('government-xl-miami-four-marina-upper-original-graph-20261009',['landsd/176571:0','landsd/179052:0','landsd/201643:0','landsd/37001:0','landsd/231147:0'],['xl-miami-four-marina-upper-original-graph-20261009.py','xl-miami-four-marina-upper-footing-inputs-20261009.py','xl-miami-four-marina-upper-footing-20261009.mjs'],'complete-original-marina-upper-source-component-and-footing-roles-v1'),('government-xl-miami-rooftop-orphan-original-support-20261009',['landsd/232089:0'],['xl-miami-rooftop-orphan-original-support-20261009.mjs'],'complete-original-two-rooftop-parts-supported-body-interface-failure-v1'),('government-xl-miami-marina-block4-roof-part-20261009',['landsd/179052:0','landsd/231147:0'],['xl-miami-marina-block4-roof-part-20261009.mjs'],'complete-original-roof-enclosure-supported-body-interface-failure-v1')]
 previous=[]
 for batch,uids,names,stage in batches:
  paths=inputs+previous+[HERE/f for f in names]
  for r in selection['rows']:
   if r['uid'] in uids:p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];paths.append(p)
  result={'uids':uids,'physicalAccepted':False,'scriptFullAcceptancePassed':False,'sourceGeometryChanges':0,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'requiresMoreComputeOrSourceEvidence':True,'remainingReason':'complete-original-source-role-or-missing-authored-support-evidence','nextStep':'Use exact supported body/source ownership and independently actual renderable original component evidence. Keep every original part, raw gap and current actor. No original support credit unless actual anchor is present and full physical/runtime gates pass.'}
  if 'three-original-podium' in batch:
   result['podiumGroundedPaths']=read(BASE/batch/'complete-original-podium-grounded-paths.json.gz')['rows'];result['remainingReason']='Miami-podium-parts29-30-detached;ClubII-bounded-wall-root-needs-independent-role;Marina-current-full-assembly-gates-required'
  elif 'four-marina' in batch:
   result['upperGraphCounts']=read(BASE/batch/'summary.json')['rows'];result['independentFootingPaths']=read(BASE/batch/'complete-upper-independent-footing-paths.json.gz')['rows']
  elif 'rooftop-orphan' in batch:
   x=read(BASE/batch/'complete-orphan-original-roof-interface.json.gz');result['originalParts']=[29,30];result['rawOriginalRoofGapRangeM']=[x['combinedOriginalParts']['strictLowRim']['minGap'],x['combinedOriginalParts']['strictLowRim']['maxGap']];result['remainingReason']='Both-retained-original-rooftop-parts-no-near-footing-contact-minimum-gap0.148m'
  else:
   x=read(BASE/batch/'complete-original-roof-part-interface.json.gz');result['unsupportedOriginalPart']=69;result['originalFaceIds']=x['partOriginalFaceIds'];result['rawSupportedWholeOriginalRoofGapM']=x['wholeOtherSupportedOriginalInterface']['strictLowRim']['minGap'];result['remainingReason']='Original10face-rooftop-enclosure1.631m-above-all-other-supported-source-roof-surfaces'
  m.freeze(batch,stage,paths,result);previous.append(BASE/batch/'result.json')
if __name__=='__main__':main()
