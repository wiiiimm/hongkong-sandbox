import * as THREE from '../vendor/three.module.js';
import {cityLighting} from './lighting.js';
import {bindClockDial,updateClockDial,hourFromInput} from './clock-dial.js';
import {createSky,getSkyState} from './sky.js';
import {dateFromHKT,hktParts} from './sky-time.js';
import {createWeather} from './weather.js';
import {createCityMeteors,meteorRateLabel,METEOR_DEFAULTS} from './meteors.js';
import {createWeatherEffects} from './weather-effects.js';
import {createTideData,chooseTideStation} from './tide-data.js';
import {drawTideGraph} from './tide-graph.js';
import {TIMELAPSE_DEFAULT_SPEED,normaliseTimelapseSpeed,timeCycleState,advanceTimelapse,timelapseDuration,timeCycleElapsed} from './time-cycle.js';
const $=id=>document.getElementById(id);
const WEATHER_KEYS=['rain','clouds','fog','wind','waves','snow','windFrom'];
export async function createEnvironment(options){
 const sky=await createSky({scene:options.scene,camera:options.camera});
 const weather=createWeather({scene:options.scene,camera:options.camera});
 const tides=createTideData();
 const meteors=createCityMeteors({scene:options.scene,camera:options.camera});
 const weatherEffects=createWeatherEffects({scene:options.scene,camera:options.camera,terrainHeight:options.terrainHeight});
 return new CityEnvironment({...options,sky,weather,meteors,weatherEffects,tides});
}
class CityEnvironment {
 constructor(options){
  Object.assign(this,options);this.date=dateFromHKT(hktParts(new Date()).date,15);this.mode='manual';this.timeLapse=false;this.timeLapseSpeed=TIMELAPSE_DEFAULT_SPEED;this.cycleFlags={};this.cycleTick=null;this.stargazing=false;this.astroKey='';this.lastLive=0;this.lastWeatherUI=0;this.baseSun=3;this.baseAmbient=1.9;this.tideStation='auto';
  this.bindUI();this.applyClock();
  document.addEventListener('visibilitychange',()=>{this.cycleTick=null;});
  addEventListener('pagehide',event=>{if(!event.persisted){this.meteors.dispose();this.tides.dispose();this.water.dispose();void this.weatherEffects.dispose();}});
 }
 get hour(){return hktParts(this.date).hour;}
 get observer(){return this.getObserver();}
 setHour(hour){const date=dateFromHKT(hktParts(this.date).date,hour);if(!date)return;this.mode='manual';this.play(false);this.date=date;this.applyClock();}
 get timeCycle(){return timeCycleState({enabled:this.timeLapse,speed:this.timeLapseSpeed,mode:this.mode,...this.cycleFlags});}
 play(enabled){this.cycleTick=null;this.timeLapse=!!enabled;if(enabled)this.mode='manual';this.syncTimeCycleUI();$('sky-mode').value=this.mode;}
 syncTimeCycleUI(){
  const state=this.timeCycle,key=`${state.enabled}|${state.speedMinutesPerSecond}|${state.suspendedBy}`;
  if(key===this.cycleUIKey)return;this.cycleUIKey=key;
  $('time-play').setAttribute('aria-pressed',String(state.enabled));$('time-play').textContent=state.enabled?'Ⅱ Pause':'▶ Timelapse';
  $('time-play').title=state.enabled?'Stop timelapse':'Play the city clock at the selected speed';
  const speed=state.speedMinutesPerSecond,text=`${speed} min/s`;
  $('time-lapse-speed').value=String(speed);$('time-lapse-speed').setAttribute('aria-valuetext',`${speed} simulated minutes per real second`);$('time-lapse-speed-value').textContent=text;
  const reason={'paused':'Paused while the city is paused.','stargazing':'Paused in Stargaze; return to resume.','reduced-motion':'Paused for Reduced Motion.','live':'Paused while the sky follows live time.'}[state.suspendedBy];
  $('time-lapse-speed-note').textContent=reason||`A full day in ${timelapseDuration(speed)}.`;
 }

