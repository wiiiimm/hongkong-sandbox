/** Diagnose collision coverage on each upward face of one unchanged source mesh. */
import {readFileSync} from "node:fs";
import {resolve} from "node:path";
import {createHash} from "node:crypto";
import * as THREE from "../../../3d-viewer/vendor/three.module.js";
import {prepareModelCatalogue, loadOfficialModel} from "../../../3d-viewer/city/official-model-assets.js";
import {BuildingIndex} from "../../../3d-viewer/city/geo.js";

const root = resolve(import.meta.dirname, "../../..");
const batch = "government-lantau-final-14-20260921";
const stage = resolve(root, "source-scripts/city/government-import/local", batch, "candidates");
const uid = "landsd/288285:0";
const read = path => JSON.parse(readFileSync(path));
const catalogue = read(resolve(stage, "catalogue.json"));
const entry = prepareModelCatalogue(catalogue, "http://staged.local/catalogue.json").find(row => row.uid === uid);
const sourceForms = read(resolve(root, "source-scripts/city/government-import/local", batch, "source-forms.json"));
const building = sourceForms[uid].building;
const assetPath = resolve(stage, entry.asset);
const asset = readFileSync(assetPath);
if (createHash("sha256").update(asset).digest("hex") !== entry.sha256) throw Error("Source asset changed");
const lighting = {night:{value:0},activity:{value:new THREE.Vector4()},retail:{value:0},elapsed:{value:0},shimmer:{value:0}};
const model = await loadOfficialModel(entry, building, lighting, {fetcher:async()=>new Response(asset)});
const collision = new BuildingIndex([model.record]);
const {position,index} = model.record.modelGeometry;
const rows = [];
for(let i=0;i<index.length;i+=3){
 const ids=[index[i],index[i+1],index[i+2]];
 const p=ids.map(j=>[position[j*3],position[j*3+1],position[j*3+2]]);
 const ab=new THREE.Vector3(p[1][0]-p[0][0],p[1][1]-p[0][1],p[1][2]-p[0][2]);
 const ac=new THREE.Vector3(p[2][0]-p[0][0],p[2][1]-p[0][1],p[2][2]-p[0][2]);
 const cross=new THREE.Vector3().crossVectors(ab,ac);
 if(cross.y<=cross.length()*.2)continue;
 const centre=[0,1,2].map(axis=>(p[0][axis]+p[1][axis]+p[2][axis])/3);
 rows.push({triangle:i/3,centre,area:cross.length()/2,
  contacts:[.1,.5,1].map(radius=>({radius,hit:collision.collision(centre[0],centre[2],centre[1]-.05,centre[1]+.05,radius)?.uid||null}))});
}
console.log(JSON.stringify({uid,parts:collision.volumes[0].map(p=>({kind:p.kind,bottom:p.bottom,top:p.top,bounds:p.bounds})),rows},null,2));
