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

export function validScreening(row, form) {
  return row?.policy === SCREENING_POLICY && row.inputHash === form.inputHash &&
    ['good-to-go', 'enhancement-required'].includes(row.decision) &&
    typeof row.reason === 'string' && row.reason.trim().length > 0 &&
    typeof row.evidence === 'string' && row.evidence.trim().length > 0 &&
    /^[a-f0-9]{64}$/.test(row.evidenceHash || '') &&
    Number.isFinite(Date.parse(row.reviewedAt));
}
