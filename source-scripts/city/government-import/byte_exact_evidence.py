"""Store large frozen evidence as byte-exact chunks; restore before replay."""
import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAX_CHUNK = 64 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def inside(path, root):
    path = Path(path).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Evidence path escapes repository')
    return path


def pack(path, *, root=ROOT, chunk_bytes=MAX_CHUNK):
    path = inside(path, root)
    if not 1 <= chunk_bytes <= MAX_CHUNK:
        raise ValueError('Invalid chunk size')
    folder = path.with_name(path.name + '.chunks')
    if inside(folder, root) != folder:
        raise ValueError('Chunk folder must not redirect through a symlink')
    folder.mkdir(exist_ok=True)
    rows, total, whole = [], 0, hashlib.sha256()
    with path.open('rb') as f:
        for i, block in enumerate(iter(lambda: f.read(chunk_bytes), b'')):
            name = f'part-{i:05d}.bin'
            target = inside(folder / name, root)
            if target.exists():
                if target.read_bytes() != block:
                    raise ValueError('Existing chunk differs')
            else:
                with target.open('xb') as out:
                    out.write(block)
            rows.append(dict(name=name, offset=total, bytes=len(block), sha256=sha(block)))
            total += len(block)
            whole.update(block)
    manifest = dict(format='byte-exact-evidence-v1', originalPath=str(path.relative_to(root.resolve())), bytes=total, sha256=whole.hexdigest(), chunks=rows)
    if file_sha(path) != manifest['sha256']:
        raise ValueError('Original changed during packaging')
    target = folder / 'manifest.json'
    if target.exists():
        if json.loads(target.read_text()) != manifest:
            raise ValueError('Existing manifest differs')
    else:
        with target.open('x') as out:
            out.write(json.dumps(manifest, indent=2) + '\n')
    verify(target, root=root)
    return target


def verified_blocks(manifest, *, root=ROOT):
    manifest = inside(manifest, root)
    d = json.loads(manifest.read_text())
    if d['format'] != 'byte-exact-evidence-v1':
        raise ValueError('Unsupported format')
    original = inside(root / d['originalPath'], root)
    if manifest != original.with_name(original.name + '.chunks') / 'manifest.json':
        raise ValueError('Manifest must be adjacent to its original')
    total, whole = 0, hashlib.sha256()
    for i, row in enumerate(d['chunks']):
        if row['name'] != f'part-{i:05d}.bin' or row['offset'] != total or not 1 <= row['bytes'] <= MAX_CHUNK:
            raise ValueError('Invalid chunk sequence')
        block = inside(manifest.parent / row['name'], root).read_bytes()
        if len(block) != row['bytes'] or sha(block) != row['sha256']:
            raise ValueError('Chunk integrity failure')
        total += len(block)
        whole.update(block)
        yield block
    if total != d['bytes'] or whole.hexdigest() != d['sha256']:
        raise ValueError('Complete evidence integrity failure')


def verify(manifest, *, root=ROOT):
    for _ in verified_blocks(manifest, root=root):
        pass


def restore(manifest, *, root=ROOT):
    manifest = inside(manifest, root)
    d = json.loads(manifest.read_text())
    target = inside(root / d['originalPath'], root)
    if target.exists():
        verify(manifest, root=root)
        if target.stat().st_size != d['bytes'] or file_sha(target) != d['sha256']:
            raise ValueError('Existing original differs; never overwrite it')
        return target
    fd, temporary = tempfile.mkstemp(prefix=target.name + '.restore-', dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            for block in verified_blocks(manifest, root=root):
                out.write(block)
            out.flush()
            os.fsync(out.fileno())
        # Hard-link publication refuses to overwrite any concurrently created file.
        os.link(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return target


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['pack', 'verify', 'restore'])
    p.add_argument('path', type=Path)
    a = p.parse_args()
    result = globals()[a.action](a.path)
    print(json.dumps(dict(action=a.action, path=str(result) if result else str(a.path), byteExact=True)))


if __name__ == '__main__':
    main()
