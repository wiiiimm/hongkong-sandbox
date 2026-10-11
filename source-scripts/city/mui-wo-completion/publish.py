"""Bounded Mui Wo publication through the existing model/tile and arrival pipelines.
Run geometry first. Root's composite hydro publication must precede places/infra.
No overlap import, new source buildings, new renderer, or wholesale HK re-download.
"""
import argparse,importlib.util,json,pathlib,shutil,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'3d-viewer/city/data';DOC=ROOT/'docs/astra-city/mui-wo-completion'
sys.path.insert(0,str(HERE.parent))
from publish_tiles import dump

def geometry():
 spec=importlib.util.spec_from_file_location('shared_model_publisher',HERE.parent/'mui-wo-models/publish.py');shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
 expected=json.loads((DOC/'terrain-audit.json').read_text());assert expected['counts']['models']==1327 and expected['counts']['whollyBelow']==0
 shutil.copyfile(HERE/'staged-terrain-mui-wo.json',OUT/'terrain-mui-wo.json')
 report=shared.publish_models(doc=DOC)
 assert report['cityCounts']['buildings']==346115 and report['officialCoverage']['detailedModels']==1859
 assert report['counts'].get('whollyBelow',0)==0 and report['counts']['partlyBelow']==13
 return report

def places_and_infrastructure():
 import repair_arrivals,build_regional
 staged=json.loads((HERE/'places-staged.json').read_text())['places'];before={r['id']:r for r in json.loads((DOC/'arrivals-staged.json').read_text())['repairs']}
 with repair_arrivals.CityArrivalValidator() as validator:
  state=validator.request('places')['places'];walking=[(id,p) for id,p in state.items() if not p.get('aerialOnly')];checks=validator.audit([p['spawn'] for _,p in walking]);failed={id for (id,p),c in zip(walking,checks) if not c['valid']}
  if failed-set(before):raise ValueError('Unexpected regional arrival failures before Mui Wo publication: '+str(failed-set(before)))
  candidates=[before[id]['spawn'] for id in failed]+[p['spawn'] for p in staged]
  if not all(r['valid'] for r in validator.audit(candidates)):raise ValueError('Staged arrival does not match current combined terrain')
 # Reuse the original repair/publication method and its fresh-module validation.
 repair_arrivals.DOC=DOC/'arrival-publication';repair_arrivals.DOC.mkdir(exist_ok=True);repair_arrivals.main()
 package_path=OUT/'regional/islands.json';package=json.loads(package_path.read_text());byid={p['id']:p for p in package['places']}
 for place in staged:byid[place['id']]=place
 package['places']=list(byid.values());dump(package_path,package)
 build_regional.main()
 shutil.copyfile(HERE/'bridges-mui-wo.json',OUT/'bridges-mui-wo.json')
 manifest=json.loads((OUT/'manifest.json').read_text());manifest['bridgeModels']=list(dict.fromkeys([*manifest.get('bridgeModels',[]),'city/data/bridges-mui-wo.json']));dump(OUT/'manifest.json',manifest)
 with repair_arrivals.CityArrivalValidator() as validator:
  places=validator.request('places')['places'];walking=[p for p in places.values() if not p.get('aerialOnly')];checks=validator.audit([p['spawn'] for p in walking]);assert all(c['valid'] for c in checks)
  report={'passed':True,'destinations':len(places),'walking':len(walking),'aerial':len(places)-len(walking),'newIds':[p['id'] for p in staged],'repairedExistingId':'muiwo','method':'Existing repair_arrivals and build_regional publishers; only the staged regional additions, with fresh live-module and source-aware terrain/collision validation.'}
 (DOC/'place-publication.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--geometry',action='store_true');ap.add_argument('--places-and-infrastructure',action='store_true');args=ap.parse_args()
 if not (args.geometry or args.places_and_infrastructure):ap.error('Choose an explicit publication stage after shared runtime/data coordination')
 if args.geometry:geometry()
 if args.places_and_infrastructure:places_and_infrastructure()
if __name__=='__main__':main()
