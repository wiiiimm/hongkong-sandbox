"""Archive only explicitly hash-bound external terminal evidence for a repo freezer."""
from hashlib import sha256
from pathlib import Path
import re


def archive_declared_external(paths, root, archive_dir, terminal_refs):
    root = Path(root).resolve()
    archive_dir = Path(archive_dir)
    assert archive_dir.resolve().is_relative_to(root), 'Archive must be inside repository'
    allowed = {}
    for ref in terminal_refs:
        path = root / ref['path']
        if not path.resolve().is_relative_to(root):
            assert re.fullmatch(r'[0-9a-f]{64}', ref['sha256'])
            assert path not in allowed or allowed[path] == ref
            allowed[path] = ref
    retained, copies = set(), []
    for path in sorted(set(map(Path, paths))):
        if path.resolve().is_relative_to(root):
            retained.add(path)
            continue
        assert path in allowed, f'Undeclared external evidence: {path}'
        original = allowed[path]
        data = path.read_bytes()
        assert sha256(data).hexdigest() == original['sha256'], 'External evidence changed'
        destination = archive_dir / (original['sha256'] + '-' + path.name)
        assert destination.resolve().is_relative_to(root)
        if destination.exists():
            assert destination.read_bytes() == data, 'Existing archive differs'
        copies.append((path, destination, data, original))
    # Validate the entire declared external set before creating any archive file.
    records = []
    for path, destination, data, original in copies:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            with destination.open('xb') as stream:
                stream.write(data)
        assert destination.read_bytes() == data
        assert sha256(path.read_bytes()).hexdigest() == original['sha256']
        retained.add(destination)
        records.append(dict(originalReference=original, archivedReference=dict(
            path=str(destination.relative_to(root)), sha256=original['sha256']),
            byteIdentical=True, originalUnmodified=True))
    return retained, records
