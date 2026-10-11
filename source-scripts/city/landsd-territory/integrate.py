"""Reuse staged official forms and the existing OSM tile baseline.
Official footprints become primary coverage; OSM names/uses survive conservative
spatial joins. Original OSM source and all official source IDs remain reproducible.
"""
import collections,json,pathlib,subprocess,sys,tarfile
from shapely.geometry import Polygon
from shapely.strtree import STRtree
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=ROOT/'3d-viewer/city/data';STAGE=OUT/'landsd-territory'
sys.path.insert(0,str(HERE.parent));from publish_tiles import publish,dump
BASELINE='5ae3900'

def main():
 stage=json.loads((STAGE/'manifest.json').read_text());manifest=json.loads((OUT/'manifest.json').read_text())
 preferred={b['uid']:b for p in (OUT/'tiles').glob('*.json') for b in json.loads(p.read_text())['buildings'] if b.get('sourceDataset')=='landsd-mui-wo'}
 tiles={};process=subprocess.Popen(['git','archive',BASELINE,'3d-viewer/city/data/tiles'],cwd=ROOT,stdout=subprocess.PIPE)
 with tarfile.open(fileobj=process.stdout,mode='r|') as archive:
  for member in archive:
   if member.isfile() and member.name.endswith('.json'):
    t=json.load(archive.extractfile(member));tiles[t['id']]=t
 if process.wait()!=0:raise RuntimeError('Could not read retained OSM baseline')
 baseline=[b for t in tiles.values() for b in t['buildings']];assert len(baseline)==117062
 official=[];heightRules={}
 for path in sorted((STAGE/'tiles').glob('*.json')):
  for b in json.loads(path.read_text())['buildings']:official.append(preferred.get(b['uid'],b))
 assert len({b['uid'] for b in official})==len(official)
 expected_ids=set(json.loads((HERE/'query-object-ids.json').read_text())['objectIds'])
 assert {b['objectId'] for b in official}==expected_ids,'Refuse an incomplete official source set'
 polys=[Polygon(b['rings'][0],b['rings'][1:]) for b in official];tree=STRtree(polys);removed=set();matches={};all_refs={};edge_overlaps=0;overlay_repairs=[]
 for k,b in enumerate(baseline):
  p=Polygon(b['rings'][0],b['rings'][1:]);overlaps=[]
  if not p.is_valid:p=p.buffer(0);overlay_repairs.append(b['uid'])
  if p.is_empty:continue
  for i in tree.query(p):
   area=p.intersection(polys[i]).area
   if area>.01:overlaps.append((int(i),area,area/p.area,area/polys[i].area))
  if any(a>=.15 or c>=.5 for _,_,a,c in overlaps):removed.add(b['uid'])
  elif overlaps:edge_overlaps+=1
  for i,area,a,c in overlaps:
   if a>=.5 or c>=.5:
    all_refs.setdefault(i,set()).update(oid for oid in [b['id'],b.get('parent')] if oid)
    if i not in matches or area>matches[i][0]:matches[i]=(area,b)
  if k and k%20000==0:print('Matched',k,'OSM forms',flush=True)
 for i,b in enumerate(official):
  if i in all_refs:b['osmRefs']=sorted(all_refs[i])
  if i in matches:
   old=matches[i][1];b['osmRef']=old['id'];b['parent']=old.get('parent',old['id'])
   if old['kind']!='yes':b['kind']=old['kind']
   if not b['name']:b['name']=old['name']
   if not b['zh']:b['zh']=old['zh']
  # Source URLs and repeated height explanations are derived from shared provenance.
  rule=manifest.get('heightRules',{}).get(b.get('heightRule'),b.get('heightRule',''))
  if rule:
   key=next((key for key,value in heightRules.items() if value==rule),None)
   if key is None:key='landsd-'+str(len(heightRules));heightRules[key]=rule
   b['heightRule']=key
  for field in ['sourceUrl','sourceAttributes','source','sourceArea','renderTopHeight']:b.pop(field,None)
  tiles.setdefault(b['tile'],{'id':b['tile'],'buildings':[],'roads':[],'parks':[]})
 for tile in tiles.values():tile['buildings']=[b for b in tile['buildings'] if b['uid'] not in removed]
 for b in official:tiles[b['tile']]['buildings'].append(b)
 source=json.loads((HERE/'manifest.json').read_text());manifest['supplementalSources']=[{'provider':'Lands Department / Hong Kong SAR Government, CSDI','datasetId':'landsd_rcd_1637211194312_35158','datasetVersion':'Building_Outline_Public_v20260819','file':source['snapshot']['file'],'sha256':source['snapshot']['compressedSHA256'],'sourceUrl':'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0','licenceUrl':'https://portal.csdi.gov.hk/csdi-webpage/doc/TNC','verification':'All retained source IDs equal the live complete ID query; existing government source download reused.'}]
 manifest['heightRules']=heightRules;manifest['licence']='CSDI terms for government geometry; ODbL-1.0 for OpenStreetMap data';manifest['sourceURL']='https://portal.csdi.gov.hk/csdi-webpage/doc/TNC'
 manifest['source']='Lands Department / Hong Kong SAR Government and OpenStreetMap contributors'
 manifest['coveragePolicy']='All verified LandsD building source records are retained as primary territory coverage. Overlapping OSM massing is replaced; matching OSM names/uses and non-overlapping source geometry remain. This is source-complete coverage, not a claim of current real-world completeness or surveyed architecture.'
 manifest['officialCoverage']={'area':'Hong Kong territory','sourceRecords':len(expected_ids),'sourceIds':len({b['id'] for b in official}),'renderedComponents':len(official),'replacedOSMForms':len(removed),'retainedOSMForms':len(baseline)-len(removed),'detailedModels':sum('modelGeometry' in b for b in official)}
 features=publish(tiles,manifest)
 report={**manifest['officialCoverage'],'cityForms':len(features),'tiles':len(tiles),'osmBaselineCommit':BASELINE,'nameUseMatches':len(matches),'retainedEdgeOverlapOSMForms':edge_overlaps,'osmOverlayRepairs':overlay_repairs,'overlapPolicy':'Replace OSM if an official form covers >=15% of the OSM footprint or the OSM form covers >=50% of an official footprint. Only >=50% overlap on either side transfers names/uses. Edge-only overlaps retained and counted.','replacedOSMUids':sorted(removed),'heightCounts':dict(collections.Counter(b['heightSource'] for b in official)),'terrainPolicy':'Government base/top fields stay absolute HKPD. The current rendered terrain is used only for missing-height/base estimates. Source/terrain conflicts are retained and reported; government heights are not silently lifted.'}
 dump(ROOT/'docs/astra-city/landsd-territory/integration.json',report);print(json.dumps({k:v for k,v in report.items() if k!='replacedOSMUids'},indent=2))
if __name__=='__main__':main()
