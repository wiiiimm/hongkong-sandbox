"""Attach audited overlap metadata while preserving native geometry verbatim."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];evidence=ROOT/'docs/astra-city/assembly-support-review/branksome-native-overlap.json';e=json.loads(evidence.read_text());path=ROOT/'source-scripts/city/assembly-support-review/exact-tin-next/support-exact-tin-232907-0.json';p=json.loads(path.read_text());before=json.dumps([p['nativeMesh']['position'],p['nativeMesh']['index']],separators=(',',':'));p['nativeMesh']['sourceOverlap']={'measuredProjectedExcessM2':e['stagedProjectedExcessM2'],'nativeProjectedExcessM2':e['nativeProjectedExcessM2'],'evidencePath':str(evidence.relative_to(ROOT)),'evidenceSHA256':hashlib.sha256(evidence.read_bytes()).hexdigest(),'policy':'highest-native-surface'};assert before==json.dumps([p['nativeMesh']['position'],p['nativeMesh']['index']],separators=(',',':'));path.write_text(json.dumps(p,separators=(',',':'))+'\n');sha=hashlib.sha256(path.read_bytes()).hexdigest()
for rel in ['docs/astra-city/assembly-support-review/exact-tin-next.json','docs/astra-city/assembly-support-review/visual-acceptance-exact-next.json','source-scripts/city/assembly-support-review/plan-exact-next.json']:
 f=ROOT/rel;d=json.loads(f.read_text());rows=d.get('patches',d.get('requiredTerrainPatches',[]))
 for row in rows:
  if row['path']==str(path.relative_to(ROOT)):row['sha256']=sha;row['sourceOverlap']=p['nativeMesh']['sourceOverlap']
 f.write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'patchSha256':sha,'positionAndIndexUnchanged':True,'evidenceSha256':p['nativeMesh']['sourceOverlap']['evidenceSHA256']}))
