import test from 'node:test';
import assert from 'node:assert/strict';
import {StreamingMetrics} from '../streaming-metrics.js';
test('measurements retain bounded samples and lifetime totals without disabled work',()=>{
 const m=new StreamingMetrics({enabled:true,capacity:4});for(let i=1;i<=10;i++)m.record('frame',i);m.count('loads',2);
 assert.deepEqual(m.snapshot.samples.frame,{count:10,retained:4,total:55,max:10,median:8,p95:9});assert.equal(m.snapshot.counters.loads,2);m.reset();assert.deepEqual(m.snapshot.samples,{});
 const off=new StreamingMetrics();off.record('frame',3);off.count('loads');assert.deepEqual(off.snapshot.samples,{});assert.deepEqual(off.snapshot.counters,{});
});
