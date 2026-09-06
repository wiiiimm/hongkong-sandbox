// Extracted unchanged from the original viewer attachTerrainFX water passes (HKS-180).
// Caller declares vWpos and the wave uniforms. Standard material depth/fog chunks stay intact.
export function applyWaterSurfaceShader(sh) {
      // animated wave normals: three sine octaves' analytic slopes, rotated into
      // view space — the PBR sun/moon specular then glints off the moving water
      sh.fragmentShader = sh.fragmentShader.replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
        { vec2 p = vWpos.xz * uWaveK; float t = uTime;
          float sx = cos(p.x * 1.00 + t * 1.1) * 1.0
                   + cos((p.x + p.y) * 1.7 + t * 1.7) * 0.6
                   + cos(p.x * 3.1 - p.y * 2.2 + t * 2.3) * 0.35;
          float sz = cos(p.y * 1.13 - t * 0.9) * 1.0
                   + cos((p.y - p.x) * 1.9 + t * 1.4) * 0.6
                   + cos(p.y * 2.7 + p.x * 2.4 + t * 2.1) * 0.35;
          vec3 wn = (viewMatrix * vec4(sx, 0.0, sz, 0.0)).xyz;
          normal = normalize(normal + wn * uWaveAmp);
          // rain pocks the surface: fine time-jittered normal noise scatters the
          // glint while it rains, reading as a roughened, drizzled sea
          if (uSparkAmt > 0.0) {
            vec2 rc = floor(vWpos.xz * uWaveK * 60.0) + floor(uTime * 8.0);
            float rj = fract(sin(dot(rc, vec2(12.9898, 78.233))) * 43758.5453) - 0.5;
            float rk = fract(sin(dot(rc, vec2(39.3468, 11.135))) * 24634.6345) - 0.5;
            normal = normalize(normal + (viewMatrix * vec4(rj, 0.0, rk, 0.0)).xyz * uSparkAmt * 0.9);
          } }`);
      // sun-glitter: per-cell micro-facets whose normals slowly rotate — each
      // flashes as it sweeps through alignment between the sun (or moon) and
      // the eye. Injected before the shared passes so height fog dims it.
      sh.fragmentShader = sh.fragmentShader.replace('#include <dithering_fragment>', `#include <dithering_fragment>
        if (uGlintAmt > 0.0) {
          vec2 gc = floor(vWpos.xz * uWaveK * 80.0);
          float gr = fract(sin(dot(gc, vec2(127.1, 311.7))) * 43758.5453);
          float ph = gr * 6.2831 + uTime * (1.0 + gr * 2.5);
          vec3 mj = normalize(normal + (viewMatrix * vec4(cos(ph) * 0.22, 0.0, sin(ph) * 0.22, 0.0)).xyz);
          vec3 Hh = normalize(uSunDirV + normalize(vViewPosition));
          gl_FragColor.rgb += vec3(1.0, 0.97, 0.88) * pow(max(dot(mj, Hh), 0.0), 420.0) * uGlintAmt;
        }`);
}
