"""Whole original face/component partition and authored shaft terminal interfaces."""
import collections
import json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from unchanged_open_exterior_paths_20261009 import original_open_paths
from original_shell_diagnostic_20261009 import shell_context
from exact_shell_context_accelerated_20261009 import shell_self_intersections
from exact_closed_shell_point_20261009 import point_membership

BATCH='xl-terrain-recovery-20261009-block37-authored-role'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PRIOR=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-block37-wall-context'
LEASE='/tmp/xl-terrain-recovery-20261009-block37-authored-role-lease.json'


def ref(path):return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}


def main():
    assert not (DOC/'inventory.json.gz').exists(),'Fresh immutable role inventory required'
    lease=read(LEASE);assert reservations.heartbeat(lease)['ok']
    roles=read(DOC/'role-context.json.gz');row=read(PRIOR/'diagnostic.json.gz');coverage=read(PRIOR/'coverage-v2.json.gz')
    gpath=ROOT/next(r['path'] for r in row['evidenceRefs'] if r['path'].endswith('runtime-geometry.json.gz'))
    g=read(gpath)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    ground=np.asarray(g['drawnGroundGeometry'],dtype=float)
    context=[{**f,'groundProjectionCovered':coverage['faces'][i]['groundProjectionCovered']} for i,f in enumerate(row['faces'])]
    binding={'sourceSHA256':row['sourceSHA256'],'rootMatrix':roles['providerOriginalHierarchy']['nodes'][0]['matrix'],
        'positionTriangleStreamSHA256':roles['rawProviderTriangleAttributes']['POSITION']['triangleStreamSHA256'],
        'normalTriangleStreamSHA256':roles['rawProviderTriangleAttributes']['NORMAL']['triangleStreamSHA256'],
        'colourTriangleStreamSHA256':roles['rawProviderTriangleAttributes']['COLOR_0']['triangleStreamSHA256'],
        'decodedWorldTrianglesSHA256':digest(tri.tobytes()),'drawnGroundSHA256':digest(ground.tobytes())}
    main_faces=set(row['affectedComponentContexts'][0]['componentFaces'])
    affected=[f['sourceFace'] for f in context if not f['inClosedBuriedComponent'] and f['minimum']['minimumGapM']<-.5]
    wall_paths=original_open_paths(tri,context,affected,main_faces,expected_binding=binding,current_binding=binding)
    assert wall_paths['allAffectedWallsHaveRoles'] and len(wall_paths['originalOrientationConflicts'])==2
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);ratio=normal[:,1]/np.linalg.norm(normal,axis=1)
    wall_faces={i for i in main_faces if abs(ratio[i])<=.25}
    shaft_faces=set(i for s in roles['closedComponentsFullOriginalInteractions'] for i in s['originalFaces'])
    ordinary=set(range(len(tri)))-wall_faces-shaft_faces
    assert not wall_faces.intersection(shaft_faces)
    assert all(context[i]['groundProjectionCovered'] and context[i]['minimum']['minimumGapM']>=-.5 for i in ordinary)
    # Compute a complete exact-coordinate shared-edge component partition once.
    edges={};adj=[set() for _ in tri]
    for i,face in enumerate(tri):
        for a,b in zip(face,np.roll(face,-1,axis=0)):edges.setdefault(tuple(sorted([tuple(a),tuple(b)])),[]).append(i)
    for ids in edges.values():
        for i in ids:adj[i].update(set(ids)-{i})
    components=[];pending=set(range(len(tri)));face_component={}
    while pending:
        seed=min(pending);members={seed};todo=[seed]
        while todo:
            i=todo.pop()
            for j in adj[i]-members:members.add(j);todo.append(j)
        pending.difference_update(members);cid=len(components)
        for i in members:face_component[i]=cid
        components.append({'componentId':cid,'originalFaces':sorted(members),
            'roleCounts':dict(collections.Counter('open-exterior-wall' if i in wall_faces else
                          'closed-authored-shaft' if i in shaft_faces else 'ordinary-strict-exterior' for i in members))})
    terminals={};interfaces=[]
    for s in roles['closedComponentsFullOriginalInteractions']:
        own=s['originalFaces'];top=tri[own].reshape(-1,3)[np.argmax(tri[own].reshape(-1,3)[:,1])]
        other_ids={face_component[c['otherSourceFace']] for c in s['contacts'] if not c['otherFaceInMainRoofComponent']}
        candidates=[cid for cid in sorted(other_ids) if len(components[cid]['originalFaces'])==224]
        assert len(candidates)==1,'Expected exact single original terminal for authored shaft'
        terminal_id=candidates[0];terminal=components[terminal_id]['originalFaces']
        if terminal_id not in terminals:
            topology=shell_context(tri,[terminal[0]])
            assert topology['componentFaces']==terminal and topology['outwardPositiveVolume']
            proof=shell_self_intersections(tri[terminal].tolist())
            assert proof['selfIntersectionFree'],'Terminal is not a closed embedded original shell'
            terminals[terminal_id]={'componentId':terminal_id,'topology':topology,'exactSelfIntersection':proof}
        point=point_membership(top.tolist(),tri[terminal].tolist())
        allowed_roles=all(c['otherSourceFace'] in main_faces or c['otherSourceFace'] in ordinary for c in s['contacts'])
        intersects_roof=any(c['otherFaceInMainRoofComponent'] and c['otherFaceUpward'] for c in s['contacts'])
        cap_clear=all(context[i]['minimum']['minimumGapM']>=-.5 for i in own if context[i]['upward'])
        interfaces.append({'shaftIndex':s['shellIndex'],'shaftOriginalFaces':own,'terminalComponentId':terminal_id,
            'highestOriginalShaftVertex':top.tolist(),'highestVertexTerminalMembership':point,
            'originalShaftToRoofInterface':intersects_roof,'allInterfacesOwnedWallOrStrictExterior':allowed_roles,
            'allUpwardShaftFacesKeepClearance':cap_clear,'wholeSourceExactInterfacesRef':ref(DOC/'role-context.json.gz')})
        assert reservations.heartbeat(lease)['ok']
        print(json.dumps({'shaft':s['shellIndex'],'terminal':terminal_id,'topInside':point['strictlyInside'],
                         'roofInterface':intersects_roof,'ownedInterfaces':allowed_roles}),flush=True)
    face_roles=[{'sourceFace':i,'componentId':face_component[i],
                 'role':'open-exterior-wall' if i in wall_faces else 'closed-authored-shaft' if i in shaft_faces
                        else 'ordinary-strict-exterior'} for i in range(len(tri))]
    result={'uid':row['uid'],'modelId':roles['modelId'],'sourceSHA256':row['sourceSHA256'],
        'wholeSourceFaces':len(tri),'allOriginalFacesAndComponentsPartitionedExactlyOnce':True,
        'components':components,'faceRoles':face_roles,'roleCounts':dict(collections.Counter(f['role'] for f in face_roles)),
        'sourceAndPhysicalBinding':binding,'originalOpenExteriorPaths':wall_paths,
        'closedShaftInterfaces':interfaces,'originalTerminals':list(terminals.values()),
        'allTerminalHighestVertexMembershipsPass':all(i['highestVertexTerminalMembership']['strictlyInside'] for i in interfaces),
        'allShaftInterfacesPass':all(i['originalShaftToRoofInterface'] and i['allInterfacesOwnedWallOrStrictExterior'] and i['allUpwardShaftFacesKeepClearance'] for i in interfaces),
        'sourceGeometryChanges':0,'closedOpenBodyCertified':False,'installationApproved':False,'publication':False,
        'evidenceRefs':[ref(p) for p in [Path(__file__),DOC/'role-context.json.gz',PRIOR/'diagnostic.json.gz',
            PRIOR/'coverage-v2.json.gz',gpath,HERE/'unchanged_open_exterior_paths_20261009.py',
            HERE/'exact_shell_context_accelerated_20261009.py',HERE/'exact_closed_shell_point_20261009.py']],
        'qualification':'Complete original component and face-role inventory. Original open-body winding conflicts retained, no closed-solid claim. Each closed shaft has whole-source exact interfaces, protected upward surfaces and a highest authored vertex inside its independent closed embedded original terminal. No source, terrain or prior review edits; fresh current physical gates remain required.'}
    assert reservations.owns(lease);save(DOC/'inventory.json.gz',result)


if __name__=='__main__':main()
