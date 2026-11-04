"""Stage the unchanged Pui O Substation GLB and bounded display-terrain repair."""
import gzip,hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
PROBE='government-lantau-pui-o-bounded-probe-20260921';BATCH='government-lantau-pui-o-bounded-20260921'
SRC=HERE/'local'/PROBE;STAGE=HERE/'accepted'/BATCH;DOC=ROOT/'docs/astra-city/government-import'/PROBE
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def save(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
def main():
 proof=read(DOC/'terrain-proof.json');metric=read(DOC/'metrics.json')['rows'][0];validation=read(DOC/'validation.json')['results'][0]
 assert proof['rawElevationUnchanged'] and not proof['sourceGeometryChanged'] and proof['changedRenderedVertices']<=400 and proof['maxRenderedHeightAdjustmentM']<=11
 assert metric['uid']==proof['uid']=='landsd/195308:0' and not metric.get('error') and metric['minSurfaceGap']>=-1.8 and metric['maxSamplerDelta']<.004
 assert validation['uid']==proof['uid'] and validation['concerns']==[] and validation['outcome']=='runtime-accepted-placement-unreviewed'
 selection=read(DOC/'selection.json.gz');row=selection['rows'][0];entry=row['candidate']['entry']
 source=SRC/entry['asset'];target=STAGE/entry['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);assert sha(target)==entry['sha256']
 terrain_source=SRC/'terrain-pui-o-overlap-corrected.json';terrain_target=STAGE/'terrain/terrain-pui-o-bounded-20260921.json';terrain_target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(terrain_source,terrain_target);assert sha(terrain_target)==proof['correctedSHA256']
 catalogue=read(SRC/'catalogue.json');assert len(catalogue['models'])==1 and catalogue['models'][0]['uid']==entry['uid'];save(STAGE/'catalogue.json',catalogue);save(STAGE/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']})
 form=row['source']['building'];save(STAGE/'source-forms.json',[form])
 url='city/data/terrain-pui-o-bounded-20260921.json';destination='city/data/official-models/'+BATCH+'/catalogue.json';old='city/data/terrain-pui-o.json'
 terrain={'area':'Pui O bounded source-preserving regional overlap repair','source':rel(terrain_target),'destination':url,'resolution':5,'sha256':sha(terrain_target),'replaces':{'url':old,'sha256':sha(ROOT/'3d-viewer'/old)}}
 save(STAGE/'plan.json',{'areas':[{'area':'Pui O Substation unchanged government source','catalogue':rel(STAGE/'catalogue.json'),'destination':destination}], 'topLevelTerrainPatches':[terrain]})
 save(STAGE/'browser-config.json',{'browserUids':[entry['uid']],'catalogueURL':destination,'doc':'docs/astra-city/government-import/'+BATCH+'/','failureTestUids':[entry['uid']],'fitBox':True,'stage':rel(STAGE)+'/', 'terrain':[terrain]})
 print(json.dumps({'uid':entry['uid'],'sourceSHA256':entry['sha256'],'terrainSHA256':sha(terrain_target),'staged':rel(STAGE)}))
if __name__=='__main__':main()
