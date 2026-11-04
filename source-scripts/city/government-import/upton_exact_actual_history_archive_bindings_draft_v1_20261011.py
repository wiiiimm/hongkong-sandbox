"""Unexecuted exact actual-history resolver; never rewrites a historical ref.

A ROOT-reviewed explicit contract is required. No inferred archive, recursive
alias, metadata exemption or substitution of new live bytes as old evidence.
"""
from pathlib import Path
import json
from hashlib import sha256

def digest(b):return sha256(b).hexdigest()
def load_contract(root,path,expected_sha):
 p=root/path;assert digest(p.read_bytes())==expected_sha
 d=json.loads(p.read_bytes());assert d['actualHistoricalBytesOnly'] is True
 entries=d['historicalArchives'];assert len(entries)==len({(e['originalPath'],e['historicalSHA256']) for e in entries})
 for e in entries:
  assert e['actualArchive']['sha256']==e['historicalSHA256']
  a=Path(e['actualArchive']['path']);assert not a.is_absolute() and '..' not in a.parts
  assert digest((root/a).read_bytes())==e['historicalSHA256']
 return d

def exact_ref(root,e,contract):
 p=root/e['path']
 if p.is_file() and digest(p.read_bytes())==e['sha256']:
  return dict(originalEvidenceRef=e,actualVerifiedFile=e,historicalArchiveUsed=False)
 matches=[a for a in contract['historicalArchives'] if (a['originalPath'],a['historicalSHA256'])==(e['path'],e['sha256'])]
 assert len(matches)==1, 'Missing exact actual historical archive: '+e['path']+' '+e['sha256']
 a=matches[0]['actualArchive'];assert digest((root/a['path']).read_bytes())==e['sha256']
 return dict(originalEvidenceRef=e,actualVerifiedFile=a,historicalArchiveUsed=True)
