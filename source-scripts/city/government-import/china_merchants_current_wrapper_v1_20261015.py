"""Append the unchanged historical China child to the exact current terrain wrapper."""
import copy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-merchants-current-wrapper-v1-20261015';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;OLD=BASE/'government-xl-retained-group-central-wrapper-20261009-264206-0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def stripped(x):
 x=copy.deepcopy(x)
 if 'nativeMesh'in x:x['nativeMesh'].pop('sourceOverlap',None)
 return x

def main():
 assert not DOC.exists()and not LOCAL.exists();oldpath=ROOT/'3d-viewer/city/data/terrain-government-xl-central-pier-successor-installed-v2-20261007.json';currentpath=ROOT/'3d-viewer/city/data/terrain-government-xl-caine-road-original-pair-installed-v2-20261010.json';inputs=read(OLD/'neighbour-inputs.json.gz');assert len(inputs['patches'])==1;candidate=inputs['patches'][0];p=ROOT/candidate['path'];assert ref(p)['sha256']==candidate['sha256'];assert ref(oldpath)['sha256']==candidate['replaces']['sha256'];a,b,c=read(oldpath),read(p),read(currentpath)
 assert len(a['patches'])==8 and len(b['patches'])==9 and len(c['patches'])==10
 assert {k:v for k,v in a.items()if k!='patches'}=={k:v for k,v in b.items()if k!='patches'}=={k:v for k,v in c.items()if k!='patches'}
 assert [stripped(x)for x in a['patches']]==[stripped(x)for x in b['patches'][:8]]==[stripped(x)for x in c['patches'][:8]]
 child=b['patches'][-1];assert child['id']=='government-native-264206-0';combined=copy.deepcopy(c);combined['patches'].append(copy.deepcopy(child));assert combined['patches'][:-1]==c['patches']and combined['patches'][-1]==child
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);url=str(currentpath.relative_to(ROOT/'3d-viewer'));entry=next(x for x in manifest['terrainPatches']if x['url']==url);assert entry['sha256']==ref(currentpath)['sha256']
 pub=module('china_current_wrapper_validator',HERE.parent/'island-detail-integration/publish.py');pub.validate_patch(combined,read(ROOT/'3d-viewer/city/data/terrain.json'))
 DOC.mkdir();LOCAL.mkdir();out=LOCAL/'terrain-central-with-china-original.json';save(out,combined);replacement=dict(candidate['replaces']);replacement.update(url=url,sha256=ref(currentpath)['sha256']);candidate.update(path=str(out.relative_to(ROOT)),sha256=ref(out)['sha256'],replaces=replacement)
 save(DOC/'neighbour-inputs.json.gz',inputs);save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'composition.json',dict(oldWrapper=ref(oldpath),historicalCandidate=ref(p),currentWrapper=ref(currentpath),currentManifest=ref(manifestpath),candidate=ref(out),oldInheritedGeometryIdentical=True,inheritedDifferencesOnlySourceOverlapMetadata=True,all10CurrentChildrenVerbatim=True,chinaChildVerbatim=True,wrapperGridVerbatim=True,unchangedPublisherValidatorPassed=True,fullAcceptance=False,publication=False,scope='Current wrapper composition and historical retained scope only; fresh full affected-actor nomination remains independent.'))
 paths=[Path(__file__),oldpath,currentpath,p,manifestpath,out,OLD/'neighbour-inputs.json.gz',HERE.parent/'island-detail-integration/publish.py',HERE.parent/'island-detail-integration/native_terrain_validation.py']
 module('china_current_wrapper_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-wrapper-original-child-composition-v1',paths,dict(uids=['landsd/264206:0'],currentWrapperCompositionPassed=True,fullAcceptance=False));print('Current wrapper and exact original child validation passed',flush=True)
if __name__=='__main__':main()
