// HKS-169: lifecycle/gesture adapter over the original HKS-2 weather synthesiser.
// No copied noise beds, sound samples, or separate AudioContext implementation.
import * as originalAudio from '../audio.js';
const clamp=value=>Math.max(0,Math.min(1,Number.isFinite(value)?value:0));
export function createWeatherAudio({audio=originalAudio,documentRef=globalThis.document,activation=()=>globalThis.navigator?.userActivation}={}){
 let enabled=false,unlocked=false,masterVolume=.6,paused=false,disposed=false,pending=false,error=null,generation=0,status='muted';
 let mix={rain:0,wind:0,waves:0,fog:0},lastMix='',blocked=!!documentRef?.hidden;
 const hidden=()=>!!documentRef?.hidden;
 const snapshot=()=>({supported:audio.audioSupported(),enabled,unlocked,audible:enabled&&unlocked&&!blocked&&!disposed&&masterVolume>0&&audio.getAudioState().contextState==='running',masterVolume,status,error});
 function silence(){audio.setEnabled(false);audio.cancelThunder();return audio.suspendAudio()?.catch(()=>{});}
 async function resume(){
  const token=++generation;pending=true;status='starting';error=null;
  try{
   await audio.setEnabled(true);
   if(disposed||token!==generation||!enabled||blocked)return snapshot();
   const state=audio.getAudioState();
   if(state.contextState!=='running')throw new Error('Audio is waiting for a user gesture.');
   unlocked=true;status='playing';audio.setMasterVolume(masterVolume);audio.setWeatherMix(mix);lastMix=JSON.stringify(mix);
  }catch(cause){
   if(!disposed&&token===generation){status='error';error=cause?.message||'Weather sound could not start.';await silence();}
  }finally{if(token===generation)pending=false;}
  return snapshot();
 }
 function updateGate(){
  const next=hidden()||paused;
  if(next===blocked)return;
  blocked=next;
  if(blocked){generation++;pending=false;status=enabled?'suspended':'muted';void silence();}
  else if(enabled&&unlocked)void resume();
  else status=enabled?'gesture-required':'muted';
 }
 const visibility=()=>updateGate();documentRef?.addEventListener('visibilitychange',visibility);
 return {
  async setEnabled(on,event){
   if(disposed)return snapshot();
   if(!on){enabled=false;generation++;pending=false;status='muted';error=null;await silence();return snapshot();}
   if(!audio.audioSupported()){enabled=false;status='unsupported';error='Web Audio is unavailable in this browser.';return snapshot();}
   // Only the actual sound control may unlock audio, never a load/timer/synthetic click.
   const active=activation();
   if(!unlocked&&!(event?.isTrusted===true&&(!active||active.isActive))){status='gesture-required';return snapshot();}
   enabled=true;updateGate();
   if(blocked){status='suspended';return snapshot();}
   return resume();
  },
  setMasterVolume(value){if(disposed||!Number.isFinite(value))return snapshot();masterVolume=clamp(value);audio.setMasterVolume(masterVolume);if(masterVolume===0)audio.cancelThunder();return snapshot();},
  update(settings={},options={}){
   if(disposed)return snapshot();paused=!!(options.paused||options.suspended);updateGate();
   mix={rain:clamp(settings.rain),wind:clamp(settings.wind),waves:clamp(settings.waves),fog:clamp(settings.fog)};
   const key=JSON.stringify(mix);
   if(enabled&&unlocked&&!blocked&&!pending&&key!==lastMix){audio.setWeatherMix(mix);lastMix=key;}
   return snapshot();
  },
  thunder(close,volume=1){if(snapshot().audible)audio.thunder(close,clamp(volume));},
  cancelThunder(){audio.cancelThunder();},
  get state(){return snapshot();},
  async dispose(){if(disposed)return;disposed=true;enabled=false;generation++;pending=false;status='disposed';documentRef?.removeEventListener('visibilitychange',visibility);await audio.disposeAudio();},
 };
}
