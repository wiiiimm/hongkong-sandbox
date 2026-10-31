"""Resolve one explicitly archived renderer revision; never waive other hashes."""
from run import ROOT,read,digest
DOC=ROOT/'docs/astra-city/government-import/government-xl-lai-chi-kok-renderer-depth-integration-v1-20261019'
OLD='395ef41515ace0a26d5f23d5c3ba72efa56aacc4692d2bedf77b5d353d948b32'
NEW='2c792243a0b12b1b4de4ed8f16467a1a0ef9507a76160291ddddf81472afc7b3'
def resolve(path,sha):
 p=ROOT/path
 if path=='3d-viewer/city/world.js'and sha==OLD:
  t=read(DOC/'transition.json');assert t['originalPath']==path and t['originalSHA256']==OLD and t['current']==dict(path=path,sha256=NEW)
  assert digest(p.read_bytes())==NEW
  p=DOC/'original-world.js';assert t['archivedOriginal']==dict(path=str(p.relative_to(ROOT)),sha256=OLD)
 assert digest(p.read_bytes())==sha,path
 return p
