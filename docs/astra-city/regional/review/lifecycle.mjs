import * as THREE from '../../../../3d-viewer/vendor/three.module.js';
import {RegionalDetail} from '../../../../3d-viewer/city/regional.js';
import {writeFile} from 'node:fs/promises';
let release;const response=new Promise(resolve=>release=resolve),oldFetch=globalThis.fetch;
globalThis.fetch=()=>response;
const scene=new THREE.Scene(),detail=new RegionalDetail({scene,sampler:{height:()=>2}});
try{
 const loading=detail.load('controlled.json');detail.dispose();
 release({ok:true,json:async()=>({schemaVersion:1,places:[],sections:[],surfaces:[{id:'controlled-polygon',kind:'plaza',source:'https://www.openstreetmap.org/way/1',rings:[[[0,0],[40,0],[40,40],[0,40],[0,0]]]}]})});await loading;
 const result={scenario:'dispose while a regional fetch is pending, then resolve the response',sceneChildren:scene.children.length,detachedGroupChildren:detail.group.children.length,cachedTiles:detail.cache.size,stats:detail.stats,expected:'No geometry or caches should be rebuilt after disposal'};
 await writeFile(new URL('lifecycle.json',import.meta.url),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}finally{globalThis.fetch=oldFetch;detail.dispose();}
