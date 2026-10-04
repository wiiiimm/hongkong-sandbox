import * as THREE from '../vendor/three.module.js';
const point=new THREE.Vector4();
/** Clipped CSS extent on both axes. Near-plane crossings conservatively fill the view. */
export function projectedBounds(box,matrix,width,height){
 let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity,behind=false,front=false;
 for(let i=0;i<8;i++){
  point.set(i&1?box.max.x:box.min.x,i&2?box.max.y:box.min.y,i&4?box.max.z:box.min.z,1).applyMatrix4(matrix);
  if(point.w<=0||point.z< -point.w){behind=true;continue;}front=true;
  const x=point.x/point.w,y=point.y/point.w;minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);
 }
 if(!front)return {width:0,height:0,pixels:0,coverage:0};
 if(behind)return {width,height,pixels:Math.max(width,height),coverage:1};
 const w=Math.max(0,Math.min(1,maxX)-Math.max(-1,minX))*width/2,h=Math.max(0,Math.min(1,maxY)-Math.max(-1,minY))*height/2;
 return {width:w,height:h,pixels:Math.max(w,h),coverage:w*h/(width*height||1)};
}
/** Catalogue-time BVH: bounded visits and candidates, nearest visible nodes first. */
export class ModelSpatialIndex {
 constructor(models){
  this.entries=new Map([...models.values()].map(entry=>[entry.uid,{entry,box:new THREE.Box3(new THREE.Vector3(...entry.worldBounds[0]),new THREE.Vector3(...entry.worldBounds[1]))}]));
  const build=rows=>{
   if(!rows.length)return null;const box=new THREE.Box3();for(const row of rows)box.union(row.box);
   if(rows.length<=8)return {box,rows};
   const size=box.getSize(new THREE.Vector3()),axis=size.x>=size.z?'x':'z';rows.sort((a,b)=>(a.box.min[axis]+a.box.max[axis])-(b.box.min[axis]+b.box.max[axis]));const middle=rows.length>>1;
   return {box,left:build(rows.slice(0,middle)),right:build(rows.slice(middle))};
  };this.root=build([...this.entries.values()]);
 }
 query(frustum,eye,{maxCandidates=256,maxNodes=1024}={}){
  const score=node=>node.box.min.distanceTo(node.box.max)/Math.max(1,node.box.distanceToPoint(eye));
  const push=node=>({node,score:score(node)}),rows=[],queue=this.root?[push(this.root)]:[];let visited=0;
  while(queue.length&&visited<maxNodes&&rows.length<maxCandidates){
   // Queue is bounded by the visit cap, independent of catalogue size.
   let best=0;for(let i=1;i<queue.length;i++)if(queue[i].score>queue[best].score)best=i;
   const {node}=queue.splice(best,1)[0];visited++;if(!frustum.intersectsBox(node.box))continue;
   if(node.rows){for(const row of node.rows)if(frustum.intersectsBox(row.box)&&rows.length<maxCandidates)rows.push(row);}else queue.push(push(node.left),push(node.right));
  }
  return {rows,visited,truncated:queue.length>0};
 }
}
