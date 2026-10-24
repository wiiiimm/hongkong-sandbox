// CPU-only catalogue replay. This is not a rendered-device performance result.
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import * as THREE from '../../vendor/three.module.js';
import {OfficialModelLayer} from '../official-models.js';
import {streamingMetrics as metrics} from '../streaming-metrics.js';
const label=process.argv[2]||'after',root=new URL('../../',import.meta.url),manifest=JSON.parse(await readFile(new URL('city/data/manifest.json',root),'utf8'));
const models=(await Promise.all(manifest.officialModelCatalogues.map(async path=>JSON.parse(await readFile(new URL(path,root),'utf8')).models))).flat();
const stream={revision:0,lighting:{},detailedModels:new Map(),getLoadedBuilding:uid=>({uid}),setDetailedModel:async()=>true},layer=new OfficialModelLayer({stream});layer.cache.setPaused(true);for(const entry of models)layer.models.set(entry.uid,entry);
const rows=[];metrics.enabled=true;
for(const [width,height] of [[390,844],[844,390],[600,800],[1440,900],[3440,1440],[3840,2160]]){
 const c=new THREE.PerspectiveCamera(44,width/height,.5,100000);c.position.set(1500,600,1600);c.lookAt(0,0,420);c.updateMatrixWorld(true);metrics.reset();
 for(let i=0;i<40;i++)layer.plan(c,{viewportWidth:width,viewportHeight:height,now:10000+i*200,force:i===0});
 rows.push({width,height,kind:'stable',metrics:metrics.snapshot});metrics.reset();
 for(let i=0;i<40;i++){c.position.x=1500+Math.sin(i*.2)*600;c.lookAt(0,0,420);layer.plan(c,{viewportWidth:width,viewportHeight:height,now:20000+i*200});}
 rows.push({width,height,kind:'moving',metrics:metrics.snapshot});
}
const out=new URL(`../../../docs/astra-city/mobile-model-streaming/evidence/planner-${label}.json`,import.meta.url);await mkdir(new URL('.',out),{recursive:true});await writeFile(out,JSON.stringify({label,environment:'Node CPU-only catalogue replay, no rendering or physical-device inference',models:models.length,rows},null,2)+'\n');await layer.dispose();console.log(label,models.length,'models',rows.map(r=>[r.width,r.kind,r.metrics.counters.plans,r.metrics.samples.modelPlannerMs?.p95]));
