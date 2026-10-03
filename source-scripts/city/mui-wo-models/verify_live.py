"""Compare every live form's immutable source identity/geometry against ff68cf1.
The existing geometry helper is checked separately in the focused Node test.
"""
import collections,hashlib,json,pathlib,subprocess,tarfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'3d-viewer/city/data';DOC=ROOT/'docs/astra-city/mui-wo-buildings/extension'
IMMUTABLE=('id','uid','tile','objectId','buildingCSUID','structureType','baseHeightHKPD','topHeightHKPD','rings','centre','heightSource')
def signature(b):return hashlib.sha256(json.dumps({k:b.get(k) for k in IMMUTABLE},sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 live={};official_ids=set();model_count=0;old_model_count=0;old_counts=collections.Counter();new_counts=collections.Counter();changed_elevations=[]
 for path in (OUT/'tiles').glob('*.json'):
  tile=json.loads(path.read_text())
  for b in tile['buildings']:
   assert b['uid'] not in live;live[b['uid']]=(signature(b),b['base'],b['height'],b.get('baseSource'));new_counts[b['heightSource']]+=1;model_count+='modelGeometry' in b
   if b['id'].startswith('landsd/'):official_ids.add(b['objectId'])
 expected_ids=set(json.loads((ROOT/'source-scripts/city/landsd-territory/query-object-ids.json').read_text())['objectIds']);assert official_ids==expected_ids
 checked=set();process=subprocess.Popen(['git','archive','ff68cf1','3d-viewer/city/data/tiles'],cwd=ROOT,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=process.stdout,mode='r|') as archive:
  for member in archive:
   if member.isfile() and member.name.endswith('.json'):
    for b in json.load(archive.extractfile(member))['buildings']:
     uid=b['uid'];checked.add(uid);assert uid in live;new,base,height,base_source=live[uid];assert new==signature(b),uid
     old_counts[b['heightSource']]+=1;old_model_count+='modelGeometry' in b
     if base!=b['base'] or height!=b['height']:
      assert b['baseHeightHKPD'] is None and b['topHeightHKPD'] is None and base_source=='terrain-estimated';changed_elevations.append({'uid':uid,'beforeBase':b['base'],'afterBase':base,'height':height})
 assert process.wait()==0;assert checked==set(live);assert old_counts==new_counts
 report={'result':'passed','baselineCommit':'ff68cf1','cityFormsBefore':len(checked),'cityFormsAfter':len(live),'officialSourceIds':len(official_ids),'sourceIdSetExactlyPreserved':True,'immutableSourceGeometryAndAttributesExactlyPreserved':list(IMMUTABLE),'modelsBefore':old_model_count,'modelsAfter':model_count,'heightClassCounts':dict(new_counts),'estimatedOnlyBaseChanges':changed_elevations,'recordedElevationChanges':0,'manifestSha256':hashlib.sha256((OUT/'manifest.json').read_bytes()).hexdigest()}
 (DOC/'live-preservation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='estimatedOnlyBaseChanges'},indent=2))
if __name__=='__main__':main()
