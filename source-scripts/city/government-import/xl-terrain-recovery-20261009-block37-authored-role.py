"""New unchanged provider hierarchy, authored roof paths and full interactions."""
import collections
import gzip
import json
import struct
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_shell_intersections_20261009 import rational_face,intersection_points

BATCH='xl-terrain-recovery-20261009-block37-authored-role'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LEASE='/tmp/xl-terrain-recovery-20261009-block37-authored-role-lease.json'
PRIOR=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-block37-wall-context'
MODEL='B340653488502062G0'
RAW=HERE/'local/government-xl-remaining-held-20260923/recovered/sheets/7-NW-3D/decoded/BUILDING'/MODEL/(MODEL+'.gltf')


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def accessor(document,binary,index):
    item=document['accessors'][index];view=document['bufferViews'][item['bufferView']]
    assert not item.get('sparse') and not item.get('normalized')
    dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[item['componentType']]
    width={'VEC3':3,'SCALAR':1}[item['type']]
    offset=view.get('byteOffset',0)+item.get('byteOffset',0)
    assert view.get('byteStride',np.dtype(dtype).itemsize*width)==np.dtype(dtype).itemsize*width
    return np.frombuffer(binary,dtype=dtype,count=item['count']*width,offset=offset).reshape(item['count'],width)


