/** UNEXECUTED pure compact projection verifier; no renderer/terrain import. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
const sha=b=>createHash('sha256').update(b).digest('hex');
export function meshBinding(mesh){
 assert.deepEqual(Object.keys(mesh).sort(),['index','position']);const p=mesh.position,ix=mesh.index;
 assert(Array.isArray(p)&&Array.isArray(ix)&&p.length>0&&ix.length>0&&p.length%3===0&&ix.length%3===0);
 assert(p.every(v=>typeof v==='number'&&Number.isFinite(v)));assert(ix.every(v=>Number.isInteger(v)&&v>=0&&v<p.length/3&&v<=0xffffffff));
 const pb=Buffer.alloc(p.length*8),ib=Buffer.alloc(ix.length*4);
 p.forEach((v,i)=>pb.writeDoubleLE(v,i*8));ix.forEach((v,i)=>ib.writeUInt32LE(v,i*4));
 // Indexed XYZ stream includes all three coordinates of each vertex occurrence.
 const indexed=Buffer.alloc(ix.length*3*8);ix.forEach((v,i)=>{for(let k=0;k<3;k++)indexed.writeDoubleLE(p[v*3+k],(i*3+k)*8);});
 const head=Buffer.alloc(16);head.writeBigUInt64LE(BigInt(p.length),0);head.writeBigUInt64LE(BigInt(ix.length),8);
 const h=createHash('sha256');h.update(Buffer.from('polyu-native-mesh-f64-le-u32-le-v1\0'));h.update(head);h.update(pb);h.update(ib);
 return {completePositionVertices:p.length/3,completeIndexedFaces:ix.length/3,positionBinary64LE_SHA256:sha(pb),indexUint32LE_SHA256:sha(ib),completeMeshTupleSHA256:h.digest('hex'),completeIndexedRawBinary64LE_SHA256:sha(indexed),tupleEncoding:'polyu-native-mesh-f64-le-u32-le-v1',unusedPositionsIncluded:true,signedZeroBitsIncluded:true};
}
export function verifyProjection(projection,sourceRef,expected,preserved){
 assert.equal(projection.schema,'compact-polyu-parent-cell-runtime-mesh-v1');assert.deepEqual(projection.sourceNominationRef,sourceRef);
 assert.equal(projection.physicalAccepted,false);assert.equal(projection.installationApproved,false);
 assert.deepEqual(projection.meshBinding,expected);assert.deepEqual(projection.preservationCounts,preserved);assert.deepEqual(meshBinding(projection.newNativeMesh),expected);
 return projection;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){const v=JSON.parse(readFileSync(0));verifyProjection(v.projection,v.sourceRef,v.expected,v.preserved);console.log('pure projection verification PASS');}
