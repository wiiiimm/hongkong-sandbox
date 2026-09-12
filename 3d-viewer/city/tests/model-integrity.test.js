import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {sha256Hex} from '../official-model-assets.js';

test('SHA-256 verification remains available on insecure preview origins',async()=>{
 const bytes=new TextEncoder().encode('Hong Kong government model');
 assert.equal(await sha256Hex(bytes,undefined),createHash('sha256').update(bytes).digest('hex'));
});
