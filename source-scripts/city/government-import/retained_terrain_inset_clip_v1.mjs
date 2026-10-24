import assert from 'node:assert/strict';
import {clipParentTriangle} from './clip_parent_terrain_triangle_v1.mjs';
export function retainOutsideInset(face, domain, cut){
 const [x0,z0,x1,z1]=domain,[a,b,c,d]=cut;
 assert(x0<=a&&a<c&&c<=x1&&z0<=b&&b<d&&d<=z1);
 const xs=face.map(p=>p[0]),zs=face.map(p=>p[2]);
 if(Math.max(...xs)<=a||Math.min(...xs)>=c||Math.max(...zs)<=b||Math.min(...zs)>=d)return [face];
 // A vertical face exactly on the cut boundary belongs to the retained side.
 // The inset's strict-interior parent capture excludes that same boundary face.
 const regions=[[x0,z0,a,z1],[c,z0,x1,z1],[a,z0,c,b],[a,d,c,z1]];
 return regions.filter(([l,t,r,u])=>l<r&&t<u).flatMap(r=>clipParentTriangle(face,r));
}
