import * as THREE from './vendor/three.module.js';

// Original viewer's tileable cloud/shore texture, extracted without changing its defaults.
export function createWaterNoiseTexture({documentImpl=globalThis.document,random=Math.random}={}) {
  const S = 256, c = documentImpl.createElement('canvas'); c.width = c.height = S;
  const x = c.getContext('2d');
  x.fillStyle = '#000'; x.fillRect(0, 0, S, S);
  for (let i = 0; i < 26; i++) {
    const px = random() * S, py = random() * S, r = 26 + random() * 58;
    for (const ox of [-S, 0, S]) for (const oy of [-S, 0, S]) {
      const g = x.createRadialGradient(px + ox, py + oy, 0, px + ox, py + oy, r);
      g.addColorStop(0, 'rgba(255,255,255,.5)'); g.addColorStop(1, 'rgba(255,255,255,0)');
      x.fillStyle = g; x.fillRect(0, 0, S, S);
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}

// Original intertidal tint and foam passes. Caller supplies vWpos and uniforms.
export function applyShorelineShader(sh) {
 sh.fragmentShader=sh.fragmentShader.replace('#include <dithering_fragment>',`#include <dithering_fragment>
        { float d = vWpos.y - uWaterY; float wet = step(0.0, d) * (1.0 - smoothstep(0.0, uBand, d));
          gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.29,0.33,0.31), wet * 0.5 * uWetAmt);
          float foam = step(0.0, d) * (1.0 - smoothstep(0.0, uBand * 0.22, d));
          float fn = texture2D(uCloudTex, vWpos.xz * uCloudScale * 60.0 + vec2(uTime * 0.02, uTime * 0.013)).r;
          gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.93,0.96,0.97),
            foam * smoothstep(0.32, 0.78, fn) * uFoamAmt * uWetAmt); }`);
}
