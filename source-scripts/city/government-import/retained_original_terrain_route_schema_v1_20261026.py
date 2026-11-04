"""Map the diagnostic sourceSHA256 alias after authenticating the exact terrain bytes."""
import copy
from pathlib import Path
import hashlib


def normalize_route(root, route):
    out=copy.deepcopy(route)
    assert isinstance(out.get('sourceSHA256'),str)and len(out['sourceSHA256'])==64
    assert out.get('sha256',out['sourceSHA256'])==out['sourceSHA256'],'Conflicting terrain checksum aliases'
    path=(Path(root)/out['source']).resolve();assert path.is_relative_to(Path(root).resolve())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==out['sourceSHA256'],'Exact tested terrain bytes changed'
    out['sha256']=out['sourceSHA256']
    assert {k:v for k,v in out.items()if k!='sha256'}=={k:v for k,v in route.items()if k!='sha256'}
    return out
