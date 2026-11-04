"""Promote one source-terrain-stabilised Discovery Bay model to browser acceptance."""
import gzip,hashlib,json,shutil,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SOURCE='government-lantau-discovery-native-probe-20260921';BATCH='government-lantau-discovery-native-20260921';UID='landsd/176056:0'
OLD=ROOT/'docs/astra-city/government-import'/SOURCE;DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH;STAGE=HERE/'accepted'/BATCH
def read(p):
 p=Path(p);b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(v,indent=2,sort_keys=True)+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return str(Path(p).relative_to(ROOT))
def main():
 old_selection=read(OLD/'selection.json.gz');assert [r['uid'] for r in old_selection['rows']]==[UID]
 metric=read(OLD/'metrics.json')['rows'][0];validation=read(OLD/'validation.json');neighbours=read(OLD/'neighbour-checks.json');native=read(OLD/'native-neighbour-checks.json')
 assert metric['sourcePreserved'] and metric['missingTerrain']==0 and metric['maxSamplerDelta']<=.004 and metric['minSurfaceGap']>=-1.8
 assert validation['checksPassed']==validation['loaderAccepted']==1 and validation['exceptions']==0 and validation['results'][0]['concerns']==[]
 assert neighbours['patches'][0]['blockedBy']==[] and native['blocked']==[]
 source=read(OLD/'native-proof.json');assert source['sourceSHA256']==old_selection['rows'][0]['candidate']['entry']['sha256']
 row=json.loads(json.dumps(old_selection['rows'][0]));entry=row['candidate']['entry'];entry['placementReview']='Exact unchanged government source and Building CSUID. All upward roof area is visible above its source terrain. A bounded 140×70 m patch of original government terrain resolves coarse-ground burial; parent boundary and all neighboring source forms pass. Retained basic form supports buried foundation. No AI or model geometry changes.'
 assert entry['retainsBasicForm'] and entry['proceduralWindows'] is False
 asset=STAGE/entry['asset'];asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(row['candidate']['path'],asset);assert sha(asset)==entry['sha256'];row['candidate']['path']=str(asset)
 old_patch=HERE/'local'/SOURCE/'government-native-176056-0.json';patch=STAGE/'terrain/government-native-176056-0.json';patch.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(old_patch,patch);assert sha(patch)==source['patchSHA256']
 catalogue=read(HERE/'local'/SOURCE/'catalogue.json');catalogue.update(area='Discovery Bay unchanged government building and source terrain',loadingPolicy='Original source mesh with bounded source-TIN terrain, neighbor, runtime and browser checks',counts={'packedModels':1},models=[entry]);save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
 form=dict(row['source']['building']);form['tile']=Path(row['source']['tile']).stem;save(STAGE/'source-forms.json',[form]);save(LOCAL/'source-forms.json',{UID:row['source']})
 terrain={'source':rel(patch),'sha256':sha(patch),'destination':'city/data/government-native-176056-0.json','resolution':read(patch)['cell'],'area':'Discovery Bay unchanged government source terrain'}
 save(STAGE/'plan.json',{'areas':[{'area':catalogue['area'],'catalogue':rel(STAGE/'catalogue.json'),'destination':f'city/data/official-models/{BATCH}/catalogue.json'}],'topLevelTerrainPatches':[terrain]})
 save(STAGE/'browser-config.json',{'stage':rel(STAGE)+'/','doc':rel(DOC)+'/','catalogueURL':f'city/data/official-models/{BATCH}/catalogue.json','terrain':[terrain],'fitBox':True,'browserUids':[UID],'failureTestUids':[UID]})
 save(DOC/'selection.json.gz',{'batch':BATCH,'rows':[row],'manifestSHA256':sha(ROOT/'3d-viewer/city/data/manifest.json'),'aiCalls':0});save(DOC/'terrain-candidates.json',[{'path':rel(patch),'sha256':sha(patch)}])
 save(DOC/'assembly-proof.json',{'uid':UID,'source':source,'neighborInputsSHA256':sha(OLD/'neighbour-inputs.json.gz'),'neighborChecksSHA256':sha(OLD/'neighbour-checks.json'),'nativeNeighborChecksSHA256':sha(OLD/'native-neighbour-checks.json'),'aiCalls':0,'modelGeometryChanges':0})
 for command in (["node",str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(STAGE),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json')],
  ["node",str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(STAGE),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')]):subprocess.run(command,cwd=ROOT,check=True)
 m=read(DOC/'metrics.json')['rows'][0];v=read(DOC/'validation.json')
 assert m['sourcePreserved'] and m['missingTerrain']==0 and m['maxSamplerDelta']<=.004 and m['minSurfaceGap']>=-1.8
 assert v['checksPassed']==v['loaderAccepted']==1 and v['exceptions']==0 and v['results'][0]['concerns']==[]
 save(DOC/'result.json',{'batch':BATCH,'models':1,'installedCandidates':[UID],'held':[],'failures':[],'representativeUids':[UID],'supportedSamplerUids':[],'missingRenderedGroundUids':[],'assemblyProofSHA256':sha(DOC/'assembly-proof.json'),'metricsSHA256':sha(DOC/'metrics.json'),'validationSHA256':sha(DOC/'validation.json'),'terrainSHA256':sha(patch),'aiCalls':0,'geometryChanges':0,'modelGeometryChanges':0,'publication':False})
 print(json.dumps({'staged':1,'terrainPatch':terrain['destination'],'aiCalls':0}))
if __name__=='__main__':main()
