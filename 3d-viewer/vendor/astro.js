/* astro.js — compact sun & moon ephemeris for the Hong Kong Sandbox viewer.
 *
 * Pure math, no network: positions (azimuth/altitude), sun rise/set, moon
 * rise/set and illumination for a given instant + observer lat/lon.
 * Formulas are the standard low-precision reductions from Jean Meeus,
 * "Astronomical Algorithms", as popularised by Astronomy Answers
 * (aa.quae.nl/en/reken) — the same family SunCalc implements. Accuracy is
 * a few arc-minutes for the sun, ~0.3° for the moon: ample for lighting a
 * terrain scene and quoting rise/set to the minute.
 *
 * Conventions: input `date` is a JS Date (an absolute instant — timezone is
 * the caller's concern). Returned azimuth is in radians measured from SOUTH,
 * positive toward WEST (use `compassDeg` for a 0°=N/90°=E compass bearing).
 * Altitude is radians above the horizon.
 */

const rad = Math.PI / 180;
const dayMs = 86400000, J1970 = 2440588, J2000 = 2451545;
const e = rad * 23.4397;                      // obliquity of the ecliptic

const toJulian = date => date.valueOf() / dayMs - 0.5 + J1970;
const fromJulian = j => new Date((j + 0.5 - J1970) * dayMs);
const toDays = date => toJulian(date) - J2000;
const hoursLater = (date, h) => new Date(date.valueOf() + h * 3600000);

const rightAscension = (l, b) => Math.atan2(Math.sin(l) * Math.cos(e) - Math.tan(b) * Math.sin(e), Math.cos(l));
const declination = (l, b) => Math.asin(Math.sin(b) * Math.cos(e) + Math.cos(b) * Math.sin(e) * Math.sin(l));
const azimuth = (H, phi, dec) => Math.atan2(Math.sin(H), Math.cos(H) * Math.sin(phi) - Math.tan(dec) * Math.cos(phi));
const altitude = (H, phi, dec) => Math.asin(Math.sin(phi) * Math.sin(dec) + Math.cos(phi) * Math.cos(dec) * Math.cos(H));
const siderealTime = (d, lw) => rad * (280.16 + 360.9856235 * d) - lw;

// atmospheric refraction near the horizon (radians in → radians of lift out)
function astroRefraction(h) {
  if (h < 0) h = 0;
  return 0.0002967 / Math.tan(h + 0.00312536 / (h + 0.08901179));
}

/* ---- sun -------------------------------------------------------------- */

const solarMeanAnomaly = d => rad * (357.5291 + 0.98560028 * d);
function eclipticLongitude(M) {
  const C = rad * (1.9148 * Math.sin(M) + 0.02 * Math.sin(2 * M) + 0.0003 * Math.sin(3 * M));
  const P = rad * 102.9372;                   // perihelion of Earth
  return M + C + P + Math.PI;
}
function sunCoords(d) {
  const M = solarMeanAnomaly(d), L = eclipticLongitude(M);
  return { dec: declination(L, 0), ra: rightAscension(L, 0) };
}

export function sunPosition(date, lat, lng) {
  const lw = rad * -lng, phi = rad * lat, d = toDays(date);
  const c = sunCoords(d), H = siderealTime(d, lw) - c.ra;
  return { azimuth: azimuth(H, phi, c.dec), altitude: altitude(H, phi, c.dec) };
}

// sunrise/sunset (upper-limb, h0 = -0.833° incl. refraction) + solar noon.
// Pass an instant near local noon of the civil day you care about.
const J0 = 0.0009;
const julianCycle = (d, lw) => Math.round(d - J0 - lw / (2 * Math.PI));
const approxTransit = (Ht, lw, n) => J0 + (Ht + lw) / (2 * Math.PI) + n;
const solarTransitJ = (ds, M, L) => J2000 + ds + 0.0053 * Math.sin(M) - 0.0069 * Math.sin(2 * L);
const hourAngle = (h, phi, dec) => Math.acos((Math.sin(h) - Math.sin(phi) * Math.sin(dec)) / (Math.cos(phi) * Math.cos(dec)));

