// Playback policy for the existing CityEnvironment clock; this is not another clock.
export const TIMELAPSE_DEFAULT_SPEED=7.5;
export const TIMELAPSE_MIN_SPEED=1;
export const TIMELAPSE_MAX_SPEED=120;
export function normaliseTimelapseSpeed(value,fallback=TIMELAPSE_DEFAULT_SPEED){
 if((typeof value!=='number'&&typeof value!=='string')||String(value).trim()===''||!Number.isFinite(Number(value)))return fallback;
 return Math.max(TIMELAPSE_MIN_SPEED,Math.min(TIMELAPSE_MAX_SPEED,Number(value)));
}
export function timeCycleState({enabled=false,speed=TIMELAPSE_DEFAULT_SPEED,mode='manual',paused=false,reducedMotion=false,stargazing=false}={}){
 const speedMinutesPerSecond=normaliseTimelapseSpeed(speed);
 const suspendedBy=!enabled?null:mode==='live'?'live':paused?'paused':stargazing?'stargazing':reducedMotion?'reduced-motion':null;
 return {enabled:!!enabled,running:!!enabled&&!suspendedBy,speedMinutesPerSecond,dayDurationSeconds:1440/speedMinutesPerSecond,suspendedBy};
}
export function advanceTimelapse(instant,dt,options){
 const state=timeCycleState(options);
 if(!state.running||!Number.isFinite(dt)||dt<=0||!Number.isFinite(instant))return instant;
 const next=instant+dt*state.speedMinutesPerSecond*60000;
 // Date arithmetic retains the civil date across full days, months and leap years.
 return Number.isFinite(next)&&Math.abs(next)<=8640000000000000?next:instant;
}
export function timelapseDuration(speed){
 const total=Math.round(1440/normaliseTimelapseSpeed(speed)),minutes=Math.floor(total/60),seconds=total%60;
 return minutes?`${minutes}m${seconds?' '+seconds+'s':''}`:`${seconds}s`;
}

// Use the renderer's monotonic timestamp, independently of its capped physics dt.
// Requiring two running samples prevents elapsed pause time becoming a clock jump.
export function timeCycleElapsed(now,previous,state){
 if(!Number.isFinite(now)||!previous||!Number.isFinite(previous.at)||!previous.running||!state.running||now<previous.at)return 0;
 return (now-previous.at)/1000;
}
