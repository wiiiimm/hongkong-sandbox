// Original viewer interpolation, shared unchanged with the city tide adapter.
// Legacy callers rely on clamped endpoints; city validates coverage and missing hours first.
export function tideAt(vals, absHour) {
  const idx = absHour - 1, i0 = Math.floor(idx);
  const cl = i => vals[Math.max(0, Math.min(vals.length - 1, i))];
  const a = cl(i0), b = cl(i0 + 1);
  return (isFinite(a) && isFinite(b)) ? a + (b - a) * (idx - i0) : NaN;
}
