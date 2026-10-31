/** Validate source-bound BASIC ground metadata. Publication independently binds
 * the exact source/terrain and geometry/collision/visual evidence. Native detail
 * retains its original coordinates and never receives this BASIC continuation.
 */
const sha=value=>typeof value==='string'&&/^[0-9a-f]{64}$/.test(value);
export function sourceBoundBasicBottom(building){
 const minimum=building.minimum||0,bottom=building.base+minimum,hint=building.nativeFallbackGround;
 // Detailed original geometry always retains its own native coordinates.
 if(!hint||building.modelGeometry)return bottom;
 const invalid=()=>{throw new Error('Invalid source-bound BASIC ground proposal');};
 if(hint.recipe!=='original-source-basic-ground-v1'||hint.uid!==(building.uid||building.id)||!sha(hint.sourceSHA256)||!sha(hint.terrainSHA256)||!sha(hint.drawnGroundSHA256))invalid();
 if(!['Tower','Podium'].includes(building.structureType)||building.kind==='roof'||building.foundationBase!==undefined)invalid();
 if(building.baseSource!=='landsd'||building.heightSource!=='landsd'||!Number.isFinite(building.baseHeightHKPD)||!Number.isFinite(building.topHeightHKPD))invalid();
 if(building.base!==building.baseHeightHKPD||Math.abs(building.base+building.height-building.topHeightHKPD)>1e-9)invalid();
 if(!Number.isFinite(minimum)||minimum<0||hint.originalBottom!==bottom||![hint.base,hint.sourceMinimumY,bottom].every(Number.isFinite))invalid();
 // A native part that remains elevated does not authorise inventing a support.
 if(hint.base<1.2||hint.base<hint.sourceMinimumY-.5||hint.base>=bottom-.02)invalid();
 return hint.base;
}
