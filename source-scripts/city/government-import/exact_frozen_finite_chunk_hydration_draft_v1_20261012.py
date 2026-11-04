"""Pure integrity gate for explicitly historical immutable proof rows, no code alias."""
import hashlib,json,gzip
from pathlib import Path

def load_chunk(root, expected_ref, expected_contract):
 root=Path(root).resolve();path=(root/expected_ref['path']).resolve();assert path.is_relative_to(root)and str(path.relative_to(root))==expected_ref['path'];raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected_ref['sha256']
 decoded=gzip.decompress(raw)if path.name.endswith('.gz')else raw;q=json.loads(decoded);assert set(q)=={'contract','rows'}and q['contract']==expected_contract
 c=expected_contract;assert type(c['firstFace'])is int and type(c['exclusiveLastFace'])is int and 0<=c['firstFace']<c['exclusiveLastFace'];rows=q['rows'];assert [r['face']for r in rows]==list(range(c['firstFace'],c['exclusiveLastFace']))
 for r in rows:
  s=r['selection'];assert s['completeGroundSHA256']==c['groundSHA256']and s['completeGroundFacetCount']==c['completeGroundFaces']and s['everyNoncandidateStrictlyDisjoint']and s['touchingAndCollapsedProjectionsRetained'];assert r['originalGroundFaceBySelectedKernelFace']==s['selectedOriginalGroundFaces']
 return rows

def hydrate(root, declared_chunks, source_body_labels):
 groups={};references=[]
 for row in declared_chunks:
  c=row['originalContract'];rows=load_chunk(root,row['actualRef'],c)
  for r in rows:assert r['originalBody']==source_body_labels.get(r['face'])
  key=(c['worldSHA256'],c['groundSHA256']);groups.setdefault(key,[]).append((c['firstFace'],c['exclusiveLastFace'],rows));references.append(row['actualRef'])
 output={}
 for key,parts in groups.items():
  parts.sort(key=lambda p:p[0]);assert parts[0][0]==0 and all(a[1]==b[0]for a,b in zip(parts,parts[1:]));rows=[r for _,_,rs in parts for r in rs];assert [r['face']for r in rows]==list(range(parts[-1][1]));output[key]=rows
 return output,references
