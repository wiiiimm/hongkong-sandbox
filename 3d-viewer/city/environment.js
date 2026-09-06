import * as THREE from '../vendor/three.module.js';
import {cityLighting} from './lighting.js';
import {bindClockDial,updateClockDial,hourFromInput} from './clock-dial.js';
import {createSky,getSkyState} from './sky.js';
import {dateFromHKT,hktParts} from './sky-time.js';
import {createWeather} from './weather.js';
const $=id=>document.getElementById(id);
const WEATHER_KEYS=['rain','clouds','fog','wind','waves','snow','windFrom'];
export async function createEnvironment(options){
 const sky=await createSky({scene:options.scene,camera:options.camera});
 const weather=createWeather({scene:options.scene,camera:options.camera});
 return new CityEnvironment({...options,sky,weather});
}
class CityEnvironment {
 constructor(options){
  Object.assign(this,options);this.date=dateFromHKT(hktParts(new Date()).date,15);this.mode='manual';this.timeLapse=false;this.stargazing=false;this.astroKey='';this.lastLive=0;this.lastWeatherUI=0;this.baseSun=3;this.baseAmbient=1.9;
  this.bindUI();this.applyClock();
 }
 get hour(){return hktParts(this.date).hour;}
 get observer(){return this.getObserver();}
 setHour(hour){const date=dateFromHKT(hktParts(this.date).date,hour);if(!date)return;this.mode='manual';this.play(false);this.date=date;this.applyClock();}
 play(enabled){this.timeLapse=enabled;if(enabled)this.mode='manual';$('time-play').setAttribute('aria-pressed',String(enabled));$('time-play').textContent=enabled?'Ⅱ Pause':'▶ Time lapse';$('sky-mode').value=this.mode;}
 bindUI(){
  bindClockDial($('time-dial'),{getHour:()=>this.hour,onChange:h=>this.setHour(h)});
  $('time').addEventListener('input',e=>{const h=hourFromInput(e.target.value);if(h!==null)this.setHour(h);});
  document.querySelectorAll('[data-hour]').forEach(b=>b.addEventListener('click',()=>this.setHour(Number(b.dataset.hour))));
  $('time-play').addEventListener('click',()=>this.play(!this.timeLapse));
  $('sky-mode').addEventListener('change',e=>{const mode=e.target.value;this.play(false);this.mode=mode;if(this.mode==='live')this.date=new Date();this.applyClock();});
  $('sky-date').addEventListener('change',e=>{const date=dateFromHKT(e.target.value,this.hour);if(!date)return;this.play(false);this.mode='manual';this.date=date;this.applyClock();});
  $('sky-constellations').addEventListener('change',e=>this.sky.setConstellations(e.target.checked));this.sky.setConstellations($('sky-constellations').checked);
  $('weather-mode').addEventListener('change',e=>{this.weather.setLive(e.target.value==='live').then(()=>this.syncWeatherUI());this.syncWeatherUI();});
  $('weather-refresh').addEventListener('click',()=>{this.weather.refresh().then(()=>this.syncWeatherUI());this.syncWeatherUI();});
  for(const key of WEATHER_KEYS)$('weather-'+key).addEventListener('input',e=>{this.weather.setManual({[key]:Number(e.target.value)/(key==='windFrom'?1:100)});this.syncWeatherUI();});
  this.syncWeatherUI();
 }
 applyClock(){
  const {scene,sun,ambient,stream,water,renderer}=this,parts=hktParts(this.date),observer=this.observer;
  const key=`${Math.floor(this.date.valueOf()/5000)}|${observer.lat}|${observer.lon}`;
  if(key!==this.astroKey){this.astronomy=getSkyState(this.date,observer.lat,observer.lon);this.astroKey=key;}
  const {night,golden:gold}=this.astronomy,activityState=cityLighting(parts.hour),{quiet,activity}=activityState;
  this.lightState={...activityState,night,golden:gold};
  const nightSky=new THREE.Color('#142338').lerp(new THREE.Color('#090f1d'),quiet*.8);
  this.background=new THREE.Color('#d9e3d5').lerp(new THREE.Color('#d6c4a2'),gold*.48).lerp(nightSky,night);
  this.baseSun=3*(1-night)+(.20-.07*quiet);this.baseAmbient=1.9*(1-night)+(.54-.18*quiet);
  sun.color.set('#fff7df').lerp(new THREE.Color('#ffc080'),gold*.72).lerp(new THREE.Color('#a8bddd'),night);
  ambient.color.set('#e8f0e6').lerp(new THREE.Color('#95b9d8'),night);ambient.groundColor.set('#6c806a').lerp(new THREE.Color('#203047'),night);
  stream.lighting.night.value=night;stream.lighting.activity.value.set(activity.slice(0,4));stream.lighting.retail.value=activity[4];
  water.material.color.set('#71a8a0').lerp(new THREE.Color('#102b3d'),night);water.material.metalness=.25-night*.15;water.material.emissive.set('#1c354b');water.material.emissiveIntensity=night*(.25-.10*quiet);
  renderer.toneMappingExposure=1.05-.1*night;
  const phase=night<.05?'Daylight':night<.95?(this.astronomy.sun.bearing<180?'Dawn':'Dusk'):activityState.phase;
  this.lightState.phase=phase;
  $('time').value=parts.time;updateClockDial($('time-dial'),parts.hour,phase);$('time-output').textContent=parts.time;$('night-phase').textContent=phase;
  $('sky-mode').value=this.mode;$('sky-date').value=parts.date;
  const hh=date=>date?hktParts(date).time:'—';
  $('sky-readout').textContent=`Sunrise ${hh(this.astronomy.sunrise)} · Sunset ${hh(this.astronomy.sunset)} · Moon ${Math.round(this.astronomy.moon.fraction*100)}%`;
  $('sky-location').textContent=`${observer.title} · Hong Kong time (UTC+8)`;
  const rise=this.astronomy.sunrise?hktParts(this.astronomy.sunrise).hour*15:90,set=this.astronomy.sunset?hktParts(this.astronomy.sunset).hour*15:270;
  $('time-dial').style.setProperty('--sunrise',`${rise}deg`);$('time-dial').style.setProperty('--sunset',`${set}deg`);
  document.querySelectorAll('[data-hour]').forEach(b=>b.setAttribute('aria-pressed',String(Math.abs(Number(b.dataset.hour)-parts.hour)<.125)));
  document.body.classList.toggle('night',this.stargazing||night>.5);
  this.onClock?.(this.lightState);
 }
 syncWeatherUI(){
  const state=this.weather.state,live=state.mode==='live';$('weather-mode').value=live?'live':'manual';$('weather-manual').disabled=live||this.stargazing;$('weather-mode').disabled=this.stargazing;$('weather-refresh').disabled=this.stargazing;$('weather-refresh').hidden=!live;
  for(const key of WEATHER_KEYS){const value=state.settings?.[key]??0;$('weather-'+key).value=String(Math.round(value*(key==='windFrom'?1:100)));$('weather-'+key+'-value').textContent=key==='windFrom'?(state.settings?.windFrom==null?'Variable / unavailable':`${Math.round(value)}°`):`${Math.round(value*100)}%`;}
  const observation=state.observation;
  $('weather-status').textContent=this.stargazing?'Weather paused in Stargaze · settings preserved':live?state.status==='loading'?'Reading Hong Kong Observatory…':state.status==='live'?'Live HKO observations':state.status==='stale'?'Last HKO observation · refresh delayed':state.error||'Live observations unavailable':'Manual weather · your settings';
  $('weather-observation').textContent=this.stargazing?'Return to Explore, Walk or Fly to see and change the weather.':live&&observation?this.describeObservation(observation):live?'Weather visuals remain separate from the city clock.':'Adjust the weather to explore different conditions.';
 }
 describeObservation(observation){
  const hkt=value=>value&&Number.isFinite(Date.parse(value))?new Date(value).toLocaleString('en-HK',{timeZone:'Asia/Hong_Kong',hour12:false}):'unavailable';
  const parts=[`${observation.condition} · observed ${hkt(observation.updatedAt)} HKT.`];
  if(observation.temperature)parts.push(`${observation.temperature.station}: ${observation.temperature.value}°C (${hkt(observation.temperature.updatedAt)} HKT).`);
  if(observation.humidity)parts.push(`Humidity ${observation.humidity.value}% (${hkt(observation.humidity.updatedAt)} HKT).`);
  if(observation.wind){const w=observation.wind;parts.push(`${w.station} wind ${w.speedKmh} km/h, ${w.from==null?'variable direction':`from ${w.from}°`} (${hkt(w.updatedAt)} HKT).`);}
  else parts.push(this.weather.state.windError||'Observed wind unavailable.');
  if(observation.rainfall)parts.push(`${observation.rainfall.district}: ${observation.rainfall.millimetres} mm, ${hkt(observation.rainfall.startTime)}–${hkt(observation.rainfall.endTime)} HKT.`);
  parts.push('Clouds and visibility are visual estimates.');return parts.join(' ');
 }
 update(dt,{now,paused,reducedMotion,stargazing,position}){
  if(this.stargazing!==stargazing){this.stargazing=stargazing;this.syncWeatherUI();}
  if(!paused&&this.mode==='live'&&now-this.lastLive>1000){this.date=new Date();this.lastLive=now;this.applyClock();}
  else if(!paused&&this.timeLapse){this.date=new Date(this.date.valueOf()+dt*3600000/8);this.applyClock();}
  else {const observer=this.observer;if(!this.astroKey.endsWith(`|${observer.lat}|${observer.lon}`))this.applyClock();}
  const fx=this.weather.update(dt,{position,reducedMotion,paused,night:this.lightState.night,suspended:stargazing});this.effects=fx;
  const bg=this.background.clone();if(stargazing)bg.set('#060a15');else bg.lerp(new THREE.Color('#66777c'),(fx.cloudCover||0)*.16);
  this.scene.background=bg;
  if(!this.scene.fog?.isFogExp2)this.scene.fog=new THREE.FogExp2(bg,0);
  this.scene.fog.color.copy(bg);this.scene.fog.density=stargazing?.000012:Math.max(.000018,fx.fogDensity||0);
  this.sun.intensity=this.baseSun*(stargazing?.3:fx.sunMultiplier??1);this.ambient.intensity=this.baseAmbient*(stargazing?.45:fx.ambientMultiplier??1);
  const source=this.astronomy.sun.altitude>0?this.astronomy.sun.direction:this.astronomy.moon.altitude>0?this.astronomy.moon.direction:{x:.3,y:.55,z:-.7};
  this.sun.target.position.copy(position);this.sun.position.copy(position).addScaledVector(new THREE.Vector3(source.x,Math.max(.08,source.y),source.z).normalize(),6000);
  this.water.material.roughness=Math.max(.15,.38+this.lightState.night*.4-(fx.waveStrength||0)*.18);if(this.water.strength)this.water.strength.value=fx.waveStrength||0;
  this.sky.update({date:this.date,lat:this.observer.lat,lon:this.observer.lon,stargazing,cloudCover:stargazing?0:fx.cloudCover||0});
  document.body.classList.toggle('night',stargazing||this.lightState.night>.5);
  if(now-this.lastWeatherUI>500){this.syncWeatherUI();this.lastWeatherUI=now;}
 }
 get state(){return {mode:this.mode,date:this.date.toISOString(),hkt:hktParts(this.date),timeLapse:this.timeLapse,astronomy:this.astronomy,sky:this.sky.state,weather:this.weather.state,effects:this.effects};}
}
