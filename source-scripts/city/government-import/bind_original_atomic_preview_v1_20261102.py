"""Copy a completed unapproved original fixture, adding atomic availability only.

No geometry, support dependency, surveyed form, terrain or approval flag changes.
The resulting fixture requires fresh atomic lifecycle and browser acceptance.
"""
import argparse,copy,shutil
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_supported_catalogue_scope_v1_20261024 import verify

def atomic_catalogue(before):
 after=copy.deepcopy(before);models=after['models'];sources={m['uid']:m['sha256']for m in models};assert 1<len(models)==len(sources)<=16
 assert all(not m.get('activationGroup')and all(m.get(k)is False for k in ['publicationApproved','placementReviewed'])for m in models)
 supports={m['uid']:m['supportDependencies'][0]['uid']for m in models if m.get('supportDependencies')};assert verify(models,sources,supports)
 for m in models:m['activationGroup']=sorted(sources)
 expected=copy.deepcopy(after)
 for m in expected['models']:del m['activationGroup']
 assert expected==before
 return after

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','preview']:p.add_argument('--'+key,required=True)
 a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch;assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()and not local.exists()
 prior=HERE/'local'/a.preview;receipt,pins=authenticate(base/a.preview);assert receipt['diagnosticOnly']and not receipt['installationApproved'];refs=[Path(__file__),base/a.preview/'result.json']
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 for width in ['1280','390']:
  report=take(base/a.preview/width/'staged-browser.json');assert report['passed']and not report['errors']
 before=take(prior/'catalogue.json');after=atomic_catalogue(before);local.mkdir(parents=True);save(local/'catalogue.json',after)
 for name in ['catalogue-index.json','source-forms.json','validation-forms.json']:
  p=prior/name;take(p);shutil.copyfile(p,local/name)
 for m in after['models']:
  p=prior/m['asset'];assert digest(p.read_bytes())==m['sha256'];refs.append(p);dest=local/m['asset'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 config=take(prior/'browser-config-390.json');assert config['viewerURL']=='http://127.0.0.1:4177/city.html'
 for terrain in config['terrain']:
  p=ROOT/terrain['source'];assert digest(p.read_bytes())==terrain['sha256'];refs.append(p)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[str(manifest.relative_to(ROOT))];refs.append(manifest)
 config.update(stage=str(local.relative_to(ROOT))+'/',catalogueURL='city/data/official-models/'+a.batch+'/catalogue.json',diagnosticOnly=True,publication=False,viewportWidths=[1280,390],atomicCaptureDirectionByViewport={1280:[-1,1.8,-1],390:[-1,2.6,-1]})
 save(local/'config.json',config);lease=read(prior/'reservation.json');resources=lease['resources'];assert {'building:'+m['uid']for m in after['models']}<=set(resources)
 result=dict(uids=sorted(m['uid']for m in after['models']),sourceSHA256ByUid={m['uid']:m['sha256']for m in after['models']},sourcePreview=a.preview,leaseResources=resources,onlyCatalogueFieldAdded='activationGroup',sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=0,supportDependencyChanges=0,approvalFlagChanges=0,atomicLifecyclePassed=False,installationApproved=False,publication=False,qualification=__doc__)
 save(out/'summary.json',result);refs.extend(p for p in local.rglob('*')if p.is_file());refs.append(HERE/'original_supported_catalogue_scope_v1_20261024.py');module('atomic_fixture_only_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unapproved-original-atomic-availability-fixture-only',refs,result)
if __name__=='__main__':main()
