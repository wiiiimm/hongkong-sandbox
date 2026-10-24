"""Cooperative local lock for manifest, review-pointer and progress publication.

Source leases still protect source ownership. This separate filesystem lock keeps
two importers in one worktree from publishing concurrently and losing a snapshot.
"""
from contextlib import contextmanager
from pathlib import Path
import fcntl

@contextmanager
def locked_publication(root):
    path=Path(root)/'source-scripts/city/government-import/local/runtime-publication.lock'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+') as stream:
        fcntl.flock(stream.fileno(),fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(),fcntl.LOCK_UN)
