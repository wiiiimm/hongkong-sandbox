"""Isolated cached-model-v1 processing; no SQLite/catalogue writes or publication."""
import importlib
import hashlib
import json
from pathlib import Path
import sys
import tempfile


def modules(root):
    source = root / 'source-scripts/city/building-batch'
    resume = root / 'source-scripts/city/landmark-resume'
    for folder in (source, resume):
        if str(folder) not in sys.path:
            sys.path.insert(0, str(folder))
    cached = importlib.import_module('cached_models')
    storage = importlib.import_module('r2_snapshot')
    if Path(cached.__file__).resolve() != source / 'cached_models.py':
        raise ValueError('Cached processor loaded from another checkout')
    if Path(storage.__file__).resolve() != resume / 'r2_snapshot.py':
        raise ValueError('Object store loaded from another checkout')
    return cached, storage


def code_hashes(root):
    root = Path(root).resolve()
    paths = ['source-scripts/city/shared-modelling/model_adapter.py',
             'source-scripts/city/building-batch/cached_models.py',
             'source-scripts/city/building-batch/runner.py',
             'source-scripts/city/landmark-resume/r2_snapshot.py']
    return {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in paths}


def process(payload, root, store):
    """Process a frozen cached-model payload and return outcome plus verified object ref.

    store implements put(key, path) and get(key, destination), as R2Store/LocalStore.
    The caller owns queue leases and must accept results only with a current lease.
    """
    root = Path(root).resolve()
    if payload.get('adapterCode') != code_hashes(root):
        raise ValueError('Frozen adapter code does not match checkout')
    if not all(payload.get(key) for key in ('snapshot', 'sourceJobId', 'sourceSelection')):
        raise ValueError('Missing frozen source provenance')
    payload = payload['adapterPayload']
    cached, storage = modules(root)
    if payload.get('toolSHA256') != cached.tool_hash(root):
        raise ValueError('Frozen job processor fingerprint does not match checkout')
    # The planner's frozen JSON stays unchanged even if the legacy adapter evolves.
    frozen = json.loads(json.dumps(payload))
    with tempfile.TemporaryDirectory(prefix='astra-model-attempt-') as temp:
        out = Path(temp)
        result = cached.Processor(root, out, max_output_bytes=32 * 1024**2)(frozen)
        result['liveReplacement'] = False
        if result['outcome'] != 'staged-needs-placement-review':
            return result
        record = result['record']
        asset = record.pop('asset')
        if Path(asset).name != asset or not asset.endswith('.glb.gz'):
            raise ValueError('Processor returned an invalid candidate path')
        source = out / asset
        sha, size = storage.digest(source), source.stat().st_size
        if sha != record['sha256'] or size != record['bytes']:
            raise ValueError('Processor candidate checksum or size mismatch')
        key = storage.key_for(sha)
        store.put(key, source)
        storage.verify_object(store, key, sha, size, out / 'verified-readback')
        result['object'] = {'key': key, 'sha256': sha, 'bytes': size}
        result['publicationApproved'] = False
        return result
