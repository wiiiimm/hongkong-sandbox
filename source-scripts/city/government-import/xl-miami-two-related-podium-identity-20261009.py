"""Capture exact fresh primary tower/podium OP lineage; no geometry modifications."""
import sys,json,importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from source import BASE,request
from miami_two_related_podium_identity_20261009 import DOC,UIDS,RELATED,verify_collection
def main():
 assert not (DOC/'result.json').exists(),'Completed stage immutable';DOC.mkdir(parents=True,exist_ok=True);selected=read(DOC.parent/'government-xl-miami-five-grounded-originals-20261009/selection.json.gz');rows=[];refs=[]
 for uid in sorted(UIDS|{RELATED}):
  old=next(r for r in selected['rows'] if r['uid']==uid);csuid=old['source']['building']['buildingCSUID'];name=uid.split('/')[1].replace(':','-');data={}
  for kind,layer,where,geom in [('provider',0,"BuildingCSUID='"+csuid+"'",True),('opRelations',1002,"BuildingCSUID='"+csuid+"'",False),('opStructures',1003,None,False)]:
   if kind=='opStructures':where='BuildingStructureID IN('+','.join(str(f['attributes']['BuildingStructureID']) for f in data['opRelations']['features'])+')'
   raw,receipt=request(BASE+'/'+str(layer)+'/query',{'f':'json','where':where,'outFields':'*','returnGeometry':str(geom).lower(),'resultRecordCount':'1000'});p=DOC/(name+'-'+kind+'.json');p.write_bytes(raw);save(DOC/(p.name+'.request.json'),receipt);refs.append({'path':str(p.relative_to(ROOT)),'sha256':digest(raw)});data[kind]=json.loads(raw);assert not data[kind].get('error') and not data[kind].get('exceededTransferLimit')
  rows.append({'uid':uid,**data})
 save(DOC/'related-podium-provider-context.json.gz',{'uids':sorted(UIDS|{RELATED}),'rows':rows,'inputHashes':refs,'sourceGeometryChanges':0,'identityAccepted':False});proof=verify_collection();save(DOC/'complete-two-original-identity.json.gz',proof);save(DOC/'selection.json.gz',{**selected,'rows':[r for r in selected['rows'] if r['uid'] in UIDS],'manifestSHA256':proof['currentManifestSHA256']});print({k:proof[k] for k in ['uids','wholeTargetCoverage','maximumFullSourceExtentM','unrelatedExcessM2','rawRelatedExcessOverlaps']},flush=True)
 spec=importlib.util.spec_from_file_location('miami_two_identity_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.freeze(DOC.name,'two-independent-grounded-originals-exact-related-podium-identity-v1',[Path(__file__),HERE/'miami_two_related_podium_identity_20261009.py',HERE/'miami_independent_original_collection_20261009.py'],{'uids':sorted(UIDS),'identityAccepted':True,'sourceIdentityPolicy':proof['policy'],'physicalAccepted':False,'requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'fresh-two-only-complete-current-physical-neighbours-runtime-browser-pending','nextStep':'Retain exact current related podium and every other actor; no collision/runtime/terrain exception. Fresh two-only physical and full basic/native neighbours must pass before staged and guarded browser/publication.'})
if __name__=='__main__':main()
