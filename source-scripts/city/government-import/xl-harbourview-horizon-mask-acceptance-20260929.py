"""Accept unchanged Harbourview Horizon only after bounded base and browser proof."""
import importlib.util
import json
import shutil
from run import ROOT, HERE, read, save, digest

spec=importlib.util.spec_from_file_location('direct_phase_one',HERE/'integrate.py')
direct=importlib.util.module_from_spec(spec);spec.loader.exec_module(direct)
BASE=ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923'
DOC=BASE/'harbourview-horizon-mask-browser-20260929'
SOURCE=BASE/'harbourview-horizon-mask-final-20260929'
STAGE=HERE/'accepted/government-xl-harbourview-horizon-mask-20260929'
UID='landsd/237402:0'
def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}

def run():
 stage=read(DOC/'stage.json');assert stage['uids']==[UID]
 assert stage['catalogueSHA256']==ref(STAGE/'catalogue.json')['sha256']
 assert stage['planSHA256']==ref(STAGE/'plan.json')['sha256']
 model=read(STAGE/'catalogue.json')['models'][0]
 assert model['uid']==UID and model['sha256']==stage['sourceSHA256']==ref(STAGE/model['asset'])['sha256']
 assert model['sourceIdentityReviewed'] and model['identityReviewApproved'] and model['placementReviewed'] and model['publicationApproved']
 patch=read(STAGE/'plan.json')['topLevelTerrainPatches'][0]
 assert stage['terrainSHA256']==ref(ROOT/patch['source'])['sha256']
 identity=read(SOURCE/'identity-resolution.json')['rows'][0]
 assert identity['exactObjectAndCSUID'] and identity['targetCoverage']>=.95 and identity['sourceExcessFraction']<=.05 and identity['unrelatedIntersectingForms']==0
 contact=read(BASE/'harbourview-horizon-contact-proof-20260929.json')
 assert contact['passed'] and contact['sourceSHA256']==model['sha256']
 assert contact['terrainSHA256']==stage['terrainSHA256']
 foundation=read(SOURCE/'foundation.json')
 assert foundation['strictFoundationAccepted'] and foundation['sourceSHA256']==model['sha256']
 assert contact['nearGroundContactVerticesAboveRecordedBase']>=100 and contact['contactHullTargetCoverage']>=.8
 assert contact['fullyBuriedUpwardTriangles']==0 and contact['fullyBuriedAreaFraction']<=.001
 checks=read(SOURCE/'checks.json')
 assert checks['sourcePreserved'] and checks['missingTerrainSamples']==0 and checks['maxSamplerDeltaM']<=.004
 assert not checks['blockedNeighbourUids'] and not checks['blockedNativeNeighbourUids']
 assert checks['runtimeConcerns']==['sampled-terrain-above-model-bottom']
 browser=direct.browser_verified(DOC/'staged-browser.json',{UID});assert not browser['errors']
 views=[view for view in browser['views'] if 'time' in view]
 assert len(views)==4 and all(view['uid']==UID and abs(view['ground']-view['groundSampler'])<=.004 for view in views)
 assert all(set(v['retained'])=={'landsd/257058:0','landsd/257059:0','landsd/259577:0'} and all(r['loaded'] and not r['hidden'] for r in v['retained'].values()) for v in views)
 evidence={name:ref(path) for name,path in (('stage',DOC/'stage.json'),('browser',DOC/'staged-browser.json'),('identity',SOURCE/'identity-resolution.json'),('foundation',SOURCE/'foundation.json'),('contact',BASE/'harbourview-horizon-contact-proof-20260929.json'),('checks',SOURCE/'checks.json'))}
 for name in ('metrics','validation','neighbour-checks','native-neighbour-checks'):
  target=DOC/(name+'.json');shutil.copyfile(SOURCE/(name+'.json'),target);evidence[name]=ref(target)
 save(DOC/'acceptance.json',{'batch':stage['batch'],'uids':[UID],'passed':True,'failures':[],'sourceSHA256':model['sha256'],'candidatePatch':ref(ROOT/patch['source']),'contactResolution':{'buriedVertexFraction':contact['buriedVertexFraction'],'buriedAreaFraction':contact['fullyBuriedAreaFraction'],'fullyBuriedUpwardTriangles':0,'visibleContactHullCoverage':contact['contactHullTargetCoverage']},'evidence':evidence,'aiCalls':0,'modelGeometryChanges':0,'publication':False})
 print(json.dumps({'accepted':UID,'browserViews':len(views),'contactCoverage':contact['contactHullTargetCoverage'],'aiCalls':0}),flush=True)
if __name__=='__main__':run()
