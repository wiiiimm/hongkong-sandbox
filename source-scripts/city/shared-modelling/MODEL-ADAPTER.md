# HKS-217 — frozen cached-model adapter

`model_adapter.code_hashes(root)` returns the implementation hashes used to freeze a job. `model_adapter.process(wrapper, root, store)` accepts:

```python
{
    'snapshot': 'immutable inventory snapshot identifier',
    'sourceJobId': 'original cached-model-v1 job ID',
    'sourceSelection': 'selection/job-set name',
    'adapterPayload': original_cached_models_payload,
    'adapterCode': code_hashes(root),
}
```

The parent planner must obtain the original payload from the immutable inventory snapshot. The adapter itself does not read SQLite, Neon or a catalogue to choose work. It verifies adapter-code hashes and the original payload's `toolSHA256` against the current checkout before constructing the existing `cached_models.Processor`. That processor checks retained source hashes, source identity, footprint match and geometry/resource limits and can reuse an exact existing compact model. No alternate model converter or new architectural refinement was introduced.

Each attempt has a private temporary output directory, outside the live viewer. The adapter does not write shared catalogues, job databases or source models. Successful outputs are placed in the injected store's `astra-modelling/objects/sha256/` namespace, read back and verified before returning:

```python
{
    # Existing processor outcome, record, proof and reusedCompact fields retained.
    'outcome': 'staged-needs-placement-review',
    'object': {'key': 'astra-modelling/objects/sha256/…', 'sha256': '…', 'bytes': 2887},
    'liveReplacement': False,
    'publicationApproved': False,
}
```

`record.asset` is removed because it names the deleted attempt-local file. Consumers must resolve `object`, not assume a shared staging path. Holds and resource/source-match outcomes return without any uploaded object. The `store` implements `put(key, source_path)` and `get(key, destination_path)` as `R2Store` or the deterministic `LocalStore` fixture. A failed upload/readback raises; no successful result is returned. A worker that loses its lease must not accept the result; an immutable, unreferenced object may remain and is safe for later deduplicated retry. Retention/garbage collection is separate.

## Verification

Five focused tests pass: code mismatch, stale legacy tools, non-uploaded holds, readback failure and immutable result/attempt isolation. Run:

```sh
python3 -m unittest discover -s source-scripts/city/shared-modelling -p 'test_model_adapter.py' -v
```

An actual retained completed payload for **landsd/101313:0** was read through a read-only SQLite connection solely to supply this standalone integration fixture. It matched the current processor fingerprint and reused its existing compact geometry. Processing plus local object readback took **0.248 seconds**; output **2,887 bytes**, SHA-256 `ade3fb9efd6c2da80f809200098eac42177114cc7eee928f27015116ab933b8c`. Outcome remained `staged-needs-placement-review`; no source, shared catalogue, database row or live viewer geometry changed. Temporary verification output is `/tmp/astra-model-adapter-verification.json`, object store `/tmp/astra-model-adapter-store/`.

This verifies the concrete model adapter and prior-compact reuse, not a live R2 cloud transfer, new geometry refinement, multi-device deployment or placement/architectural acceptance. The queue planner/lease integration belongs to the parent worker and its separate tests.


A later real-R2 integration verification ran two current-set jobs through the actual shared Neon worker with two concurrent threads and independently downloaded/hash-checked both cloud objects. See [VERIFICATION.md](VERIFICATION.md#real-r2-model-preparation--hks-216--hks-217) and [cloud-model-worker-verification.json](cloud-model-worker-verification.json). The earlier LocalStore fixture above remains historical evidence; the new cloud check does not change placement/publication gates.
