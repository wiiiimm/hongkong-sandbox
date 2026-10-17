import test from 'node:test';
import assert from 'node:assert/strict';
import {attachModelVariants,sourceMetadataHash,selectModelVariant} from '../model-variants.js';
const hash=c=>c.repeat(64);
async function fixture(){
 const source={uid:'landsd/1:0',sha256:hash('a'),worldBounds:[[0,0,0],[10,10,10]],triangles:12};
 const cat={models:[source],rootTranslation:[-834500,0,816500],crs:'EPSG:2326',verticalDatum:'Hong Kong Principal Datum'};
 const variant={uid:source.uid,runtimeVersion:1,status:'approved',sourceSha256:source.sha256,sourceMetadataSha256:await sourceMetadataHash(source,cat),variantId:hash('b'),revisionId:hash('c'),recipeSha256:hash('d'),sha256:hash('e'),tier:'balanced',codec:'meshopt',collisionPolicy:'validated-variant',lossy:true,bytes:100,glbBytes:200,decodedGeometryBytes:1000,triangles:10,indexedVertices:8,encoding:'gzip',asset:'variants/test.glb.gz',minPixels:20,maxPixels:300,worldBounds:source.worldBounds,maxPositionErrorMetres:.001,
  approval:{artifactSha256:hash('e'),gates:Object.fromEntries(['sourceIdentity','geometry','placement','visual','collision','devicePerformance'].map(g=>[g,'passed']))}};
 return {source,cat,variant};
}
test('approved source-bound optional variant inherits placement/support metadata, not arbitrary overrides',async()=>{
 const {source,cat,variant}=await fixture();source.assetURL='http://localhost/original.glb.gz';
 const [result]=await attachModelVariants([source],{...cat,models:[{uid:source.uid,sha256:source.sha256,worldBounds:source.worldBounds,triangles:source.triangles}],optimisedVariants:[{...variant,rootTranslation:[1,2,3],suppressesBuildingUids:['landsd/99:0']}]},'http://localhost/catalogue.json');
 assert.equal(result.variants.length,1);assert.equal(result.variants[0].sourceSha256,source.sha256);assert.equal(result.variants[0].suppressesBuildingUids,undefined);assert.match(result.variants[0].assetURL,/variants\/test.glb.gz\?v=/);
});
test('stale, unapproved, unsupported, cross-origin and incomplete optional entries retain enhanced source',async()=>{
 const {source,cat,variant}=await fixture();
 for(const change of [{sourceSha256:hash('f')},{sourceMetadataSha256:hash('f')},{status:'draft'},{codec:'unknown'},{lossy:'yes'},{asset:'https://elsewhere.test/x.glb.gz'},{approval:{}},{worldBounds:[[20,0,0],[30,10,10]]}]){
  const [result]=await attachModelVariants([source],{...cat,optimisedVariants:[{...variant,...change}]},'http://localhost/catalogue.json');assert.equal(result.variants.length,0);assert.equal(selectModelVariant(result,{pixels:100}),result);
 }
 const modified={...source,supportDependencies:['landsd/2:0']};
 const [stale]=await attachModelVariants([modified],{...cat,models:[modified],optimisedVariants:[variant]},'http://localhost/catalogue.json');assert.equal(stale.variants.length,0);
});
test('Base downloads nothing; screen size and user/device preference choose eligible tiers',async()=>{
 const {source,cat,variant}=await fixture();
 const [result]=await attachModelVariants([source],{...cat,optimisedVariants:[variant,{...variant,variantId:hash('f'),tier:'high',minPixels:200,maxPixels:1000}]},'http://localhost/catalogue.json');
 assert.equal(selectModelVariant(result,{quality:'base',pixels:100}),null);
 assert.equal(selectModelVariant(result,{quality:'auto',profile:'mobile',pixels:250}).tier,'balanced');
 assert.equal(selectModelVariant(result,{quality:'high',pixels:250}).tier,'high');
 assert.equal(selectModelVariant(result,{quality:'high',pixels:100}).tier,'balanced');
 assert.equal(selectModelVariant(result,{quality:'high',pixels:1500}),result);
 assert.equal(selectModelVariant(result,{quality:'lightweight',pixels:100}),result);
 assert.equal(selectModelVariant(result,{quality:'high',pixels:210,current:result.variants[0]}).tier,'balanced');
});
