// Shared original viewer palette; sun altitude is in degrees above the horizon.
import * as THREE from './vendor/three.module.js';
const S01=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t);};

// sun-altitude → sky colour: deep night, warm dawn/dusk, clear blue day.
// Chained smoothstep lerps keep the transitions band-free; palette is tunable.
export function skyColour(altD, onPaper) {
  const P = onPaper
    ? { day: 0xcfe0f1, dusk: 0xf0a45f, night: 0x121a26 }   // paper: pale blue / soft amber / slate night
    : { day: 0x6ea3d8, dusk: 0xf4813c, night: 0x070a12 };  // dark: clear blue / warm dusk / deep night
  const c = new THREE.Color(P.night);
  c.lerp(new THREE.Color(P.dusk), 0.97 * S01((altD + 14) / 10));   // −14° night → −4° dusk (kept 3% night-blue so the whole dome never goes flat orange)
  c.lerp(new THREE.Color(P.day), S01((altD - 4) / 8));             // +4° dusk → +12° full day (wide golden hour — intentional)
  return c;
}

// Clarity should deepen the night after civil twilight, not erase golden hour.
export const skyNightBlend=altitude=>1-S01((altitude+14)/8);
