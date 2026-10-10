"""Pin current retained native identity, whole bounds and untouched legacy flags.

The final owned-B acceptance still independently replays the complete v2 proof.
No native whole-landmark acceptance is introduced by carrier qualification.
"""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-terrain-recovery-hkdi-block-b-current-qualified-native-role-v3-20261010';DOC=BASE/BATCH
s=importlib.util.spec_from_file_location('hkdi_current_owned_v2',HERE/'xl-terrain-recovery-20261010-hkdi-block-b-current-qualified-native-role-v2.py');prior=importlib.util.module_from_spec(s);s.loader.exec_module(prior)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def recheck():
 r=prior.recheck();manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==r['currentManifest'];native=next(x for x in read(prior.PROBE/'selection.json.gz')['rows']if x['uid']==prior.NATIVE);matches=[]
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid']==prior.NATIVE:matches.append((p,e))
 assert len(matches)==1;catalogue,entry=matches[0]
 assert entry['buildingCSUID']==native['source']['building']['buildingCSUID']=='4418318510T20100222' and entry['modelId']==native['modelId']=='B441831851001063C0'
 assert entry['worldBounds']==native['native']['model']['worldBounds'] and entry['sha256']==prior.SOURCES[prior.NATIVE]
 assert entry['publicationApproved']is True and entry['placementReviewed']is True and entry['wholeLandmarkAccepted']is False
 assert entry.get('knownPlacementHold')is None
 for p,h in read(HERE/'local'/prior.PROBE.name/'runtime-geometry.json.gz')['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 current_form=next(x['building']for x in read(prior.PHYS/'neighbour-inputs.json.gz')['rows']if x['building']['uid']==prior.NATIVE);assert current_form['buildingCSUID']==entry['buildingCSUID']
 assert ref(manifest)==r['currentManifest'];r.update(contract='hkdi-owned-block-b-current-qualified-native-cap-support-v3',completeCurrentInstalledNativeEntryPreserved=entry,currentNativeWholeLandmarkAccepted=False,currentNativeReacceptance=False)
 r['evidenceRefs']=sorted({x['path']:x for x in r['evidenceRefs']+[ref(Path(__file__)),ref(Path(prior.__file__)),ref(catalogue)]}.values(),key=lambda x:x['path']);return r

def main():
 assert not DOC.exists();r=recheck();save(DOC/'typed-role.json.gz',r);m=prior.module('hkdi_current_v3_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');m.freeze(BATCH,'current-owned-block-b-exposed-installed-native-caps-plus-current-complete-native-identity-bounds-and-preserved-legacy-flags-v3',[ROOT/x['path']for x in r['evidenceRefs']],dict(uids=[prior.OWNED],completeOriginalFaces=11593,completeOriginalComponents=345,currentTypedPhysicalAccepted=True,currentNativeWholeLandmarkAccepted=False,currentNativeReacceptance=False,reasons=[],typedRole=ref(DOC/'typed-role.json.gz'),publication=False,newlyInstalled=0));print(dict(ownedBAccepted=True,nativeReacceptance=False),flush=True)
if __name__=='__main__':main()
