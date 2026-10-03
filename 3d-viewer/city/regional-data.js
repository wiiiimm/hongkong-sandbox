// Regional packages retain source geometry; browsing sections are not boundaries.
export const SURFACE_STYLES = {
 beach: '#d6c396', pier: '#b5b2a0', plaza: '#c6c2ad', pitch: '#648b69', apron: '#9ca5a0',
};
export function surfaceBounds(surface) {
 const points=surface.rings?.[0];
 if(!points?.length)return null;
 const bounds=[Infinity,Infinity,-Infinity,-Infinity];
 for(const p of points){if(p.length!==2||!p.every(Number.isFinite))return null;bounds[0]=Math.min(bounds[0],p[0]);bounds[1]=Math.min(bounds[1],p[1]);bounds[2]=Math.max(bounds[2],p[0]);bounds[3]=Math.max(bounds[3],p[1]);}
 return bounds;
}
export function validateRegionalPackage(data) {
 if(data?.schemaVersion!==1||!Array.isArray(data.surfaces)||!Array.isArray(data.places)||!Array.isArray(data.sections))throw new Error('Invalid regional detail package');
 const ids=new Set();
 for(const surface of data.surfaces){
  if(!surface.id||ids.has(surface.id)||!Object.hasOwn(SURFACE_STYLES,surface.kind)||!surface.source||!surfaceBounds(surface))throw new Error('Invalid mapped surface '+surface.id);
  ids.add(surface.id);
  for(const ring of surface.rings)if(ring.length<4||ring.some(p=>p.length!==2||!p.every(Number.isFinite))||ring[0][0]!==ring.at(-1)[0]||ring[0][1]!==ring.at(-1)[1])throw new Error('Invalid surface ring '+surface.id);
 }
 return data;
}
export function regionalPlaceMatches(places,query,region=null) {
 const needle=query.trim().toLocaleLowerCase();
 return Object.entries(places).filter(([id,p])=>(!region||p.region===region)&&(!needle||[id,p.title,p.zh,p.sectionId,p.description].some(s=>String(s||'').toLocaleLowerCase().includes(needle))));
}
