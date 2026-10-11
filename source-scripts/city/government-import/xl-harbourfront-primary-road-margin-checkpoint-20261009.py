"""Freeze exact original street-front evidence; no identity/support acceptance."""
import importlib.util,json
from run import ROOT,HERE,read
BASE=ROOT/'docs/astra-city/government-import'
def main():
 batch='government-xl-two-harbourfront-primary-owner-20261009';doc=BASE/batch;proof=read(doc/'attached-original-road-margin-diagnostic.json.gz')
 paths=[HERE/n for n in ['xl-harbourfront-primary-owner-discovery-20261009.py','xl-harbourfront-primary-tour-scenes-20261009.mjs','xl-harbourfront-original-low-wall-vectors-20261009.py','xl-harbourfront-attached-road-margin-evidence-20261009.py','xl-harbourfront-primary-road-margin-checkpoint-20261009.py','xl-second-pass.py','government_georef_cell_identity.py']]
 paths +=[HERE.parent/'landsd-territory/source.py',ROOT/proof['originalPath'],ROOT/'3d-viewer/city/data/tiles/1_-1.json']
 for name in ['xl-terrain-recovery-20261009-118230-current-inputs','xl-terrain-recovery-20261009-118230-original-components']:
  paths +=[p for p in (BASE/name).rglob('*') if p.is_file()]
 spec=importlib.util.spec_from_file_location('harbourfront_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(batch,'exact-original-attached-road-margin-primary-source-evidence-v1',paths,{'uids':['landsd/118230:0'],'sourceKey':proof['sourceKey'],'sourceSHA256':proof['sourceSHA256'],'worldTrianglesSHA256':proof['worldTrianglesSHA256'],'completeOriginalFaces':19438,'allFarFaceIds':proof['allFarFaceIds'],'everyFarFaceBelongsToMainBody':True,'maxIndependentRoadMarginDistanceM':proof['maxFarOriginalVertexRoadMarginDistanceM'],'identityAccepted':False,'physicalAccepted':False,'scriptFullAcceptancePassed':False,'sourceIdentityInterpretationUsedAI':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'requiresComputeProcessing':True,'remainingReason':'source-specific-street-front-boundary-identity-review-and-complete-original-wall-cylinder-support-pending','nextStep':'Review all ten exact attached far faces against independent road-margin/cartographic quantization and primary owner imagery. Then independently resolve complete source support/physical/current foreign/runtime/browser gates; raw extent and all original geometry retained.'})
 print(json.dumps({'jobId':result['jobId'],'sourceKey':proof['sourceKey']}),flush=True)
if __name__=='__main__':main()
