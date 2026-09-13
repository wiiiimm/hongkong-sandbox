"""Freeze review decisions and exact embedded-runtime hashes; read-only Neon refresh."""
import argparse,json,pathlib,hashlib,subprocess,sys,datetime
R=pathlib.Path(__file__).resolve().parents[3];S=pathlib.Path(__file__).parent;p=argparse.ArgumentParser();p.add_argument('--refresh',action='store_true');args=p.parse_args();read=lambda p:json.loads(p.read_bytes())
if args.refresh:
 subprocess.run([sys.executable,str(R/'source-scripts/city/enhancement-screening/screen.py'),'export'],check=True)
 sys.path.insert(0,str(R/'source-scripts/city/landmark-completion-audit'));from audit import capture
 capture(read(R/'docs/astra-city/model-integration-20260909/current-source-review.json')['snapshotId'])
frozen=read(R/'docs/astra-city/landmark-completion-audit/neon-snapshot.json');rows=[{k:r[k] for k in ['uid','source_sha256','review_state']}for r in frozen['rows'] if r['review_state']=='installed-verified'];lookup={r['uid']:r for r in rows};embedded=[]
for t in read(R/'3d-viewer/city/data/manifest.json')['tiles']:
 path=R/'3d-viewer'/t['url']
 for b in read(path)['buildings']:
  if not b.get('modelGeometry') or b['uid'] not in lookup:continue
  h=hashlib.sha256(json.dumps(b['modelGeometry'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
  if lookup[b['uid']]['source_sha256']!=h:continue
  # JSON.stringify is the browser/build representation; canonical Python SHA remains the ledger key.
  code="const fs=require('fs'),crypto=require('crypto'),b=JSON.parse(fs.readFileSync(process.argv[1])).buildings.find(b=>b.uid===process.argv[2]);process.stdout.write(crypto.createHash('sha256').update(JSON.stringify(b.modelGeometry)).digest('hex'));"
  js=subprocess.check_output(['node','-e',code,str(path),b['uid']],text=True);embedded.append({'uid':b['uid'],'sourceSHA256':h,'runtimeDigest':js})
out={'version':1,'snapshotId':frozen['snapshotId'],'capturedAt':frozen['capturedAt'],'rows':rows,'embedded':embedded};(R/'3d-viewer/scripts/building-progress/review-proof.json').write_text(json.dumps(out,indent=2)+'\n');print('Frozen review rows:',len(rows),'embedded byte proofs:',len(embedded))