def main():
    assert not (DOC/'role-context.json.gz').exists(),'Fresh source-role context required'
    lease=read(LEASE);assert reservations.heartbeat(lease)['ok']
    row=read(PRIOR/'diagnostic.json.gz')
    geometry_path=ROOT/next(x['path'] for x in row['evidenceRefs'] if x['path'].endswith('runtime-geometry.json.gz'))
    g=read(geometry_path)['rows'][0]
    tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    native=read(ROOT/'docs/astra-city/government-import/government-xl-sustained-131-followthrough-20261006-228547-0/selection.json.gz')['rows'][0]
    asset=ROOT/native['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
    packed=gzip.decompress(asset.read_bytes());length,kind=struct.unpack_from('<II',packed,12)
    assert kind==0x4e4f534a
    glb=json.loads(packed[20:20+length]);blen,bkind=struct.unpack_from('<II',packed,20+length)
    assert bkind==0x004e4942;gbin=packed[28+length:28+length+blen]
    raw=read(RAW);rbin=(RAW.parent/raw['buffers'][0]['uri']).read_bytes()
    assert raw['nodes']==glb['nodes'] and raw['scenes']==glb['scenes'] and raw['materials']==glb['materials']
    assert len(raw['meshes'])==len(glb['meshes'])==1
    rp=raw['meshes'][0]['primitives'][0];gp=glb['meshes'][0]['primitives'][0]
    ri=accessor(raw,rbin,rp['indices']).ravel();gi=accessor(glb,gbin,gp['indices']).ravel()
    assert len(ri)==len(gi)==len(tri)*3
    attributes={}
    for name in ['POSITION','NORMAL','COLOR_0']:
        a=accessor(raw,rbin,rp['attributes'][name])[ri]
        b=accessor(glb,gbin,gp['attributes'][name])[gi]
        assert np.array_equal(a,b),name+' original triangle stream differs'
        attributes[name]={'triangleStreamSHA256':digest(a.tobytes()),'allValuesIdentical':True}
    members=set(row['affectedComponentContexts'][0]['componentFaces'])
    affected={f['sourceFace'] for f in row['faces'] if not f['inClosedBuriedComponent']
              and f['minimum'] and f['minimum']['minimumGapM']<-.5}
    byface={f['sourceFace']:f for f in row['faces']}
    edges={}
    for i in members:
        for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
            edges.setdefault(tuple(sorted([tuple(a),tuple(b)])),[]).append(i)
    adj={i:set() for i in members}
    for ids in edges.values():
        for i in ids:adj[i].update(set(ids)-{i})
    roofs={i for i in members if byface[i]['upward']}
    previous={i:None for i in roofs};todo=collections.deque(sorted(roofs))
    while todo:
        i=todo.popleft()
        for j in sorted(adj[i]):
            if j not in previous and abs(byface[j]['normalYRatio'])<=.25:
                previous[j]=i;todo.append(j)
    paths=[]
    for i in sorted(affected):
        path=[i]
        while path[-1] in previous and previous[path[-1]] is not None:path.append(previous[path[-1]])
        paths.append({'sourceFace':i,'authoredWallToRoofPath':path,
            'exposedUpwardRoofReached':path[-1] in roofs,
            'minimumAuthoredWallHeightHKPD':float(tri[i,:,1].min()),
            'roofMinimumGroundGapM':byface[path[-1]]['minimum']['minimumGapM'] if path[-1] in roofs else None})
    rational=[rational_face(t.tolist()) for t in tri]
    low,high=tri.min(axis=1),tri.max(axis=1)
    scope=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-shell-cohort/diagnostic.json.gz'
    original=next(r for r in read(scope)['rows'] if r['uid']==row['uid'])
    interactions=[]
    for shell_index,shell in enumerate(original['shells']):
        own=set(shell['componentFaces']);others=np.array([i for i in range(len(tri)) if i not in own])
        pairs=0;contacts=[]
        for i in sorted(own):
            hits=others[np.all((low[others]<=high[i])&(high[others]>=low[i]),axis=1)]
            pairs+=len(hits)
            for j in hits:
                points=intersection_points(rational[i],rational[j])
                if points:
                    contacts.append({'columnFace':i,'otherSourceFace':int(j),
                        'otherFaceInMainRoofComponent':int(j) in members,
                        'columnFaceUpward':byface[i]['upward'],'otherFaceUpward':byface[int(j)]['upward'],
                        'points':[[str(v) for v in p] for p in sorted(points)]})
        interactions.append({'shellIndex':shell_index,'originalFaces':sorted(own),
            'wholeOtherSourceFaces':len(others),'exactAABBCandidatePairs':int(pairs),'contacts':contacts,
            'contactCount':len(contacts),'allContactsInMainRoofComponent':all(c['otherFaceInMainRoofComponent'] for c in contacts),
            'upwardCapContactCount':sum(c['columnFaceUpward'] for c in contacts)})
        assert reservations.heartbeat(lease)['ok']
        print(json.dumps({'shell':shell_index,'pairs':int(pairs),'contacts':len(contacts),
                         'capContacts':interactions[-1]['upwardCapContactCount']}),flush=True)
    result={'uid':row['uid'],'modelId':MODEL,'sourceSHA256':row['sourceSHA256'],'sourceFaces':len(tri),
        'providerOriginalHierarchy':{k:raw.get(k) for k in ['asset','scenes','nodes','materials']},
        'rawProviderTriangleAttributes':attributes,'originalMeshPrimitives':len(raw['meshes'][0]['primitives']),
        'wallRolePaths':paths,'all857WallFacesHaveOriginalRoofPaths':all(p['exposedUpwardRoofReached'] for p in paths),
        'affectedOriginalBaseHeightRangeHKPD':[min(p['minimumAuthoredWallHeightHKPD'] for p in paths),max(p['minimumAuthoredWallHeightHKPD'] for p in paths)],
        'closedComponentsFullOriginalInteractions':interactions,'allOriginalSourceFacesAccountedFor':True,
        'roleVerifiedForAcceptance':False,'sourceGeometryChanges':0,'installationApproved':False,'publication':False,
        'evidenceRefs':[ref(p) for p in [Path(__file__),RAW,RAW.parent/raw['buffers'][0]['uri'],asset,
          geometry_path,scope,PRIOR/'diagnostic.json.gz',PRIOR/'coverage-v2.json.gz',
          HERE/'exact_original_shell_intersections_20261009.py']],
        'qualification':'All original provider triangle positions, normals and colours equal packed indexed triangle streams exactly; unchanged hierarchy/materials. New original-edge wall-to-roof paths and exact rational whole-source component interactions. Positive classification and a reviewed typed contact contract remain separate; no inherited failure is converted to acceptance.'}
    assert reservations.owns(lease)
    save(DOC/'role-context.json.gz',result)


if __name__=='__main__':main()
