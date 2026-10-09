"""Fresh complete original six-actor support topology; no publication acceptance."""
import json,sys,subprocess,uuid,time
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from original_multi_actor_support_graph_20261009 import verify

BATCH='xl-terrain-recovery-20261009-market-six-exact-assembly-support'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-market-six-original-physical-v5-20261009'
GEOMETRY=HERE/'local/government-xl-terrain-recovery-market-six-original-physical-v5-20261009/runtime-geometry.json.gz'
CENSUS=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-ground-anchored-support-v4/diagnostic.json.gz'

def owned():
    assert not DOC.exists();lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    selection=read(PHYSICAL/'selection.json.gz');assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256']
    assert read(PHYSICAL/'neon-sync.json')['resultVerified']
    census=read(CENSUS);runtime={r['uid']:r for r in read(GEOMETRY)['rows']};cs={r['uid']:r for r in census['rows']}
    assert set(runtime)==set(cs)=={r['uid'] for r in selection['rows']}
    refs=[GEOMETRY,CENSUS,PHYSICAL/'selection.json.gz',PHYSICAL/'result.json',Path(__file__),HERE/'original_multi_actor_support_graph_20261009.py',HERE/'test_original_multi_actor_support_graph_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'xl-terrain-recovery-20261009-market-six-ground-anchored-support-v4.mjs']
    for path,sha in census['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    actors=[];components=[];ground_interfaces=[];triangles=[];cursor=0;ground_hashes={}
    for row in selection['rows']:
        uid=row['uid'];g=runtime[uid];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==g['sourceSHA256']==row['sourceSHA256'];refs.append(asset)
        tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
        assert len(tri)==row['native']['model']['triangles']==cs[uid]['sourceTriangles']
        actors.append(dict(uid=uid,sourceSHA256=digest(raw),originalStreamBindingSHA256=digest(json.dumps(source_stream_binding(raw),sort_keys=True,separators=(',',':')).encode()),globalFaceRange=[cursor,cursor+len(tri)],completeOriginalFaceCount=len(tri),originalWorldTrianglesSHA256=digest(tri.tobytes())))
        ground_hashes[uid]=digest(np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3).tobytes())
        for c in cs[uid]['rows']:
            faces=c['originalRuntimeFaces'];assert c['triangles']==len(faces)
            bounds=[tri[faces].min(axis=(0,1)).tolist(),tri[faces].max(axis=(0,1)).tolist()]
            assert np.max(np.abs(np.asarray(bounds)-np.asarray(c['bounds'])))<1e-10,'Runtime component/source coordinates changed'
            components.append(dict(actorUID=uid,globalOriginalFaces=[cursor+i for i in faces],bounds=bounds))
            ground_interfaces.append(c['groundOnlyInterface'])
        triangles.append(tri);cursor+=len(tri)
    tri=np.concatenate(triangles);contacts=[];tested=0;started=time.monotonic()
    rational={}
    def face(i):
        if i not in rational:rational[i]=rational_face(tri[i])
        return rational[i]
    for a,ca in enumerate(components):
        for b in range(a+1,len(components)):
            cb=components[b];lo=np.maximum(ca['bounds'][0],cb['bounds'][0]);hi=np.minimum(ca['bounds'][1],cb['bounds'][1])
            if np.any(lo>hi):continue
            # Exact 3D AABB broadphase only; positive contact is independently
            # recomputed with binary-float Fraction geometry, never tolerance.
            af=np.asarray(ca['globalOriginalFaces'],int);bf=np.asarray(cb['globalOriginalFaces'],int)
            small,large=(af,bf) if len(af)<=len(bf) else (bf,af)
            polygons=shapely.box(tri[large,:,0].min(axis=1),tri[large,:,2].min(axis=1),tri[large,:,0].max(axis=1),tri[large,:,2].max(axis=1));tree=shapely.STRtree(polygons)
            witness=None
            for i in small:
                t=tri[i];xy=shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max())
                for k in tree.query(xy):
                    j=int(large[k]);u=tri[j]
                    if t[:,1].max()<u[:,1].min() or u[:,1].max()<t[:,1].min():continue
                    if not np.any(np.cross(t[1]-t[0],t[2]-t[0])) or not np.any(np.cross(u[1]-u[0],u[2]-u[0])):continue
                    tested+=1
                    if tested%500==0:assert reservations.heartbeat(lease)['ok']
                    if len(intersection_points(face(int(i)),face(j)))>=2:
                        witness=[int(i),j] if int(i) in ca['globalOriginalFaces'] else [j,int(i)];break
                if witness:break
            if witness:contacts.append(dict(components=[a,b],globalOriginalFaces=witness))
        assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(component=a,total=len(components),contacts=len(contacts),exactPairsTested=tested,elapsedSeconds=time.monotonic()-started)),flush=True)
    binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),currentDrawnGroundSHA256=digest(json.dumps(ground_hashes,sort_keys=True,separators=(',',':')).encode()),groundInterfacesInputSHA256=digest(CENSUS.read_bytes()),groundInterfacesSHA256=digest(json.dumps(ground_interfaces,sort_keys=True,separators=(',',':'),allow_nan=False).encode()),supportScope='complete-current-drawn-ground-only')
    result=verify(tri,actors,components,ground_interfaces,contacts,expected_binding=binding,current_binding=binding)
    result.update(actors=actors,components=components,groundInterfaces=ground_interfaces,contactWitnesses=contacts,binding=binding,groundHashesByUID=ground_hashes,exactPairsTested=tested,elapsedSeconds=time.monotonic()-started,manifestSHA256=selection['manifestSHA256'],evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in sorted(set(refs))])
    assert reservations.owns(lease);save(DOC/'diagnostic.json.gz',result)
    print(json.dumps({k:result[k] for k in ['supportInterfaceAccepted','completeOriginalFaces','completeOriginalComponentCount','genuineGroundAnchorComponents','reasons']}),flush=True)

def start():
    selection=read(PHYSICAL/'selection.json.gz');claim=reservations.claim('codex-market-support-'+str(uuid.uuid4()),['building:'+r['uid'] for r in selection['rows']]+['terrain-patch:'+r['uid'] for r in selection['rows']],batch=BATCH,ttl=3600);assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'owned'],cwd=ROOT,check=True)
if __name__=='__main__':owned() if len(sys.argv)>1 else start()
