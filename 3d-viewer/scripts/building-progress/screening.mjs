import {createHash} from 'node:crypto';

export const SCREENING_POLICY = 'good-enough-v1';
export const canonical = value => Array.isArray(value)
  ? `[${value.map(canonical).join(',')}]`
  : value !== null && typeof value === 'object'
    ? `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonical(value[key])}`).join(',')}}`
    : JSON.stringify(value);
export const digest = value => createHash('sha256').update(canonical(value)).digest('hex');

// Acceptance concerns the rendered building, not just the downloaded mesh.
export function screeningFingerprint(building, native, context) {
  return digest([SCREENING_POLICY, building, native || null, context]);
}

export function localTerrainContext(baseContext, terrainHashes = []) {
  return digest([baseContext, [...terrainHashes].sort()]);
}

export function terrainHashesForBuilding(building, patches = []) {
  const points = (building.rings || []).flat();
  const xs = points.map(point => point[0]), zs = points.map(point => point[1]);
  const bounds = points.length
    ? [Math.min(...xs), Math.max(...xs), Math.min(...zs), Math.max(...zs)]
    : [building.centre?.[0], building.centre?.[0], building.centre?.[1], building.centre?.[1]];
  return patches.filter(patch => patch.targets.has(building.uid) || (
    bounds.every(Number.isFinite) && bounds[0] <= patch.bounds[1] && bounds[1] >= patch.bounds[0] &&
    bounds[2] <= patch.bounds[3] && bounds[3] >= patch.bounds[2]
  )).map(patch => patch.hash);
}

export function validScreening(row, form) {
  return row?.policy === SCREENING_POLICY && row.inputHash === form.inputHash &&
    ['good-to-go', 'enhancement-required'].includes(row.decision) &&
    typeof row.reason === 'string' && row.reason.trim().length > 0 &&
    typeof row.evidence === 'string' && row.evidence.trim().length > 0 &&
    /^[a-f0-9]{64}$/.test(row.evidenceHash || '') &&
    Number.isFinite(Date.parse(row.reviewedAt));
}
