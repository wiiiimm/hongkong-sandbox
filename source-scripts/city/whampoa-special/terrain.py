"""Reuse native-TIN sampling and guarded parent-aligned one-metre patch preparation."""
import pathlib,json,sys,hashlib,importlib.util,numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/whampoa-special'
sys.path.insert(0,str(ROOT/'source-scripts/city/assembly-support-review'));import native_terrain as native;import terrain_patches as patches
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=read(DOC/'support.json');podium=report['podium'];row={'uid':podium['uid'],'name':'The Whampoa hull/platform','rim':podium['rim']};(DOC/'terrain-input-report.json').write_text(json.dumps({'rows':[row]},indent=2)+'\n')
mp=ROOT/'source-scripts/city/landmark-acquisition/batches/terrain-final-increment/staged/11-NE-21C/manifest.json';m=read(mp);t=m['terrain'];files=[]
for rel in [t['url']]+[p for p in t['sourceHashes']if p.endswith('.bin')]:
 path=mp.parent/rel;files.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size})
source={'sheet':m['tile'],'revision':m['tileRevision'],'manifest':str(mp.relative_to(ROOT)),'manifestSha256':sha(mp),'worldBounds':t['worldBounds'],'files':files,'sourceFilesVerified':True}
_,_,_,_,usable,tree=native.terrain_index(mp.parent);pts=np.array([[r['position'][0],r['position'][2]]for r in row['rim']]);values=native.samples(pts,usable,tree)
assert np.isfinite(values).all()
evidence={'issue':'HKS-219','sources':[source],'sourceGridProposals':[{'uid':row['uid']}],'rim':[{'position':r['position'],'currentGround':r['ground'],'nativeGround':float(v),'nativeGap':r['position'][1]-float(v)}for r,v in zip(row['rim'],values)]}
(DOC/'native-terrain.json').write_text(json.dumps(evidence,indent=2)+'\n');patchInputs=HERE/'patch-inputs';patchInputs.mkdir(exist_ok=True);(patchInputs/'report.json').write_bytes((DOC/'terrain-input-report.json').read_bytes());(patchInputs/'native-terrain.json').write_bytes((DOC/'native-terrain.json').read_bytes());patches.HERE=HERE;patches.OUT=patchInputs;patches.main();(DOC/'terrain-patches.json').write_bytes((patchInputs/'terrain-patches.json').read_bytes());print('Native rim gap range',min(r['nativeGap']for r in evidence['rim']),max(r['nativeGap']for r in evidence['rim']))
