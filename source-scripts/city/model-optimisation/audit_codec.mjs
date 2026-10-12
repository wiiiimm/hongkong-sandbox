/** Read-only revalidation of immutable outputs, without re-encoding. */
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import { createInterface } from 'node:readline';
import assert from 'node:assert/strict';
import { sha, verifyExact } from './codec.mjs';
import { verifyLossy } from './lossy_codec.mjs';

for await (const line of createInterface({ input: process.stdin })) {
  try {
    const request = JSON.parse(line);
    const source = readFileSync(request.source), artifact = readFileSync(request.artifact);
    assert.equal(sha(source), request.sourceSha256);
    assert.equal(sha(artifact), request.artifactSha256);
    const verification = request.recipe?.lossy
      ? await verifyLossy(gunzipSync(source), gunzipSync(artifact), request.recipe.parameters)
      : await verifyExact(gunzipSync(source), gunzipSync(artifact));
    assert.deepEqual(verification.exactBufferViewSha256, request.exactBufferViewSha256);
    if(request.recipe?.lossy) for(const key of ['vertices','triangles','primitiveDiagnostics',
      'maxPositionQuantisationErrorMetres','simplifierEstimatedErrorMetres','sourceGeometryExact']) {
      assert.deepEqual(verification[key],request.metrics[key],`lossy geometry metrics ${key}`);
    }
    process.stdout.write(JSON.stringify({ ok: true, sourceBytes: source.length, outputBytes: artifact.length }) + '\n');
  } catch (error) {
    process.stdout.write(JSON.stringify({ ok: false, error: error.message.slice(0, 600) }) + '\n');
  }
}
