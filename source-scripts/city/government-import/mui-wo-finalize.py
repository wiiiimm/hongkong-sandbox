"""Stage the script-approved Mui Wo remainder and freeze neighbour evidence; no AI."""
import gzip,hashlib,json,shutil
from pathlib import Path
import shapely
from shapely.geometry import Polygon,box
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BATCH='government-mui-wo-23-20260914';BASE=ROOT/'docs/astra-city/government-import'/BATCH;DOC=BASE/'resolution'
LOCAL=HERE/'local'/BATCH;RECOVERED=LOCAL/'recovered';STAGE=HERE/'accepted'/'government-mui-wo-7-20260914'
read=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()) if str(p).endswith('.gz') else Path(p).read_bytes())
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(v,indent=2,ensure_ascii=False)+'\n').encode();p.write_bytes(gzip.compress(raw) if str(p).endswith('.gz') else raw)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT))
def terrain_bounds(p):
 g=p['meta']['georef'];x0=g['bE']-834500;z0=816500-g['bN'];return [x0,z0,x0+(p['w']-1)*g['aE'],z0-(p['h']-1)*g['aN']]

def main():
 selection=read(BASE/'check-selection.json.gz');metrics=read(DOC/'staged-metrics.json');resolution=read(DOC/'source-resolution.json');terrain_candidates=read(DOC/'terrain-candidates.json')
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==selection['manifestSHA256']
 by_metric={r['uid']:r for r in metrics['rows']};by_resolution={r['uid']:r for r in resolution['rows']};accepted=[]
 for row in selection['rows']:
  uid=row['uid'];m=by_metric[uid];e=row['candidate']['entry'];b=row['source']['building'];native=row['native']['model'];viewer=native['matching']['viewerMatches']
  contact=not m.get('error') and not m['missingTerrain'] and m['minSurfaceGap']>=-.5 and m['minLowGap']>=-.5 and m['maxLowGap']<=1 and m['maxSamplerDelta']<=.004
  if not contact:continue
  assert by_resolution[uid].get('terrainPatch') and e['objectId']==b['objectId'] and e['buildingCSUID']==b['buildingCSUID']
  assert len(viewer)==1 and viewer[0]['uid']==uid and viewer[0]['objectId']==b['objectId'] and viewer[0]['buildingCSUID']==b['buildingCSUID']
  assert m['sourcePreserved'] and m['sourceSHA256']==e['sha256']
  assert all(m['budget'][key]<=metrics['profiles']['mobile'][key] for key in ('triangles','geometryBytes','residentBytes'))
  accepted.append(row)
 assert len(accepted)==7,{r['uid'] for r in accepted}
 ids={r['uid'] for r in accepted};STAGE.mkdir(parents=True,exist_ok=True)
 catalogue=read(RECOVERED/'catalogue.json');catalogue.update(area='Mui Wo verified original government models · September 2026',loadingPolicy='Verified exact government sources with source-TIN contact, neighbour and browser checks; no AI modelling')
 catalogue['models']=[]
 for row in accepted:
  entry=dict(row['candidate']['entry']);entry.update(priority='detail',placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,publicationApproved=True,placementReview='Exact object ID and Building CSUID with a unique viewer match; unchanged government geometry; native TIN contact and mobile runtime checks passed. No AI or architectural reconstruction.')
  source=RECOVERED/entry['asset'];assert sha(source)==entry['sha256'] and source.stat().st_size==entry['bytes'];target=STAGE/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);catalogue['models'].append(entry)
 catalogue['counts']['packedModels']=len(accepted);save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':len(accepted),'catalogues':['catalogue.json']})
 save(STAGE/'source-forms.json',[dict(r['source']['building']) for r in accepted]);save(LOCAL/'accepted-source-forms.json',{r['uid']:r['source'] for r in accepted})
 wrapper=read(terrain_candidates[0]['path']);new_children=[p for p in wrapper.get('patches',[]) if set(p.get('meta',{}).get('targetUids',[]))&ids]
 assert len(new_children)==1 and new_children[0]['meta']['targetUids']==['landsd/192816:0']
 bundle={'schemaVersion':1,'kind':'nested-source-terrain-refinement','parentTerrainURL':'city/data/terrain-mui-wo.json','parentSha256':terrain_candidates[0]['replaces']['sha256'],'patches':new_children}
 save(STAGE/'terrain-mui-wo-bundle.json',bundle)
 east=read(terrain_candidates[1]['path']);east_ids=sorted(set(east['meta']['targetUids'])&ids);assert len(east_ids)==6
 staged_terrain=[]
 for i,(candidate,patch,uids) in enumerate(((terrain_candidates[0],new_children[0],['landsd/192816:0']),(terrain_candidates[1],east,east_ids))):
  staged_terrain.append({**candidate,'uids':uids,'bounds':terrain_bounds(patch),'triangles':len(patch.get('nativeMesh',{}).get('index',[]))//3})
 save(DOC/'terrain-candidates.json',staged_terrain)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');live={m['uid'] for url in manifest.get('officialModelCatalogues',[]) for m in read(ROOT/'3d-viewer'/url)['models']};regions=[box(*p['bounds']) for p in staged_terrain];neighbours=[];hashes={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes();touched=False
  for b in json.loads(raw)['buildings']:
   poly=Polygon(b['rings'][0],b['rings'][1:]);hits=[i for i,region in enumerate(regions) if poly.intersects(region)]
   if not hits:continue
   neighbours.append({'building':b,'patchIndexes':hits,'existingNative':b['uid'] in live or bool(b.get('modelGeometry'))});touched=True
  if touched:hashes[rel(path)]=sha(path)
 save(DOC/'neighbour-inputs.json.gz',{'rows':neighbours,'inputHashes':hashes,'patches':staged_terrain,'candidateIds':sorted(ids)})
 destination='city/data/official-models/government-mui-wo-20260914/catalogue.json';east_dest='city/data/terrain-government-mui-wo-east-20260914.json'
 plan={'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':destination,'terrain':[rel(STAGE/'terrain-mui-wo-bundle.json')]}],'topLevelTerrainPatches':[{'source':terrain_candidates[1]['path'],'sha256':terrain_candidates[1]['sha256'],'destination':east_dest,'resolution':east['cell'],'area':'Mui Wo east · original government source TIN'}]}
 save(STAGE/'plan.json',plan);save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':destination,'terrain':[{'source':p['path'],'destination':('city/data/terrain-mui-wo-staged-20260914.json' if i==0 else east_dest),'resolution':patch['cell'],'area':'Mui Wo staged original terrain',**({'replaces':p['replaces']} if p.get('replaces') else {})} for i,(p,patch) in enumerate(((terrain_candidates[0],wrapper),(terrain_candidates[1],east)))],'fitBox':True,'browserUids':sorted(ids),'failureTestUids':[sorted(ids)[0]]})
 decision={'batch':BATCH,'checked':23,'accepted':sorted(ids),'held':sorted(set(by_metric)-ids),'identityPolicy':'Exact object ID + Building CSUID + unique viewer match; strict-fit exceptions remain source-identity exact.','terrainPatches':2,'neighbourForms':len(neighbours),'inputHashes':metrics['inputHashes'],'metricsSHA256':sha(DOC/'staged-metrics.json'),'resolutionSHA256':sha(DOC/'source-resolution.json'),'catalogueSHA256':sha(STAGE/'catalogue.json'),'planSHA256':sha(STAGE/'plan.json'),'aiCalls':0,'modelGeometryChanges':0,'publication':False}
 save(DOC/'decision.json',decision);print(json.dumps({'accepted':len(ids),'held':len(decision['held']),'neighbourForms':len(neighbours),'terrainPatches':2,'aiCalls':0}))
if __name__=='__main__':main()
