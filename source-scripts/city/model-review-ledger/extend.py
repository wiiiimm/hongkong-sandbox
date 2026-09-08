"""Append exact source inventory supplements without discarding prior review decisions.
Default is a dry run. Only the integration owner updates the checkout pointer.
"""
import argparse, hashlib, json, os, tempfile
from pathlib import Path
import ledger
ROOT=ledger.ROOT
POINTER=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'
def digest(value): return hashlib.sha256(value).hexdigest()
def build(current, supplements):
 parts={p['uid']:p for p in current['parts']}
 for supplement in supplements:
  for part in supplement['parts']:
   if part['uid'] in parts and parts[part['uid']]!=part:
    raise ValueError('Conflicting existing source metadata: '+part['uid'])
   parts[part['uid']]=part
 ordered=[parts[k] for k in sorted(parts)]
 snapshot=digest(json.dumps(ordered,sort_keys=True,separators=(',',':')).encode())[:16]
 return {'issue':'HKS-214','snapshotId':snapshot,'derivedFrom':current['snapshotId'],'parts':ordered,'qualification':'Source components, including supplemental requests, not whole-landmark or regional completion. Prior decisions inherit only for identical UID/source state/SHA.'}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--supplement',action='append',required=True);p.add_argument('--expected-snapshot',required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
 pointer_raw=POINTER.read_bytes();pointer=json.loads(pointer_raw)
 if pointer['snapshotId']!=a.expected_snapshot: raise ValueError('Current inventory changed; reread before extending')
 current=json.loads((ROOT/pointer['inventory']).read_bytes());paths=[ROOT/x for x in a.supplement]
 result=build(current,[json.loads(x.read_bytes()) for x in paths]);result['inputs']={str(x.relative_to(ROOT)):digest(x.read_bytes()) for x in paths}
 out=POINTER.parent/('source-review-inventory-'+result['snapshotId']+'.json')
 print(json.dumps({'previous':current['snapshotId'],'snapshot':result['snapshotId'],'parts':len(result['parts']),'added':len(result['parts'])-len(current['parts']),'apply':a.apply}))
 if not a.apply:return
 encoded=(json.dumps(result,indent=2)+'\n').encode()
 if out.exists():
  if out.read_bytes()!=encoded:raise ValueError('Immutable snapshot file collision')
 else:out.write_bytes(encoded)
 status=ledger.seed(out,inherit=current['snapshotId'])
 if POINTER.read_bytes()!=pointer_raw:raise ValueError('Pointer changed during seeding; new snapshot retained, pointer not overwritten')
 next_pointer={'snapshotId':result['snapshotId'],'inventory':str(out.relative_to(ROOT)),'previousSnapshots':pointer.get('previousSnapshots',[])+[current['snapshotId']],'qualification':result['qualification']}
 fd,name=tempfile.mkstemp(prefix='.source-review-',dir=POINTER.parent)
 try:
  with os.fdopen(fd,'w') as f:json.dump(next_pointer,f,indent=2);f.write('\n')
  os.replace(name,POINTER)
 finally:
  if os.path.exists(name):os.unlink(name)
 print(json.dumps(status,default=str))
if __name__=='__main__':main()
