/** Explicit staged terrain replacements; never infer replacement from overlap. */
import assert from 'node:assert/strict';

export function replacementRows(candidate) {
  assert(!(candidate.replaces && candidate.replacesMany), 'Conflicting replacement contracts');
  const rows = candidate.replacesMany ?? (candidate.replaces ? [candidate.replaces] : []);
  assert(Array.isArray(rows), 'Replacement list required');
  if (candidate.replacesMany) assert(rows.length >= 2, 'Plural replacement needs at least two parents');
  for (const row of rows) {
    assert(typeof row.url === 'string' && /^city\/data\/[^.][^\s]*\.json$/.test(row.url)
      && !row.url.includes('..'), 'Invalid terrain replacement URL');
    assert(/^[a-f0-9]{64}$/.test(row.sha256), 'Pinned parent hash required');
    assert(Array.isArray(row.retainedUids) && row.retainedUids.length > 0
      && row.retainedUids.every(uid => typeof uid === 'string'), 'Retained model scope required');
    assert(new Set(row.retainedUids).size === row.retainedUids.length, 'Duplicate retained model');
  }
  return rows;
}

export function replacementURLs(candidates, installed, hashes) {
  const available = new Set(installed.map(row => row.url)), result = new Set();
  for (const candidate of candidates) for (const row of replacementRows(candidate)) {
    assert(available.has(row.url), 'Missing terrain replacement parent');
    assert(!result.has(row.url), 'Parent replaced more than once');
    assert.equal(hashes['3d-viewer/' + row.url], row.sha256, 'Retained terrain parent changed');
    result.add(row.url);
  }
  return result;
}
