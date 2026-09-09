"""HKS-222: reuse retained source members without reusing placement acceptance."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'shared-modelling'))
from db import connect
sys.path.insert(0, str(HERE.parent / 'landmark-resume'))
from r2_snapshot import digest, key_for, verify_object

SHA = re.compile(r'^[0-9a-f]{64}$')
KIND = 'original-and-prepared-sheet'


def validate_artifact(artifact):
    if not isinstance(artifact, dict) or not isinstance(artifact.get('sha256'), str) or not SHA.fullmatch(artifact['sha256']):
        raise ValueError('Source bundle SHA-256 required')
    if artifact.get('key') != key_for(artifact['sha256']) or artifact.get('kind') != KIND:
        raise ValueError('Source bundle requires its exact content-addressed modelling key and kind')
    if type(artifact.get('bytes')) is not int or artifact['bytes'] <= 0:
        raise ValueError('Source bundle byte count required')
    return artifact


def previous_source_artifacts():
    """One read-only query; latest retained bundle per frozen source, across pipelines."""
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        rows = con.execute('''SELECT DISTINCT ON(i.source_sha) i.source_sha,a.value
            FROM astra_modelling.native_stage_inputs i
            JOIN astra_modelling.native_stage_results r USING(cache_key)
            CROSS JOIN LATERAL jsonb_array_elements(r.result->'artifacts') a(value)
            WHERE a.value->>'kind'=%s
            ORDER BY i.source_sha,r.created_at DESC,i.cache_key,a.value->>'key' ''', (KIND,)).fetchall()
    result = {}
    for source_sha, artifact in rows:
        if not isinstance(source_sha, str) or not SHA.fullmatch(source_sha):
            raise ValueError('Invalid retained source identity')
        result[source_sha] = validate_artifact(artifact)
    return result


def restore_original(r2, artifact, sheet, out):
    """Verify the whole bundle, then safely restore only the exact ZIP and its record.

    Restored bytes remain a cache candidate: acquire() must check the current source
    ETag, directory and member CRCs. Nothing is extracted into viewer/public paths.
    """
    artifact = validate_artifact(artifact)
    if not isinstance(sheet, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}', sheet):
        raise ValueError('Invalid source sheet')
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    wanted = {f'original/{sheet}.zip': f'{sheet}.zip', 'original/download.json': 'download.json'}
    with tempfile.TemporaryDirectory(prefix='source-restore-', dir=out.parent) as temporary:
        temp = Path(temporary)
        bundle = temp/'bundle.tar.gz'
        verify_object(r2, artifact['key'], artifact['sha256'], artifact['bytes'], bundle)
        found = set()
        with tarfile.open(bundle, 'r:gz') as tar:
            for member in tar:
                path = PurePosixPath(member.name)
                if path.is_absolute() or '..' in path.parts or '\\' in member.name:
                    raise ValueError('Unsafe source bundle member')
                if member.name not in wanted:
                    continue
                if member.name in found or not member.isfile():
                    raise ValueError('Duplicate or non-regular original member')
                maximum = 1_048_576 if member.name.endswith('/download.json') else 8 * 1024**3
                if not 0 <= member.size <= maximum:
                    raise ValueError('Original member exceeds restore bound')
                source = tar.extractfile(member)
                if source is None:
                    raise ValueError('Original member has no readable bytes')
                with source, (temp/wanted[member.name]).open('wb') as target:
                    shutil.copyfileobj(source, target)
                found.add(member.name)
        if found != set(wanted):
            raise ValueError('Source bundle omits an exact original member')
        record = json.loads((temp/'download.json').read_bytes())
        archive = temp/f'{sheet}.zip'
        if not isinstance(record, dict) or record.get('sheet') != sheet or type(record.get('bytes')) is not int or record['bytes'] != archive.stat().st_size or record.get('sha256') != digest(archive):
            raise ValueError('Restored original ZIP differs from its source record')
        out.mkdir(parents=True, exist_ok=True)
        os.replace(archive, out/archive.name)
        os.replace(temp/'download.json', out/'download.json')
    return out/'download.json', record
