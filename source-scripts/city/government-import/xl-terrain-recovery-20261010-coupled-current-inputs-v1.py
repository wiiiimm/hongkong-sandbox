"""Combine independently current-verified originals, without support/role credit."""
import argparse,re
from pathlib import Path
from run import ROOT,read,save,digest
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--preflight',action='append',required=True);p.add_argument('--batch',required=True);a=p.parse_args();assert len(a.preflight)>1 and len(set(a.preflight))==len(a.preflight) and re.fullmatch('[a-z0-9-]+',a.batch)
 doc=ROOT/'docs/astra-city/government-import'/a.batch;assert not doc.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';sha=digest(manifest.read_bytes());rows=[];contexts=[];proofs=[];refs=[ref(Path(__file__)),ref(manifest)]
 for inputpath in a.preflight:
  folder=ROOT/inputpath;selection=read(folder/'check-selection.json.gz');preflight=read(folder/'indexed-preflight.json');assert selection['manifestSHA256']==preflight['manifestSHA256']==sha and len(selection['rows'])==len(preflight['rows'])==1
  r=selection['rows'][0];proof=preflight['rows'][0];assert proof['uid']==r['uid'] and proof['canStartTerrainWork'] is True and proof['identity']['passed'] is True and proof['sourceSHA256']==r['sourceSHA256'];assert digest((ROOT/r['candidate']['path']).read_bytes())==r['sourceSHA256']
  context=read(folder/'context.json.gz')['rows'];assert len(context)==1 and context[0]['uid']==r['uid'] and context[0]['sourceSHA256']==r['sourceSHA256']
  for path,h in context[0]['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/path).read_bytes())==h,'Changed current regional forms'
  for v in preflight['evidenceRefs']:assert ref(ROOT/v['path'])==v,'Changed independent preflight input'
  rows.append(r);contexts.extend(context);proofs.append(proof);refs.extend(preflight['evidenceRefs']);refs.extend(ref(f) for f in folder.rglob('*') if f.is_file())
 assert len({r['uid'] for r in rows})==len(rows) and digest(manifest.read_bytes())==sha
 save(doc/'check-selection.json.gz',dict(rows=rows,batch=a.batch,manifestSHA256=sha));save(doc/'context.json.gz',dict(rows=contexts));save(doc/'indexed-preflight.json',dict(rows=proofs,manifestSHA256=sha,evidenceRefs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path']),sourceGeometryChanges=0,allIdentitiesFreshlyPassed=True,structuralSupportStillRequiresCompleteOriginalProof=True,fullAcceptance=False,publication=False))
 print(dict(batch=a.batch,uids=[r['uid'] for r in rows]),flush=True)
if __name__=='__main__':main()
