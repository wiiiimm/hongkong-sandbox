"""Source-bound narrow vertical column role with complete foreign actor scope."""
import hashlib
import json
import numpy as np
from shapely.geometry import Polygon,box
from unchanged_closed_column_role_20261009 import column_role


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def scoped_column_role(triangles, ground, contexts, column_faces, *, expected_binding,
                       current_binding, expected_role, foreign_scope):
    tri=np.asarray(triangles,float);ids=sorted(column_faces)
    assert expected_role['role']=='original-vertical-column-termination'
    assert expected_role['sourceSHA256']==current_binding['sourceSHA256']
    assert expected_role['columnFaces']==ids
    actual_bounds=[tri[ids].min(axis=(0,1)).tolist(),tri[ids].max(axis=(0,1)).tolist()]
    assert actual_bounds==expected_role['originalBounds'],'Original source role geometry differs'
    assert current_binding['originalColumnRoleSHA256']==canonical_sha(expected_role)
    assert expected_binding==current_binding
    size=np.asarray(actual_bounds[1])-actual_bounds[0]
    # A narrow role discriminator, not a burial-depth allowance. Broad solids
    # cannot receive column credit. Source-specific bounds further fence use.
    elongated=size[1]>=2*max(size[0],size[2]) and max(size[0],size[2])>0
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1)
    ratio=np.divide(normals[:,1],length,out=np.zeros(len(tri)),where=length>0)
    crosses=any(abs(ratio[i])<=.25 and contexts[i]['minimum'] and
                contexts[i]['minimum']['minimumGapM']<0 and contexts[i]['maximumObservedGapM'] is not None and
                contexts[i]['maximumObservedGapM']>0 for i in ids)
    assert foreign_scope and foreign_scope['completeCurrentActorScope'],'Missing complete foreign actor scope proof'
    actors=foreign_scope['actors'];manifest=foreign_scope['expectedActorManifest']
    assert actors and len(actors)==len(manifest)
    assert len({a['uid'] for a in actors})==len(actors)
    actual=[];foreign=[];separation=[]
    column_projection=box(actual_bounds[0][0],actual_bounds[0][2],actual_bounds[1][0],actual_bounds[1][2])
    for actor in actors:
        mode=actor.get('proofType','exact-world-triangles')
        if mode=='exact-world-triangles':
            mesh=np.asarray(actor['worldTriangles'],float)
            assert mesh.ndim==3 and mesh.shape[1:]==(3,3) and len(mesh) and np.isfinite(mesh).all()
            record={'uid':actor['uid'],'worldTrianglesSHA256':hashlib.sha256(mesh.tobytes()).hexdigest(),
                    'currentSourceBinding':actor['currentSourceBinding']}
            foreign.append(mesh)
        elif mode=='current-basic-full-footprint':
            rings=actor['originalCurrentRings'];polygon=Polygon(rings[0],rings[1:])
            assert polygon.is_valid and polygon.area>0 and polygon.disjoint(column_projection), 'Basic footprint intersects column'
            record={'uid':actor['uid'],'proofType':mode,'originalCurrentRingsSHA256':canonical_sha(rings),
                    'currentSourceBinding':actor['currentSourceBinding']}
            separation.append({'uid':actor['uid'],'proofType':mode,'projectionDistanceM':polygon.distance(column_projection)})
        elif mode=='complete-original-native-bounds':
            bounds=np.asarray(actor['originalWholeSourceBounds'],float)
            assert bounds.shape==(2,3) and np.isfinite(bounds).all() and (bounds[1]>=bounds[0]).all()
            # Exact native whole-source bounds, never GIS footprint proxies.
            assert np.any(bounds[0]>actual_bounds[1]) or np.any(bounds[1]<actual_bounds[0]),'Native bounds intersect: full original export required'
            record={'uid':actor['uid'],'proofType':mode,'originalWholeSourceBoundsSHA256':canonical_sha(bounds.tolist()),
                    'currentSourceBinding':actor['currentSourceBinding']}
            separation.append({'uid':actor['uid'],'proofType':mode,'wholeSourceBoundsStrictlyDisjoint':True})
        else:raise AssertionError('Unsupported foreign actor proof mode')
        assert record['currentSourceBinding'],'Missing current actor source binding'
        actual.append(record)
    assert sorted(actual,key=lambda x:x['uid'])==sorted(manifest,key=lambda x:x['uid']),'Omitted/changed foreign actor'
    scope={k:foreign_scope[k] for k in ['expectedActorManifest','currentGroupBoundaryBinding','completeCurrentActorScope']}
    assert scope['currentGroupBoundaryBinding'],'Current source/group boundary missing'
    assert current_binding['currentForeignScopeSHA256']==canonical_sha(scope)
    result=column_role(tri,ground,contexts,ids,expected_binding=expected_binding,current_binding=current_binding,
                       foreign_triangles=np.concatenate(foreign) if foreign else ())
    if not elongated:result['reasons'].append('original-solid-is-not-narrow-vertical-column')
    if not crosses:result['reasons'].append('no-original-ground-crossing-column-side')
    result.update(contract='unchanged-closed-column-termination-v2',verifiedColumnRole=not result['reasons'],
                  sourceSpecificOriginalRole=expected_role,completeCurrentForeignScope=scope,
                  currentForeignActorsChecked=len(actors),verticalColumnHeightToPlanRatio=float(size[1]/max(size[0],size[2])),
                  groundCrossingSideProved=crosses,strictlySeparatedCurrentActors=separation)
    return result
