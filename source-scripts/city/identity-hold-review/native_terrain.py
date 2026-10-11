"""Reuse native terrain TIN sampling for the five newly resolved source identities."""
import pathlib,json,importlib.util,numpy as np,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-hold-review'
s=importlib.util.spec_from_file_location('shared_native_terrain',ROOT/'source-scripts/city/assembly-support-review/native_terrain.py');lib=importlib.util.module_from_spec(s);s.loader.exec_module(lib)
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=read(DOC/'support.json');cat={m['uid']:m for m in read(HERE/'identity-approved/catalogue.json')['models']};inputs=read(ROOT/'docs/astra-city/landmark-preflight/terrain-inputs.json');rows=[];used=[]
def overlaps(a,b):return a[0][0]<=b[1][0] and b[0][0]<=a[1][0] and a[0][2]<=b[1][2] and b[0][2]<=a[1][2]
for mp in HERE.glob('airport-terrain*/staged/*/manifest.json'):
 m=read(mp);t=m['terrain'];files=[]
 for rel in [t['url']]+[p for p in t['sourceHashes']if p.endswith('.bin')]:
  path=mp.parent/rel;files.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size})
 inputs['nativeSources'].append({'sheet':m['tile'],'revision':m['tileRevision'],'manifest':str(mp.relative_to(ROOT)),'manifestSha256':sha(mp),'worldBounds':t['worldBounds'],'files':files,'sourceFilesVerified':True})
acc={p['uid']:np.full(len(p['rim']),-np.inf)for p in report['rows']};sourceByUid={p['uid']:[]for p in report['rows']}
for source in inputs['nativeSources']:
 targets=[p for p in report['rows']if overlaps(cat[p['uid']]['worldBounds'],source['worldBounds'])]
 if not targets:continue
 mp=ROOT/source['manifest'];assert sha(mp)==source['manifestSha256']
 for f in source['files']:assert sha(ROOT/f['path'])==f['sha256']
 _,_,_,_,usable,tree=lib.terrain_index(mp.parent);used.append(source)
 for p in targets:
  points=np.array([[r['position'][0],r['position'][2]]for r in p['rim']]);acc[p['uid']]=np.maximum(acc[p['uid']],lib.samples(points,usable,tree));sourceByUid[p['uid']].append(source['manifest'])
for p in report['rows']:
 vals=acc[p['uid']];out=[]
 for r,v in zip(p['rim'],vals):out.append({**r,'nativeTerrain':float(v)if np.isfinite(v)else None,'nativeGap':float(r['position'][1]-v)if np.isfinite(v)else None})
 rows.append({'uid':p['uid'],'nativeSources':sourceByUid[p['uid']],'rim':out,'rimSamples':len(out),'nativeCovered':sum(r['nativeTerrain']is not None for r in out),'nativeContactWithin2m':sum(r['nativeGap']is not None and abs(r['nativeGap'])<=2 for r in out)})
result={'issue':'HKS-214','sourceSupportSHA256':sha(DOC/'support.json'),'rows':rows,'nativeSources':used,'terrainChanged':False,'verticalScale':1,'method':'Existing multi-primitive native decoder and exact TIN barycentric samples at all low-rim vertices; no extrapolation or generated terrain edit.'};(DOC/'native-terrain.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items()if k!='rim'}for r in rows]))