export function sunTimes(date, lat, lng) {
  const lw = rad * -lng, phi = rad * lat;
  const d = toDays(date), n = julianCycle(d, lw), ds = approxTransit(0, lw, n);
  const M = solarMeanAnomaly(ds), L = eclipticLongitude(M), dec = declination(L, 0);
  const Jnoon = solarTransitJ(ds, M, L);
  const w = hourAngle(-0.833 * rad, phi, dec);
  if (!isFinite(w)) return { sunrise: null, sunset: null, solarNoon: fromJulian(Jnoon) };
  const Jset = solarTransitJ(approxTransit(w, lw, n), M, L);
  return { sunrise: fromJulian(Jnoon - (Jset - Jnoon)), sunset: fromJulian(Jset), solarNoon: fromJulian(Jnoon) };
}

/* ---- moon ------------------------------------------------------------- */

function moonCoords(d) {                       // geocentric ecliptic coordinates
  const L = rad * (218.316 + 13.176396 * d);   // mean longitude
  const M = rad * (134.963 + 13.064993 * d);   // mean anomaly
  const F = rad * (93.272 + 13.229350 * d);    // mean distance from ascending node
  const l = L + rad * 6.289 * Math.sin(M);     // longitude
  const b = rad * 5.128 * Math.sin(F);         // latitude
  const dt = 385001 - 20905 * Math.cos(M);     // distance (km)
  return { ra: rightAscension(l, b), dec: declination(l, b), dist: dt };
}

export function moonPosition(date, lat, lng) {
  const lw = rad * -lng, phi = rad * lat, d = toDays(date);
  const c = moonCoords(d), H = siderealTime(d, lw) - c.ra;
  let h = altitude(H, phi, c.dec);
  h += astroRefraction(h);
  return { azimuth: azimuth(H, phi, c.dec), altitude: h, distance: c.dist };
}

// fraction: 0 new → 1 full. phase: 0 new, 0.25 first quarter, 0.5 full, 0.75 last.
export function moonIllumination(date) {
  const d = toDays(date), s = sunCoords(d), m = moonCoords(d);
  const sdist = 149598000;                     // Earth–Sun distance (km)
  const phi = Math.acos(Math.sin(s.dec) * Math.sin(m.dec) + Math.cos(s.dec) * Math.cos(m.dec) * Math.cos(s.ra - m.ra));
  const inc = Math.atan2(sdist * Math.sin(phi), m.dist - sdist * Math.cos(phi));
  const angle = Math.atan2(Math.cos(s.dec) * Math.sin(s.ra - m.ra),
    Math.sin(s.dec) * Math.cos(m.dec) - Math.cos(s.dec) * Math.sin(m.dec) * Math.cos(s.ra - m.ra));
  return { fraction: (1 + Math.cos(inc)) / 2, phase: 0.5 + 0.5 * inc * (angle < 0 ? -1 : 1) / Math.PI, angle };
}

// moonrise/moonset by hourly scan of the local day with quadratic interpolation.
// Pass local midnight; returns { rise?, set? } — either can be absent.
export function moonTimes(date, lat, lng) {
  const hc = 0.133 * rad;                      // mean upper-limb correction
  let h0 = moonPosition(date, lat, lng).altitude - hc;
  let rise = 0, set = 0;
  for (let i = 1; i <= 24; i += 2) {
    const h1 = moonPosition(hoursLater(date, i), lat, lng).altitude - hc;
    const h2 = moonPosition(hoursLater(date, i + 1), lat, lng).altitude - hc;
    const a = (h0 + h2) / 2 - h1, b = (h2 - h0) / 2, xe = -b / (2 * a);
    const ye = (a * xe + b) * xe + h1;
    const D = b * b - 4 * a * h1;
    let roots = 0, x1 = 0, x2 = 0;
    if (D >= 0) {
      const dx = Math.sqrt(D) / (Math.abs(a) * 2);
      x1 = xe - dx; x2 = xe + dx;
      if (Math.abs(x1) <= 1) roots++;
      if (Math.abs(x2) <= 1) roots++;
      if (x1 < -1) x1 = x2;
    }
    if (roots === 1) { if (h0 < 0) rise = i + x1; else set = i + x1; }
    else if (roots === 2) { rise = i + (ye < 0 ? x2 : x1); set = i + (ye < 0 ? x1 : x2); }
    if (rise && set) break;
    h0 = h2;
  }
  const r = {};
  if (rise) r.rise = hoursLater(date, rise);
  if (set) r.set = hoursLater(date, set);
  return r;
}

/* ---- helpers ----------------------------------------------------------- */

// astro azimuth (from south, +west) → compass bearing degrees (0 N, 90 E)
export const compassDeg = az => ((az / rad) + 180) % 360;
