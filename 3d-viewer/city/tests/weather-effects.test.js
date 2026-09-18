import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from '../../vendor/three.module.js';
import * as original from '../../audio.js';
import {createWeatherAudio} from '../weather-audio.js';
import {createWeatherEffects,normaliseStorm,lightningChannel,MIN_STRIKE_INTERVAL} from '../weather-effects.js';
class Param{
 constructor(){this.value=0;this.calls=[];}
 setTargetAtTime(...v){this.calls.push(['target',...v]);this.value=v[0];}
 setValueAtTime(...v){this.calls.push(['value',...v]);this.value=v[0];}
 exponentialRampToValueAtTime(...v){this.calls.push(['exponential',...v]);this.value=v[0];}
 linearRampToValueAtTime(...v){this.calls.push(['linear',...v]);this.value=v[0];}
 cancelScheduledValues(...v){this.calls.push(['cancel',...v]);}
}
class AudioNode{
 constructor(kind){this.kind=kind;this.gain=new Param();this.frequency=new Param();this.Q=new Param();this.connections=[];this.stopped=false;}
 connect(node){this.connections.push(node);return node;}
 disconnect(){this.connections=[];this.disconnected=true;}
 start(at){this.startAt=at;}
 stop(at){this.stopAt=at;this.stopped=true;if(at===undefined)this.onended?.();}
}
class AudioContextMock{
 static instances=[];static failure=null;static deferred=null;
 constructor(){this.sampleRate=1000;this.currentTime=10;this.state='suspended';this.destination={};this.nodes=[];AudioContextMock.instances.push(this);}
 node(kind){const node=new AudioNode(kind);this.nodes.push(node);return node;}
 createGain(){return this.node('gain');}createOscillator(){return this.node('oscillator');}createBiquadFilter(){return this.node('filter');}createBufferSource(){return this.node('source');}
 createBuffer(_channels,length){return {getChannelData:()=>new Float32Array(length)};}
 resume(){if(AudioContextMock.failure)return Promise.reject(AudioContextMock.failure);if(AudioContextMock.deferred)return AudioContextMock.deferred;this.state='running';return Promise.resolve();}
 suspend(){this.state='suspended';return Promise.resolve();}
 close(){this.state='closed';for(const node of this.nodes)if(['source','oscillator'].includes(node.kind))node.stop();return Promise.resolve();}
}
function documentMock(){const listeners=new Set();return {hidden:false,addEventListener(_name,fn){listeners.add(fn);},removeEventListener(_name,fn){listeners.delete(fn);},visibility(hidden){this.hidden=hidden;for(const fn of listeners)fn();},get listeners(){return listeners.size;}};}
async function withAudio(fn){const saved=globalThis.AudioContext;globalThis.AudioContext=AudioContextMock;AudioContextMock.instances=[];AudioContextMock.failure=null;AudioContextMock.deferred=null;try{await original.disposeAudio();await fn();}finally{await original.disposeAudio();globalThis.AudioContext=saved;}}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
function audioSpy(){let initialised=false,enabled=false,contextState='none';const calls=[];return {calls,audioSupported:()=>true,getAudioState:()=>({initialised,enabled,contextState}),setEnabled(on){calls.push(['enabled',on]);enabled=on;if(on){initialised=true;contextState='running';}return Promise.resolve();},setWeatherMix(m){calls.push(['mix',{...m}]);},setMasterVolume(v){calls.push(['volume',v]);},cancelThunder(){calls.push(['cancel']);},suspendAudio(){contextState=initialised?'suspended':'none';return Promise.resolve();},thunder(close,volume){calls.push(['thunder',close,volume]);},disposeAudio(){initialised=false;contextState='none';return Promise.resolve();}};}

