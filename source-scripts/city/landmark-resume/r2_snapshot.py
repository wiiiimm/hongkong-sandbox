#!/usr/bin/env python3
"""Immutable, checksum-verified working checkpoints (HKS-216). No runtime assets changed."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sqlite3
import subprocess
import tempfile
from urllib.parse import urlsplit

PREFIX = 'astra-modelling/'

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def safe_path(root, relative):
    p = PurePosixPath(relative)
    forbidden = {'.git', '.vercel', '.aws', 'node_modules', '__pycache__'}
    if (not relative or p.is_absolute() or '..' in p.parts or '\\' in relative
            or any(x in forbidden or x.startswith('.env') or x.endswith(('.pem', '.key')) for x in p.parts)):
        raise ValueError('Unsafe or credential-bearing path')
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Path resolves outside checkout')
    return path

def key_for(sha):
    if not re.fullmatch('[0-9a-f]{64}', sha):
        raise ValueError('Invalid object digest')
    return PREFIX + 'objects/sha256/' + sha[:2] + '/' + sha

class LocalStore:
    def __init__(self, root): self.root = Path(root)
    def get(self, key, dest):
        import shutil
        shutil.copyfile(self.root / key, dest)
    def put(self, key, source):
        target = self.root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if digest(target) != digest(source): raise ValueError('Immutable object conflict')
            return False
        import shutil
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as f:
            temporary = Path(f.name)
        try:
            shutil.copyfile(source, temporary)
            os.link(temporary, target)
        except FileExistsError:
            if digest(target) != digest(source): raise ValueError('Concurrent object conflict')
        finally: temporary.unlink(missing_ok=True)
        return True

def r2_endpoint(environ):
    endpoint = environ.get('R2_ENDPOINT_URL')
    if not endpoint:
        account = environ.get('R2_ACCOUNT_ID', '')
        if not re.fullmatch('[0-9a-fA-F]{32}', account):
            raise ValueError('Set R2_ENDPOINT_URL or a valid R2_ACCOUNT_ID')
        endpoint = 'https://' + account + '.r2.cloudflarestorage.com'
    parsed = urlsplit(endpoint)
    if (parsed.scheme != 'https' or not parsed.hostname
            or not re.fullmatch(r'[0-9a-fA-F]{32}(?:\.(?:eu|fedramp))?\.r2\.cloudflarestorage\.com', parsed.hostname)
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.path not in ('', '/') or parsed.query or parsed.fragment):
        raise ValueError('R2 endpoint must be an HTTPS Cloudflare R2 account endpoint without credentials or path')
    return endpoint.rstrip('/')

class R2Store:
    def __init__(self, bucket):
        import boto3
        endpoint = r2_endpoint(os.environ)
        required = ('R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY')
        if any(not os.environ.get(k) for k in required):
            raise ValueError('Set R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY')
        self.bucket = bucket
        self.client = boto3.client('s3', endpoint_url=endpoint, region_name='auto', aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'])
    def get(self, key, dest): self.client.download_file(self.bucket, key, str(dest))
    def put(self, key, source):
        from botocore.exceptions import ClientError
        try:
            with open(source, 'rb') as f:
                self.client.put_object(Bucket=self.bucket, Key=key, Body=f, IfNoneMatch='*', Metadata={'sha256': digest(source)})
            return True
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] not in (409, 412): raise
            # Never trust metadata alone: verify existing bytes before resume.
            with tempfile.TemporaryDirectory() as temp:
                existing = Path(temp) / 'object'
                self.get(key, existing)
                if digest(existing) != digest(source): raise ValueError('Remote immutable object conflict')
            return False

def verify_object(store, key, sha, size, dest):
    store.get(key, dest)
    if dest.stat().st_size != size or digest(dest) != sha:
        raise ValueError('Object checksum or size mismatch')

def snapshot(root, inventory, store, output, profiles):
    root = Path(root).resolve()
    data = json.loads(Path(inventory).read_text())
    allowed_profiles = {'unmodified-cli-restore', 'portable-working-closure', 'optional-review-evidence'}
    if not profiles or not set(profiles).issubset(allowed_profiles):
        raise ValueError('Unsupported snapshot profile')
    rows, uploaded, uploaded_bytes = [], 0, 0
    with tempfile.TemporaryDirectory() as temp:
        for item in data['rows']:
            if not set(profiles).intersection(item['profiles']) or item['gitTracked']: continue
            relative = item['path']
            source = safe_path(root, relative)
            if item['kind'] == 'symlink':
                target = item['linkTarget']
                # Relative links may contain .., but must resolve inside checkout.
                if Path(target).is_absolute() or not (source.parent / target).resolve().is_relative_to(root):
                    raise ValueError('Unsafe symlink target')
                rows.append({'path': relative, 'kind': 'symlink', 'target': target})
                continue
            if not source.is_file(): raise ValueError('Missing inventoried input: ' + relative)
            working = source
            if source.suffix == '.sqlite':
                working = Path(temp) / 'ledger.sqlite'
                with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as src, sqlite3.connect(working) as dst:
                    src.backup(dst)
                    if dst.execute('PRAGMA quick_check').fetchone()[0] != 'ok': raise ValueError('SQLite backup failed integrity check')
            sha, size = digest(working), working.stat().st_size
            key = key_for(sha)
            if store.put(key, working): uploaded += 1; uploaded_bytes += size
            check = Path(temp) / 'check'
            verify_object(store, key, sha, size, check)
            check.unlink()
            rows.append({'path': relative, 'kind': 'file', 'sha256': sha, 'bytes': size})
        commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
        manifest = {'version': 1, 'gitCommit': commit, 'profiles': profiles, 'sourceSnapshot': data.get('snapshotId'), 'files': rows, 'qualification': 'Working inputs only; model acceptance and live publication are separate.'}
        output = Path(output)
        output.write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
        manifest_sha = digest(output)
        key = PREFIX + 'snapshots/' + manifest_sha + '.json'
        store.put(key, output)
        verify_object(store, key, manifest_sha, output.stat().st_size, Path(temp) / 'manifest')
    return {'manifestSHA256': manifest_sha, 'files': len(rows), 'uploadedObjects': uploaded, 'uploadedBytes': uploaded_bytes, 'manifestKey': key}

def restore(root, manifest_path, store, expected_sha):
    root = Path(root).resolve()
    manifest_path = Path(manifest_path)
    if digest(manifest_path) != expected_sha: raise ValueError('Manifest checksum mismatch')
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('version') != 1: raise ValueError('Unsupported snapshot version')
    actual_commit = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    if actual_commit != manifest['gitCommit']: raise ValueError('Checkout does not match snapshot commit')
    seen = set()
    # Validate all destinations before downloading or writing anything.
    for row in manifest['files']:
        path = safe_path(root, row['path'])
        if row['path'] in seen: raise ValueError('Duplicate manifest path')
        seen.add(row['path'])
        if row['kind'] == 'symlink':
            target = row['target']
            if Path(target).is_absolute() or not (path.parent / target).resolve().is_relative_to(root): raise ValueError('Unsafe symlink')
        elif row['kind'] != 'file': raise ValueError('Unsupported entry kind')
        else: key_for(row['sha256'])
        if path.exists() or path.is_symlink():
            okay = path.is_symlink() and row['kind'] == 'symlink' and os.readlink(path) == row['target']
            okay |= not path.is_symlink() and path.is_file() and row['kind'] == 'file' and digest(path) == row['sha256']
            if not okay: raise ValueError('Refusing to overwrite existing working material: ' + row['path'])
    with tempfile.TemporaryDirectory(dir=root) as temp:
        staged = []
        for row in manifest['files']:
            if row['kind'] != 'file': continue
            dest = Path(temp) / row['sha256']
            if not dest.exists(): verify_object(store, key_for(row['sha256']), row['sha256'], row['bytes'], dest)
            staged.append((row, dest))
        # All payloads verified before restoring; atomic per-file and restart-safe.
        import shutil
        for row, source in staged:
            path = safe_path(root, row['path'])
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists(): continue
            with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as f: tmp = Path(f.name)
            try:
                shutil.copyfile(source, tmp)
                os.link(tmp, path)
            finally: tmp.unlink(missing_ok=True)
        for row in manifest['files']:
            if row['kind'] != 'symlink': continue
            path = safe_path(root, row['path'])
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.is_symlink(): path.symlink_to(row['target'])
    return {'restoredEntries': len(manifest['files']), 'gitCommit': actual_commit}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['snapshot', 'restore'])
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--inventory', type=Path)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--manifest-sha256')
    p.add_argument('--profile', action='append', default=[])
    p.add_argument('--local-store', type=Path)
    p.add_argument('--bucket', default='hk-sandbox-assets')
    a = p.parse_args()
    store = LocalStore(a.local_store) if a.local_store else R2Store(a.bucket)
    if a.operation == 'snapshot':
        if not a.inventory: p.error('--inventory is required')
        result = snapshot(a.root, a.inventory, store, a.manifest, a.profile or ['unmodified-cli-restore'])
    else:
        if not a.manifest_sha256: p.error('--manifest-sha256 is required')
        result = restore(a.root, a.manifest, store, a.manifest_sha256)
    print(json.dumps(result, indent=2))

if __name__ == '__main__': main()
