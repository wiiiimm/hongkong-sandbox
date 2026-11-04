import test from 'node:test';
import assert from 'node:assert/strict';
import {replacementRows, replacementURLs} from './terrain-replacements.mjs';
import {makeTerrainSampler, ORIGIN} from '../../../3d-viewer/city/geo.js';

const a = {url: 'city/data/a.json', sha256: 'a'.repeat(64), retainedUids: ['landsd/1:0']};
const b = {url: 'city/data/b.json', sha256: 'b'.repeat(64), retainedUids: ['landsd/2:0']};
const hashes = {['3d-viewer/' + a.url]: a.sha256, ['3d-viewer/' + b.url]: b.sha256};

test('all explicit parents are removed regardless of original manifest order', () => {
  const installed = [b, {url: 'city/data/untouched.json'}, a];
  const removed = replacementURLs([{replacesMany: [a, b]}], installed, hashes);
  assert.deepEqual(installed.filter(row => !removed.has(row.url)), [{url: 'city/data/untouched.json'}]);
  assert.deepEqual(replacementRows({replaces: a}), [a]);
  assert.deepEqual(replacementRows({}), []);
});

test('changed or unavailable original terrain cannot be replaced', () => {
  assert.throws(() => replacementURLs([{replacesMany: [a, b]}], [a, b],
    {...hashes, ['3d-viewer/' + b.url]: 'c'.repeat(64)}), /parent changed/);
  assert.throws(() => replacementURLs([{replacesMany: [a, b]}], [a], hashes), /Missing/);
});

test('duplicate and conflicting replacement claims cannot silently drop a patch', () => {
  assert.throws(() => replacementURLs([{replacesMany: [a, a]}], [a, b], hashes), /more than once/);
  assert.throws(() => replacementURLs([{replaces: a}, {replaces: a}], [a, b], hashes), /more than once/);
  assert.throws(() => replacementRows({replaces: a, replacesMany: [a, b]}), /Conflicting/);
});

test('invalid paths, unpinned parents and absent retained model scope reject', () => {
  for (const bad of [{...a, url: 'city/data/../a.json'}, {...a, sha256: null},
    {...a, retainedUids: []}, {...a, retainedUids: ['landsd/1:0', 'landsd/1:0']}]) {
    assert.throws(() => replacementRows({replacesMany: [bad, b]}));
  }
  assert.throws(() => replacementRows({replacesMany: [a]}), /at least two/);
});

test('viewer terrain samples the staged surface at both replaced parents', () => {
  const grid = (x, z, step, height) => ({w: 2, h: 2, elev: Array(4).fill(height),
    meta: {georef: {bE: ORIGIN[0] + x, bN: ORIGIN[1] - z, aE: step, aN: -step}}});
  const root = grid(0, 0, 100, 2), patches = [grid(0, 0, 4, 10), grid(8, 0, 4, 20), grid(30, 0, 4, 30)];
  const installed = [a, b, {url: 'city/data/untouched.json'}];
  const before = makeTerrainSampler({...root, patches});
  assert.equal(before.height(2, 2), 10);
  assert.equal(before.height(10, 2), 20);
  const removed = replacementURLs([{replacesMany: [a, b]}], installed, hashes);
  const after = makeTerrainSampler({...root,
    patches: [...patches.filter((_, i) => !removed.has(installed[i].url)), grid(0, 0, 12, 5)]});
  assert.equal(after.height(2, 2), 5);
  assert.equal(after.height(10, 2), 5);
  assert.equal(after.height(32, 2), 30);
});
