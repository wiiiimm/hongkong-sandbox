// Presentation controls, not measured visibility or air-quality observations.
export const DEFAULT_HAZE=.35;
export const HAZE_STORAGE_KEY='astra-city-atmospheric-haze-v1';
export const CLEAR_WEATHER_DENSITY=Math.sqrt(-Math.log(.02))/30000;
export function normaliseHaze(value,fallback=DEFAULT_HAZE){
 if(value===null||value===undefined||value==='')return fallback;
 const n=Number(value);return Number.isFinite(n)?Math.max(0,Math.min(1,n)):fallback;
}
export function readHaze(storage){try{return normaliseHaze(storage.getItem(HAZE_STORAGE_KEY));}catch{return DEFAULT_HAZE;}}
export function saveHaze(storage,value){try{storage.setItem(HAZE_STORAGE_KEY,String(normaliseHaze(value)));}catch{/* Private/blocked storage must not break the live control. */}}
// Scene fog is an artistic distance response to reported visibility, not a pollutant reading.
export function hazeFromVisibility(metres){return Number.isFinite(metres)&&metres>0?normaliseHaze(.5*Math.sqrt(30000/metres)):null;}
export function hazePresentation({amount=DEFAULT_HAZE,weatherDensity=CLEAR_WEATHER_DENSITY,stargazing=false,visibilityMetres=null}={}){
 const observed=hazeFromVisibility(visibilityMetres),haze=observed??normaliseHaze(amount),strength=4*haze*haze;
 const additionalWeatherFog=stargazing?0:Math.max(0,(Number.isFinite(weatherDensity)?weatherDensity:CLEAR_WEATHER_DENSITY)-CLEAR_WEATHER_DENSITY);
 return {haze,source:observed===null?'manual':'visibility',fogDensity:observed===null?(stargazing?.000012:CLEAR_WEATHER_DENSITY)*strength+additionalWeatherFog:Math.sqrt(-Math.log(.02))/visibilityMetres,
  limitingMagnitude:Math.max(1,6-haze*(stargazing?1.4:6.4)),nightClearWeight:Math.max(0,1-2*haze),nightGlowWeight:Math.max(0,2*haze-1)*.25};
}
