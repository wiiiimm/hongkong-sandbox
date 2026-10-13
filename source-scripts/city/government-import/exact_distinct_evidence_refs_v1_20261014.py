"""Per-load/per-phase exact path/SHA identity set; no mtime or cross-phase cache."""
from pathlib import PurePosixPath

def distinct_refs(refs):
    seen={}
    for ref in refs:
        path=ref['path'];sha=ref['sha256'];p=PurePosixPath(path)
        assert isinstance(path,str) and path and not p.is_absolute() and '..'not in p.parts
        assert isinstance(sha,str) and len(sha)==64 and all(c in '0123456789abcdef'for c in sha)
        if path in seen:assert seen[path]['sha256']==sha, 'Conflicting SHA declarations for exact same evidence path: '+path
        else:seen[path]=dict(ref)
    return list(seen.values())

def check_distinct_refs(refs,check):
    result=distinct_refs(refs)
    for q in result:check(q)
    return result
