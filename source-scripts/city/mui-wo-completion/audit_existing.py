"""HKS-192: classify existing coverage/conflicts before acquiring or changing models."""
import collections,gzip,hashlib,json,math,pathlib
from shapely.geometry import Polygon,Point,box
from shapely.strtree import STRtree
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/mui-wo-completion';OUT=ROOT/'3d-viewer/city/data'
def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def grid_sample(d,x,z):
 g=d['meta']['georef'];c=(x+834500-g['bE'])/g['aE'];r=(816500-z-g['bN'])/g['aN'];w=d['w']
 if not (0<=c<w-1 and 0<=r<d['h']-1):return None
 i,j=math.floor(c),math.floor(r);u,v=c-i,r-j;indices=[j*w+i,j*w+i+1,(j+1)*w+i] if u+v<=1 else [j*w+i+1,(j+1)*w+i,(j+1)*w+i+1]
 if any(d['elev'][k] is None for k in indices):return None
 a,b,e=[d['elev'][k] for k in indices]
 return a+(b-a)*u+(e-a)*v if u+v<=1 else e+(b-e)*(1-u)+(a-e)*(1-v)
def main():
 package=load(OUT/'mui-wo-buildings.json');buildings=package['buildings'];byuid={b['uid']:b for b in buildings};manifest=load(OUT/'manifest.json');live={b['uid']:b for t in manifest['tiles'] if any(b['tile']==t['id'] for b in buildings) for b in load(ROOT/'3d-viewer'/t['url'])['buildings'] if b['uid'] in byuid}
 assert set(live)==set(byuid)
 baseline=load(ROOT/'docs/astra-city/mui-wo-buildings/extension/integration.json');grids=[]
 for p in [ROOT/'docs/astra-city/mui-wo-buildings/review/model-sample/terrain-source-5m.json',*sorted((ROOT/'source-scripts/city/mui-wo-models/staged').glob('*/terrain-source-5m.json'))]:grids.append((p,load(p)))
 rows=[];counts=collections.Counter();localities=collections.defaultdict(collections.Counter)
 for row in baseline['rows']:
  b=byuid[row['uid']];current=live[b['uid']];p=Polygon(b['rings'][0],b['rings'][1:]);samples=[{'file':str(path.relative_to(ROOT)),'height':v} for path,g in grids if (v:=grid_sample(g,p.centroid.x,p.centroid.y)) is not None]
  r={**row,'centre':b['centre'],'nearestMappedLocality':b['locality'],'structureType':b['structureType'],'sourceDateStamp':b['sourceAttributes'].get('DateStamp'),'sourceTINAtCentre':samples,'liveDetailedModel':bool(current.get('modelGeometry'))};rows.append(r)
  label='TIN-covered' if samples else 'archival-DTM-only';counts['forms']+=1;counts[label]+=1
  if row['whollyBelow']:counts['whollyBelow']+=1;counts['whollyBelow:'+label]+=1
  if row['partlyBelow']:counts['partlyBelow']+=1;counts['partlyBelow:'+label]+=1
  loc=localities[b['locality']['name']];loc['forms']+=1;loc['models']+=bool(current.get('modelGeometry'));loc['whole']+=row['whollyBelow'];loc['partial']+=row['partlyBelow']
 official=[Polygon(b['rings'][0],b['rings'][1:]) for b in buildings];tree=STRtree(official);unmatched=[]
 for r in load(ROOT/'docs/astra-city/mui-wo-buildings/extension/build.json')['unmatched']:
  a,b=r['worldBounds'];p=box(a[0],a[2],b[0],b[2]);candidates=[]
  for idx in tree.query(p.buffer(10)):
   poly=official[int(idx)];obj=buildings[int(idx)];area=p.intersection(poly).area
   candidates.append({'uid':obj['uid'],'sourceGeoRefNo':obj['sourceAttributes']['GeoRefNo'],'buildingCSUID':obj['buildingCSUID'],'bboxOverlapM2':round(area,3),'sourceFootprintShare':round(area/poly.area,4),'centreDistanceM':round(p.centroid.distance(poly.centroid),3),'sourceBase':obj['baseHeightHKPD'],'sourceTop':obj['topHeightHKPD']})
  unmatched.append({**r,'nearbyOfficialCandidates':sorted(candidates,key=lambda x:-x['bboxOverlapM2'])[:8],'interpretation':'Bounding-box screening only; no footprint/model identity is inferred from spatial overlap.'})
 report={'schemaVersion':1,'sectionId':'10.6','purpose':'Current baseline classification; no new import or source geometry modification.','counts':dict(counts),'liveModels':sum(bool(b.get('modelGeometry')) for b in live.values()),'officialForms':len(buildings),'sourceBbox':package['bboxWGS84'],'localities':{k:dict(v) for k,v in localities.items()},'unmatchedSourceModels':unmatched,'conflicts':[r for r in rows if r['partlyBelow']],'sources':{'priorAudit':'docs/astra-city/mui-wo-buildings/extension/integration.json','sourceCoverage':'Retained original source terrain5m grids; centre is covered only when its exact triangle has three finite source samples.','localityNote':'Nearest retained OSM village node, not surveyed settlement boundaries.'}}
 DOC.mkdir(parents=True,exist_ok=True);(DOC/'existing-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('unmatchedSourceModels','conflicts','localities')},indent=2))
if __name__=='__main__':main()
