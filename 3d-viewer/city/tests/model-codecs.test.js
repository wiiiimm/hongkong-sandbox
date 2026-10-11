import test from 'node:test';
import assert from 'node:assert/strict';
import {loadModelCodec,modelCodecSupported} from '../model-codecs.js';

test('vendored Meshopt decoder decodes a small pinned synthetic attribute buffer',async()=>{
 assert.equal(modelCodecSupported('meshopt'),true);
 const {decoder}=await loadModelCodec('meshopt');
 const encoded=new Uint8Array(Buffer.from('oAEwAAAACAEwAAAACAEwAAAACAEwAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAgME','base64'));
 const decoded=new Uint8Array(8);decoder.decodeGltfBuffer(decoded,2,4,encoded,'ATTRIBUTES');
 assert.deepEqual([...decoded],[1,2,3,4,5,6,7,8]);
});

test('codec factory rejects undeclared codecs without loading external resources',async()=>{
 assert.equal(modelCodecSupported('none'),true);assert.equal(modelCodecSupported('draco'),true);assert.equal(modelCodecSupported('unknown'),false);
 await assert.rejects(loadModelCodec('unknown'),/Unsupported model codec/);
});

test('failed Draco decoder initialization disposes shared loader and retries fresh',async()=>{
 let constructions=0,initializations=0,disposals=0;
 class MockDRACOLoader{
  constructor(){this.instance=++constructions;}
  setDecoderPath(path){this.decoderPath=path;return this;}
  setWorkerLimit(limit){this.workerLimit=limit;return this;}
  async _initDecoder(){initializations++;if(this.instance===1)throw new Error('decoder bootstrap failed');}
  dispose(){disposals++;return this;}
 }
 const loadDraco=async()=>({DRACOLoader:MockDRACOLoader});
 const failed=await Promise.allSettled([loadModelCodec('draco',{loadDraco}),loadModelCodec('draco',{loadDraco})]);
 assert.deepEqual(failed.map(result=>result.status),['rejected','rejected']);assert.match(failed[0].reason.message,/decoder bootstrap failed/);
 assert.equal(constructions,1);assert.equal(initializations,1);assert.equal(disposals,1);
 const result=await loadModelCodec('draco',{loadDraco});
 assert.equal(constructions,2);assert.equal(initializations,2);assert.equal(disposals,1);assert.equal(result.loader.instance,2);assert.equal(result.loader.workerLimit,1);assert.match(result.loader.decoderPath,/\/vendor\/$/);
 const shared=await Promise.all([loadModelCodec('draco',{loadDraco}),loadModelCodec('draco',{loadDraco})]);
 assert.equal(shared[0].loader,result.loader);assert.equal(shared[1].loader,result.loader);assert.equal(constructions,2);
});
