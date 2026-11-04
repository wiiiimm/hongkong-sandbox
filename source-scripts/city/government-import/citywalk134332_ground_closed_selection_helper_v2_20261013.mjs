/** Pure closed selection and numeric equality; no renderer import. */
import assert from 'node:assert/strict';
export function completeRegion(providerBounds,worlds,margin=1){
 assert(providerBounds.length===2&&providerBounds.every(a=>a.length===3&&a.every(Number.isFinite)));assert(margin===1);
 let x0=providerBounds[0][0],z0=providerBounds[0][2],x1=providerBounds[1][0],z1=providerBounds[1][2];assert(x0<=x1&&z0<=z1);
 for(const a of worlds){assert(a.length%3===0&&a.every(Number.isFinite));for(let i=0;i<a.length;i+=3){x0=Math.min(x0,a[i]);z0=Math.min(z0,a[i+2]);x1=Math.max(x1,a[i]);z1=Math.max(z1,a[i+2]);}}
 return [x0-margin,z0-margin,x1+margin,z1+margin];
}
export function closedFaceSelected(ids,worlds,region){
 assert(ids.length===3&&region.length===4&&region.every(Number.isFinite));assert(region[0]<=region[2]&&region[1]<=region[3]);
 let selected=false;
 for(const a of worlds){assert(ids.every(i=>Number.isInteger(i)&&i>=0&&i*3+2<a.length));const x=ids.map(i=>a[i*3]),z=ids.map(i=>a[i*3+2]);assert([...x,...z].every(Number.isFinite));if(!(Math.max(...x)<region[0]||Math.min(...x)>region[2]||Math.max(...z)<region[1]||Math.min(...z)>region[3]))selected=true;}
 return selected;
}
export function numericBufferLiteralEquality(original,literal){
 assert(original.length===literal.length);const signedZeroDifferences=[];
 for(let i=0;i<original.length;i++){assert(Number.isFinite(original[i])&&Number.isFinite(literal[i]));assert(original[i]===literal[i],'Actual buffer-to-literal coordinate mismatch at '+i);if(!Object.is(original[i],literal[i])){assert(original[i]===0&&literal[i]===0);signedZeroDifferences.push({coordinate:i,originalNegativeZero:Object.is(original[i],-0),literalNegativeZero:Object.is(literal[i],-0)});}}
 return {numericCoordinateEquality:true,bitwiseFloat64EncodingEquality:signedZeroDifferences.length===0,signedZeroDifferences};
}
