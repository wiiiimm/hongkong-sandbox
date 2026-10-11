import {createMeteorTrails} from '../meteor-trails.js';
export {METEOR_DEFAULTS,meteorRateLabel} from '../meteor-trails.js';

/** City adapter for the original HKS-85 shooting stars. Pass the existing sky's
 * starFade after sky.update(); it already knows the observer, daylight, clouds,
 * moonlight and Stargaze presentation. This module has no DOM or clock listeners.
 */
export function createCityMeteors({scene,camera,random}={}){
 const trails=createMeteorTrails({parent:scene,random,fog:false});
 let elapsed=0,paused=false,reducedMotion=false,starFade=0,radius=0,disposed=false;
 function update(dt,{starFade:fade=0,paused:hold=false,reducedMotion:reduce=false}={}){
  if(disposed)return;
  paused=!!hold;reducedMotion=!!reduce;starFade=Number.isFinite(fade)?Math.max(0,Math.min(1,fade)):0;
  radius=Math.min(85000,camera.far*.82)*.98;trails.group.position.copy(camera.position);
  // Keep one camera-centred pool just inside the catalogue sphere. World axes
  // are already horizontal; rotating with camera bearing would drag the sky.
  trails.group.visible=!paused&&!reducedMotion;
  if(reducedMotion){trails.hide();return;}
  if(paused)return;
  // Simulation date/time lapse never changes trail speed. A resumed/late frame
  // cannot produce a backlog burst even if a caller supplies a large delta.
  elapsed+=Number.isFinite(dt)?Math.max(0,Math.min(.1,dt)):0;
  trails.step(elapsed,{starFade,radius});
 }
 return {update,setOptions:trails.setOptions,
  get state(){const s=trails.state;return {...s,paused,reducedMotion,starFade,radius,elapsed,visibleTrails:trails.group.visible?s.visibleTrails:0,running:!disposed&&s.enabled&&s.rate>0&&starFade>=.55&&!paused&&!reducedMotion,disposed};},
  dispose(){if(disposed)return;disposed=true;trails.dispose();}
 };
}
