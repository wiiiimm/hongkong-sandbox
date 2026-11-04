import * as THREE from '../../../3d-viewer/vendor/three.module.js';
export function levels(g,x,z){const ys=[];for(const t of g.triangles){if(x<t.minX-1e-7||x>t.maxX+1e-7||z<t.minZ-1e-7||z>t.maxZ+1e-7)continue;const px=x-t.ax,pz=z-t.az,u=(px*(t.cz-t.az)-pz*(t.cx-t.ax))/t.det,v=((t.bx-t.ax)*pz-(t.bz-t.az)*px)/t.det;if(u>=-1e-7&&v>=-1e-7&&u+v<=1+1e-7)ys.push(t.ay+u*(t.by-t.ay)+v*(t.cy-t.ay));}return ys.sort((a,b)=>a-b).filter((y,i,ys)=>!i||Math.abs(y-ys[i-1])>.01);}
const temp=new THREE.Vector3();
export function nearest(g,point){let best=Infinity;for(const face of g.faces){face.closestPointToPoint(point,temp);best=Math.min(best,temp.distanceTo(point));if(best<.0001)break;}return best;}
