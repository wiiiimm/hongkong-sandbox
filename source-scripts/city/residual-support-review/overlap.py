"""Reuse the existing native-overlap evidence and Float32 ray validation."""
import pathlib,json,hashlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review';old='source-scripts/city/assembly-support-review/exact-tin-next/support-exact-tin-232907-0.json';new='source-scripts/city/residual-support-review/exact-tin/support-exact-tin-234162-0.json';oldDoc='docs/astra-city/assembly-support-review/branksome-native-overlap.json';newDoc='docs/astra-city/residual-support-review/island-native-overlap.json'
s=(ROOT/'source-scripts/city/assembly-support-review/native_overlap_review.py').read_text().replace(old,new).replace(oldDoc,newDoc).replace('support-exact-tin-232907-0','support-exact-tin-234162-0');exec(compile(s,str(HERE/'overlap.py'),'exec'),{'__file__':str(HERE/'overlap.py')})
s=(ROOT/'source-scripts/city/assembly-support-review/native_overlap_ray_test.mjs').read_text().replace(old,new).replace(oldDoc,newDoc);(HERE/'overlap-ray.generated.mjs').write_text(s);subprocess.run(['/Users/williamli/.nvm/versions/node/v24.17.0/bin/node',str(HERE/'overlap-ray.generated.mjs')],check=True)
p=json.loads((ROOT/new).read_bytes());e=json.loads((ROOT/newDoc).read_bytes());p['nativeMesh']['sourceOverlap']={'measuredProjectedExcessM2':e['stagedProjectedExcessM2'],'nativeProjectedExcessM2':e['nativeProjectedExcessM2'],'evidencePath':newDoc,'evidenceSHA256':hashlib.sha256((ROOT/newDoc).read_bytes()).hexdigest(),'policy':'highest-native-surface'};(ROOT/new).write_text(json.dumps(p,separators=(',',':'))+'\n');bundle=json.loads((DOC/'terrain-bundle.json').read_bytes())
for b in bundle['bundles']:
 for row in b['patches']:
  if row['path']==new:row['sha256']=hashlib.sha256((ROOT/new).read_bytes()).hexdigest()
(DOC/'terrain-bundle.json').write_text(json.dumps(bundle,indent=2)+'\n')
