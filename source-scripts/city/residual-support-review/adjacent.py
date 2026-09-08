"""Follow-up exact terrain audit using separately acquired, checksummed adjacent sheets."""
import pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/residual-support-review';read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();extra=[]
for s in read(ROOT/'docs/astra-city/assembly-support-review/residual-terrain-verification.json')['sheets']:
 path=ROOT/s['manifest'];assert sha(path)==s['manifestSHA256'];m=read(path);gltf=path.parent/m['terrain']['url'];assert sha(gltf)==s['derivedGeometrySHA256'];files=[{'path':str(gltf.relative_to(ROOT)),'sha256':sha(gltf)}]
 for f in s['verifiedSourceMembers']:assert sha(ROOT/f['path'])==f['sha256']
 for b in read(gltf)['buffers']:
  p=gltf.parent/b['uri'];digest=sha(p);assert digest in m['terrain']['sourceHashes'].values();files.append({'path':str(p.relative_to(ROOT)),'sha256':digest})
 extra.append({'sheet':s['sheet'],'manifest':s['manifest'],'manifestSha256':s['manifestSHA256'],'worldBounds':s['worldBounds'],'files':files,'originalSourceMembers':s['verifiedSourceMembers']})
(DOC/'adjacent-sources.json').write_text(json.dumps(extra,indent=2)+'\n');source=(HERE/'native_audit.py').read_text().replace(";work={}",";sources+=read(DOC/'adjacent-sources.json');meshes['rows']=[m for m in meshes['rows']if m['uid']in ['landsd/229653:0','landsd/230686:0']];work={}").replace("DOC/'native-audit.json'","DOC/'native-audit-adjacent.json'");exec(compile(source,str(HERE/'native_audit.py'),'exec'),{'__file__':str(HERE/'native_audit.py'),'__name__':'__main__'})