 bindUI(){
  bindClockDial($('time-dial'),{getHour:()=>this.hour,onChange:h=>this.setHour(h)});
  $('time').addEventListener('input',e=>{const h=hourFromInput(e.target.value);if(h!==null)this.setHour(h);});
  document.querySelectorAll('[data-hour]').forEach(b=>b.addEventListener('click',()=>this.setHour(Number(b.dataset.hour))));
  $('time-play').addEventListener('click',()=>this.play(!this.timeLapse));
  $('time-lapse-speed').addEventListener('input',e=>{this.timeLapseSpeed=normaliseTimelapseSpeed(e.target.value,this.timeLapseSpeed);this.cycleTick=null;this.syncTimeCycleUI();});
  this.syncTimeCycleUI();
  $('sky-mode').addEventListener('change',e=>{const mode=e.target.value;this.play(false);this.mode=mode;if(this.mode==='live')this.date=new Date();this.applyClock();});
  $('sky-date').addEventListener('change',e=>{const date=dateFromHKT(e.target.value,this.hour);if(!date)return;this.play(false);this.mode='manual';this.date=date;this.applyClock();});
  $('sky-constellations').addEventListener('change',e=>this.sky.setConstellations(e.target.checked));this.sky.setConstellations($('sky-constellations').checked);
  $('weather-mode').addEventListener('change',e=>{const live=e.target.value==='live';Promise.allSettled([this.weather.setLive(live),this.tides.setLive(live)]).then(()=>this.syncWeatherUI());this.syncWeatherUI();});
  $('weather-refresh').addEventListener('click',()=>{Promise.allSettled([this.weather.refresh(),this.tides.refresh()]).then(()=>this.syncWeatherUI());this.syncWeatherUI();});
  $('tide-level').addEventListener('input',e=>{this.tides.setManual(Number(e.target.value));this.syncTideUI();});
  $('tide-station').addEventListener('change',e=>{this.tideStation=e.target.value;this.syncTideStation();this.syncTideUI();});
  for(const key of WEATHER_KEYS)$('weather-'+key).addEventListener('input',e=>{this.weather.setManual({[key]:Number(e.target.value)/(key==='windFrom'?1:100)});this.syncWeatherUI();});
  $('sky-meteors').checked=METEOR_DEFAULTS.enabled;$('sky-meteor-rate').value=String(METEOR_DEFAULTS.rate*100);
  const syncMeteors=()=>{const enabled=$('sky-meteors').checked,rate=Number($('sky-meteor-rate').value)/100;this.meteors.setOptions({enabled,rate});$('sky-meteor-rate').disabled=!enabled;$('sky-meteor-rate-value').textContent=enabled?meteorRateLabel(rate):'Off';};
  $('sky-meteors').addEventListener('change',syncMeteors);$('sky-meteor-rate').addEventListener('input',syncMeteors);syncMeteors();
  $('storm-lightning').addEventListener('change',e=>{this.weatherEffects.setManual({lightning:e.target.checked});this.syncEffectsUI();});
  $('storm-rate').addEventListener('input',e=>{this.weatherEffects.setManual({thunderRate:Number(e.target.value)/100});this.syncEffectsUI();});
  $('weather-volume').addEventListener('input',e=>{this.weatherEffects.setMasterVolume(Number(e.target.value)/100);this.syncEffectsUI();});
  $('weather-sound').addEventListener('click',async event=>{const pending=this.weatherEffects.setSound((!this.weatherEffects.state.sound.enabled||['error','gesture-required'].includes(this.weatherEffects.state.sound.status)),event);this.syncEffectsUI();try{await pending;}finally{this.syncEffectsUI();}});
  this.syncWeatherUI();
 }
 syncTideStation(){
  const code=this.tideStation==='auto'?chooseTideStation(this.observer).code:this.tideStation;
  if(this.tides.state.station.code!==code)this.tides.setStation(code);
 }
 syncTideUI(){
  const state=this.tides.state,live=state.mode==='live',prediction=state.prediction,usable=Number.isFinite(prediction?.heightHKPD);
  $('tide-station').value=this.tideStation;$('tide-station').disabled=this.stargazing;
  $('tide-level').value=String(live?state.restingLevelHKPD:state.manualLevelHKPD);$('tide-level-value').textContent=(live?state.restingLevelHKPD:state.manualLevelHKPD).toFixed(2)+' m';
  const status=this.stargazing?'Tide and waves paused in Stargaze':!live?'Manual sea level · simulation':state.status==='loading'?'Reading HKO tide predictions…':state.status==='live'?'HKO astronomical tide prediction':state.status==='partial'?'Partial HKO tide prediction':state.status==='stale'?'Previous prediction · refresh delayed':state.error||'Tide prediction unavailable';
  if($('tide-status').textContent!==status)$('tide-status').textContent=status;
  const station=state.station.name;
  $('tide-readout').textContent=state.restingLevelHKPD.toFixed(2)+' m HKPD'+(live&&usable?' · '+prediction.trend:'');
  const source=live&&usable?`${station} · predicted ${new Date(prediction.time).toLocaleString('en-HK',{timeZone:'Asia/Hong_Kong',hour12:false})} HKT. ${prediction.heightCD.toFixed(2)} m Chart Datum. Prediction, not a measured water level; surge is not included.`:live?'Using your saved manual sea level until a usable prediction arrives.':'Sea levels use Hong Kong Principal Datum, matching the terrain.';
  $('tide-source').textContent=source+(live&&this.tideStation==='auto'?' Automatic chooses the nearer of Cheung Chau and Quarry Bay; local tide differences remain approximate.':'');
  drawTideGraph($('tide-graph'),live?prediction:null);
 }
 syncEffectsUI(){
  const state=this.weatherEffects.state,sound=state.sound;
  $('storm-lightning').checked=state.manual.lightning;$('storm-rate').value=String(Math.round(state.manual.thunderRate*100));$('storm-rate-value').textContent=Math.round(state.manual.thunderRate*100)+'%';$('storm-rate').disabled=!state.manual.lightning;
  $('storm-note').textContent=this.stargazing?'Storms pause in Stargaze; your settings are kept.':this.weather.state.mode==='live'?'Manual storms resume when you return to Manual weather.':state.visualSuppressed?'Lightning flashes are paused; your storm settings are kept.':'Simulated storms follow your manual settings.';
  $('weather-sound').setAttribute('aria-pressed',String(sound.enabled));$('weather-sound').disabled=!sound.supported||sound.status==='starting';$('weather-sound').textContent=!sound.supported?'Weather sound unavailable':sound.status==='starting'?'Starting sound…':sound.status==='error'?'Retry weather sound':sound.status==='gesture-required'?'Enable weather sound':sound.enabled?'Mute weather sound':'Enable weather sound';
  $('weather-volume').value=String(Math.round(sound.masterVolume*100));$('weather-volume-value').textContent=Math.round(sound.masterVolume*100)+'%';
  const label=sound.error||({muted:'Sound is off.','gesture-required':'Choose Enable weather sound to start.',starting:'Starting weather sound…',playing:sound.masterVolume===0?'Volume is zero.':'Weather sound follows the current conditions.',suspended:'Weather sound is paused.',unsupported:'This browser does not support weather sound.',disposed:'Weather sound has stopped.'}[sound.status]||'Sound is off.');
  if($('weather-sound-status').textContent!==label)$('weather-sound-status').textContent=label;
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
  this.syncEffectsUI();this.syncTideUI();
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
  this.cycleFlags={paused,reducedMotion,stargazing};this.syncTimeCycleUI();
  const cycle=this.timeCycle,clockDelta=timeCycleElapsed(now,this.cycleTick,cycle);this.cycleTick={at:now,running:cycle.running};
  if(!paused&&this.mode==='live'&&now-this.lastLive>1000){this.date=new Date();this.lastLive=now;this.applyClock();}
  else if(this.timeCycle.running){this.date=new Date(advanceTimelapse(this.date.valueOf(),clockDelta,{enabled:this.timeLapse,speed:this.timeLapseSpeed,mode:this.mode,...this.cycleFlags}));this.applyClock();}
  else {const observer=this.observer;if(!this.astroKey.endsWith(`|${observer.lat}|${observer.lon}`))this.applyClock();}
  this.syncTideStation();this.tides.update({paused,suspended:stargazing});this.water.setLevel(this.tides.state.restingLevelHKPD);
  const fx=this.weather.update(dt,{position,reducedMotion,paused,night:this.lightState.night,suspended:stargazing});this.effects=fx;
  const storm=this.weatherEffects.update(dt,{settings:this.weather.state.settings,mode:this.weather.state.mode,paused,reducedMotion,suspended:stargazing,position});
  const bg=this.background.clone();if(stargazing)bg.set('#060a15');else bg.lerp(new THREE.Color('#66777c'),(fx.cloudCover||0)*.16);
  this.scene.background=bg;
  if(!this.scene.fog?.isFogExp2)this.scene.fog=new THREE.FogExp2(bg,0);
  this.scene.fog.color.copy(bg);this.scene.fog.density=stargazing?.000012:Math.max(.000018,fx.fogDensity||0);
  this.sun.intensity=this.baseSun*(stargazing?.3:fx.sunMultiplier??1);this.ambient.intensity=this.baseAmbient*(stargazing?.45:fx.ambientMultiplier??1)+storm.ambientBoost;
  const source=this.astronomy.sun.altitude>0?this.astronomy.sun.direction:this.astronomy.moon.altitude>0?this.astronomy.moon.direction:{x:.3,y:.55,z:-.7};
  this.sun.target.position.copy(position);this.sun.position.copy(position).addScaledVector(new THREE.Vector3(source.x,Math.max(.08,source.y),source.z).normalize(),6000);
  this.water.material.roughness=Math.max(.15,.38+this.lightState.night*.4-(fx.waveStrength||0)*.18);
  this.water.update(dt,{settings:this.weather.state.settings,camera:this.camera,sunDirection:source,night:this.lightState.night,paused,reducedMotion,suspended:stargazing});
  this.sky.update({date:this.date,lat:this.observer.lat,lon:this.observer.lon,stargazing,cloudCover:stargazing?0:fx.cloudCover||0});
  this.meteors.update(dt,{starFade:this.sky.state.starFade,paused,reducedMotion});
  document.body.classList.toggle('night',stargazing||this.lightState.night>.5);
  if(now-this.lastWeatherUI>500){this.syncWeatherUI();this.lastWeatherUI=now;}
 }
 get state(){return {mode:this.mode,date:this.date.toISOString(),hkt:hktParts(this.date),timeLapse:this.timeLapse,timeCycle:this.timeCycle,sunLight:{position:this.sun.position.toArray(),target:this.sun.target.position.toArray(),castShadow:this.sun.castShadow,shadowMatrix:this.sun.shadow.matrix.toArray()},astronomy:this.astronomy,sky:this.sky.state,weather:this.weather.state,effects:this.effects,meteors:this.meteors.state,storm:this.weatherEffects.state,tides:this.tides.state,water:this.water.state};}
}
