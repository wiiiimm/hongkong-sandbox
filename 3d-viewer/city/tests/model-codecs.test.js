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
