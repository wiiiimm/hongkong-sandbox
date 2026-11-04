import test from 'node:test';
import assert from 'node:assert/strict';
import {hourAtPoint,hourFromInput,updateClockDial} from '../clock-dial.js';
test('24-hour dial places midnight, dawn, noon and evening around the complete circle',()=>{
 for(const [x,y,h] of [[0,-1,0],[1,0,6],[0,1,12],[-1,0,18]])assert.equal(hourAtPoint(x,y),h);
 assert.ok(hourAtPoint(-.001,-1)>23.99);assert.ok(hourAtPoint(.001,-1)<.01);
});
test('exact time accepts every minute of the day and rejects invalid input',()=>{
 for(let m=0;m<1440;m++){const value=`${String(Math.floor(m/60)).padStart(2,'0')}:${String(m%60).padStart(2,'0')}`;assert.ok(Math.abs(hourFromInput(value)-m/60)<1e-12);}
 for(const value of ['', '24:00','12:60','-1:00','5:30','12:30:00'])assert.equal(hourFromInput(value),null);
});
test('clock accessibility and drawing stay in range as time lapse rounds through midnight',()=>{
 const attributes={},elements={};const dial={setAttribute:(k,v)=>attributes[k]=v,querySelector:s=>elements[s]??={setAttribute:(k,v)=>{assert.ok(Number.isFinite(v));}}};
 updateClockDial(dial,23.999,'Winding down');assert.equal(attributes['aria-valuenow'],'0');assert.match(attributes['aria-valuetext'],/^00:00/);
});
