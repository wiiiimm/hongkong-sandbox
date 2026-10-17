"""Literal code/metadata contract preparation only; no project imports/DB."""
import ast,difflib,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
H=ROOT/'source-scripts/city/government-import'
OLD=ROOT/'docs/astra-city/government-import/government-xl-lai-chi-kok281463-provider-site-scope-v2-20261013'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 old=json.loads((OLD/'comparison-input-contract.json').read_bytes());pins=dict(old['allInputHashes'])
 for rel,value in pins.items():assert sha(ROOT/rel)==value
 before=OLD/'source-component-comparison-draft-v1.py';after=HERE/'source-component-comparison-draft-v2.py'
 diff=''.join(difflib.unified_diff(before.read_text().splitlines(True),after.read_text().splitlines(True),fromfile=str(before.relative_to(ROOT)),tofile=str(after.relative_to(ROOT))))
 with (HERE/'v1-to-v2.diff').open('x') as stream:stream.write(diff)
 closure=set(old['staticLiteralLocalPythonClosure']);pending=[after,H.parent/'shared-modelling/reservation_runner.py']
 while pending:
  p=pending.pop().resolve();rel=str(p.relative_to(ROOT))
  if rel in closure:continue
  closure.add(rel);pins[rel]=sha(p);tree=ast.parse(p.read_bytes(),filename=str(p))
  for node in ast.walk(tree):
   names=[n.name for n in node.names] if isinstance(node,ast.Import) else ([node.module] if isinstance(node,ast.ImportFrom) and node.module else [])
   for name in names:
    for base in (H,H.parent/'shared-modelling'):
     q=base/(name.replace('.','/')+'.py')
     if q.exists():pending.append(q)
 for p in [OLD/'comparison-input-contract.json',OLD/'actual-metadata-packet-validation.json',HERE/'METHOD-v2.md',HERE/'prepare-contract-v2.py',HERE/'v1-to-v2.diff']:
  pins[str(p.relative_to(ROOT))]=sha(p)
 for rel,value in pins.items():assert sha(ROOT/rel)==value
 new={**old,'allInputHashes':pins,'staticLiteralLocalPythonClosure':sorted(closure),'callerVersion':2,'priorVersionContract':{'path':str((OLD/'comparison-input-contract.json').relative_to(ROOT)),'sha256':sha(OLD/'comparison-input-contract.json')},'priorExactSourceReceipt':{'path':'docs/astra-city/government-import/government-xl-identity-190-actionable-ledger-20261010/result.json','jobId':'d705c0870384ecba840b1252c45b14688f73e165d0cdbc00d4277a6e0e8704ea'},'normalExecutionStillUnexecutedByThisAgent':True}
 with (HERE/'comparison-input-contract-v2.json').open('x') as stream:json.dump(new,stream,indent=2);stream.write('\n')
 print(json.dumps({'pins':len(pins),'all81OldPinsRetained':len(old['allInputHashes'])==81 and all(pins[k]==v for k,v in old['allInputHashes'].items()),'canonicalResources':len(new['canonicalResources']),'literalClosure':len(closure),'callerSHA256':sha(after),'contractSHA256':sha(HERE/'comparison-input-contract-v2.json')}))
if __name__=='__main__':main()
