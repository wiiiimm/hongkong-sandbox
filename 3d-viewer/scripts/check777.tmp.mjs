import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read('../data/models/plane-777.glb');
const root = doc.getRoot();
const xf=(m,x,y,z)=>[m[0]*x+m[4]*y+m[8]*z+m[12],m[1]*x+m[5]*y+m[9]*z+m[13],m[2]*x+m[6]*y+m[10]*z+m[14]];
let g=[1e9,1e9,1e9,-1e9,-1e9,-1e9], gr=[1e9,1e9,1e9,-1e9,-1e9,-1e9], body=[1e9,1e9,1e9,-1e9,-1e9,-1e9];
let tris=0, gear=0;
for(const node of root.listNodes()){const mesh=node.getMesh(); if(!mesh)continue; const wm=node.getWorldMatrix();
 for(const prim of mesh.listPrimitives()){
  const pos=prim.getAttribute('POSITION'); if(!pos)continue;
  const isGear=/^CXGear/.test(prim.getMaterial()?.getName()||'');
  const t=(prim.getIndices()?prim.getIndices().getCount():pos.getCount())/3; tris+=t; if(isGear)gear+=t;
  const el=[];
  for(let v=0;v<pos.getCount();v++){pos.getElement(v,el);const w=xf(wm,el[0],el[1],el[2]);
   for(let k=0;k<3;k++){g[k]=Math.min(g[k],w[k]);g[3+k]=Math.max(g[3+k],w[k]);
    const tgt=isGear?gr:body; tgt[k]=Math.min(tgt[k],w[k]); tgt[3+k]=Math.max(tgt[3+k],w[k]);}}
 }}
const r=a=>a.map(v=>+v.toFixed(3));
console.log('tris',Math.round(tris),'gear',Math.round(gear));
console.log('all ',r(g)); console.log('gear',r(gr)); console.log('body',r(body));
const span=g[3]-g[0];
console.log('length units',span.toFixed(3),'→ scaled to 73.9 m by loader; 1 unit =',(73.9/span).toFixed(2),'m');
console.log('gear bottom below body bottom:', gr[1]<body[1], '(gear minY',gr[1].toFixed(3),'body minY',body[1].toFixed(3),')');
console.log('wingspan units',(g[5]-g[2]).toFixed(3),'→',((g[5]-g[2])*73.9/span).toFixed(1),'m (real 64.8)');