test('original audio retains its weather mix, volume, engine exports and thunder envelopes',()=>withAudio(async()=>{
 await original.setEnabled(true);assert.equal(original.getAudioState().contextState,'running');assert.equal(original.isEnabled(),true);
 const ctx=AudioContextMock.instances[0];original.setMasterVolume(.7);original.setMasterVolume(NaN);assert.equal(original.getAudioState().masterVolume,.7);
 original.setWeatherMix({rain:.5,wind:.4,waves:.3,fog:1});
 const targets=ctx.nodes.flatMap(n=>n.gain.calls.filter(c=>c[0]==='target').map(c=>c[1]));for(const v of [.08,.14,.03])assert.ok(targets.some(n=>Math.abs(n-v)<1e-8));
 original.setEngine(.5);original.setUfoEngine(.3,.2);assert.ok(ctx.nodes.filter(n=>n.kind==='oscillator').length>=11);
 original.thunder(true);assert.equal(original.getAudioState().activeThunderSources,2);original.thunder(false,.5);assert.equal(original.getAudioState().activeThunderSources,3);
 const voice=ctx.nodes.find(n=>n.kind==='source'&&n.startAt>10);assert.ok(voice.startAt>=10.25&&voice.startAt<=10.75);assert.ok(voice.stopAt>voice.startAt+2.2);
 original.cancelThunder();assert.equal(original.getAudioState().activeThunderSources,0);assert.equal(voice.disconnected,true);
 await original.suspendAudio();assert.equal(ctx.state,'suspended');await original.initAudio();assert.equal(ctx.state,'running');assert.equal(AudioContextMock.instances.length,1);
 await original.disposeAudio();assert.equal(ctx.state,'closed');assert.equal(original.getAudioState().initialised,false);await original.initAudio();assert.equal(AudioContextMock.instances.length,2);
}));
test('sound never creates a context without a trusted, active user gesture',()=>withAudio(async()=>{
 const doc=documentMock();let active=false;const audio=createWeatherAudio({documentRef:doc,activation:()=>({isActive:active})});
 await audio.setEnabled(true);await audio.setEnabled(true,{isTrusted:false});await audio.setEnabled(true,{isTrusted:true});assert.equal(AudioContextMock.instances.length,0);assert.equal(audio.state.status,'gesture-required');
 active=true;await audio.setEnabled(true,{isTrusted:true});assert.equal(AudioContextMock.instances.length,1);assert.equal(audio.state.audible,true);assert.equal(audio.state.status,'playing');
 audio.setMasterVolume(0);assert.equal(audio.state.audible,false);audio.setMasterVolume(.5);audio.update({rain:1,wind:.6,waves:.5,fog:0});audio.thunder(true);assert.equal(original.getAudioState().activeThunderSources,2);
 await audio.setEnabled(false);assert.equal(audio.state.enabled,false);assert.equal(original.getAudioState().activeThunderSources,0);assert.equal(AudioContextMock.instances[0].state,'suspended');
 await audio.setEnabled(true);assert.equal(audio.state.audible,true);assert.equal(AudioContextMock.instances.length,1);await audio.dispose();assert.equal(doc.listeners,0);assert.equal(audio.state.status,'disposed');
}));
test('hidden tabs and paused/stargaze states cancel thunder and suspend audio without losing preference',()=>withAudio(async()=>{
 const doc=documentMock(),audio=createWeatherAudio({documentRef:doc,activation:()=>({isActive:true})});await audio.setEnabled(true,{isTrusted:true});audio.thunder(true);
 doc.visibility(true);assert.equal(audio.state.status,'suspended');assert.equal(audio.state.enabled,true);assert.equal(audio.state.audible,false);assert.equal(original.getAudioState().activeThunderSources,0);
 doc.visibility(false);await tick();assert.equal(audio.state.audible,true);audio.update({rain:1},{suspended:true});assert.equal(audio.state.audible,false);audio.update({rain:1},{paused:false,suspended:false});await tick();assert.equal(audio.state.audible,true);await audio.dispose();
}));
test('resume failures are reported and later gesture retries recover; late resumes cannot revive disposal',()=>withAudio(async()=>{
 const audio=createWeatherAudio({documentRef:documentMock(),activation:()=>({isActive:true})});AudioContextMock.failure=new Error('Autoplay denied');await audio.setEnabled(true,{isTrusted:true});assert.equal(audio.state.status,'error');assert.match(audio.state.error,/Autoplay denied/);assert.equal(audio.state.audible,false);
 AudioContextMock.failure=null;await audio.setEnabled(true,{isTrusted:true});assert.equal(audio.state.status,'playing');
 await audio.setEnabled(false);let resolve;AudioContextMock.deferred=new Promise(r=>resolve=r);const pending=audio.setEnabled(true);await audio.dispose();resolve();await pending;assert.equal(audio.state.status,'disposed');assert.equal(audio.state.audible,false);
}));
test('forked channel retains finite bounded geometry and reaches the supplied terrain endpoint',()=>{
 const data=lightningChannel({x:12000,z:-5000,ground:187.2,top:1300,random:()=>.5});assert.equal(data.length,14*6);assert.deepEqual([...data.slice(-3)],[12000,Math.fround(187.2),-5000]);assert.ok([...data].every(Number.isFinite));
 let seed=6;const rnd=()=>((seed=Math.imul(seed,1664525)+1013904223)>>>0)/4294967296;
 const forks=lightningChannel({x:10,z:10,ground:0,random:rnd});assert.ok(forks.length>84&&forks.length<1000);assert.ok([...forks].every(Number.isFinite));
 assert.deepEqual(normaliseStorm({lightning:true,thunderRate:2}),{lightning:true,thunderRate:1});assert.equal(normaliseStorm({thunderRate:NaN}).thunderRate,.4);
});
test('manual storms respect rate limits, live/manual restoration and reduced-motion suppression',async()=>{
 const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera();camera.position.set(0,100,500);camera.lookAt(0,200,-1000);const doc=documentMock(),spy=audioSpy();
 const fx=createWeatherEffects({scene,camera,terrainHeight:()=>32,random:()=>.5,documentRef:doc,audioOptions:{audio:spy,activation:()=>({isActive:true})}});await fx.setSound(true,{isTrusted:true});fx.setManual({lightning:true,thunderRate:1});const settings={rain:.8,wind:.6,waves:.7,fog:.2};
 fx.update(0,{settings,mode:'manual'});assert.equal(fx.triggerStrike(),true);assert.equal(fx.triggerStrike(),false);assert.equal(fx.state.lastStrike.position.y,32);assert.ok(fx.update(.01,{settings}).ambientBoost>0);
 for(let i=0;i<15;i++)fx.update(.25,{settings});assert.equal(fx.triggerStrike(),false);fx.update(.25,{settings});assert.equal(fx.triggerStrike(),true);assert.equal(MIN_STRIKE_INTERVAL,4);
 fx.update(.1,{settings,mode:'live'});assert.equal(fx.state.active,false);assert.equal(fx.state.flash,0);assert.equal(fx.triggerStrike(),false);assert.equal(fx.state.manual.lightning,true);assert.equal(fx.state.source,'Manual storm simulation');
 fx.update(.1,{settings,mode:'manual',reducedMotion:true});for(let i=0;i<20;i++)fx.update(.25,{settings,reducedMotion:true});assert.equal(fx.state.flash,0);assert.equal(scene.getObjectByName('Forked lightning').visible,false);assert.equal(fx.state.visualSuppressed,true);assert.ok(spy.calls.some(c=>c[0]==='thunder'));
 const count=fx.state.strikes;for(let i=0;i<30;i++)fx.update(.25,{settings,paused:true});assert.equal(fx.state.strikes,count);assert.equal(fx.state.sound.audible,false);
 fx.update(.1,{settings,suspended:true});assert.equal(fx.state.active,false);doc.visibility(true);assert.equal(fx.triggerStrike(),false);
 await fx.dispose();assert.equal(scene.getObjectByName('City storm · manual simulation'),undefined);assert.equal(doc.listeners,0);assert.deepEqual(fx.update(.1),{ambientBoost:0,flash:0});
});
