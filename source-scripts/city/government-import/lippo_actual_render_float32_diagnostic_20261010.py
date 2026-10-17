"""Independently bind actual render attributes and two explicit F32 world streams.

This is a finite coordinate diagnostic, not a universal GPU/camera arithmetic
claim, physical support or permission to modify original mesh data.
"""
import numpy as np
from run import digest
from lippo_three_original_current_inventory_20261010 import EXPECTED
from lippo_current_bound_six_roof_identity_v1_20261010 import literal_measurements

KINDS=('roundedWorldPositionFloat32','explicitFloat32ModelMatrixWorldPosition')

def finite(value,shape=None):
    a=np.asarray(value,dtype='<f8')
    if shape is not None:a=a.reshape(shape)
    assert np.isfinite(a).all(),'Nonfinite actual render stream'
    return a

def reconstruct(export,literal):
    assert export['startAndEndInputHashesVerified'] and export['sourceGeometryChanges']==0
    rows=export['rows'];lr=literal['rows']
    assert len(rows)==len(lr)==3 and {r['uid'] for r in rows}==set(EXPECTED)
    assert len({r['uid'] for r in rows})==len({r['uid'] for r in lr})==3
    by={r['uid']:r for r in lr};streams={k:{} for k in KINDS};bindings=[]
    for r in rows:
        uid=r['uid'];old=by[uid]
        assert r['sourceSHA256']==old['sourceSHA256']==EXPECTED[uid][1]
        assert r['completeFaces']==EXPECTED[uid][2] and r['sourceGeometryChanges']==0
        assert r['actualRenderMeshes']
        vertices=[];indices=[];explicit=[];offset=0
        for mesh in r['actualRenderMeshes']:
            assert mesh['positionAttributeArrayType']=='Float32Array'
            p=finite(mesh['completeOriginalVertexAttribute'],(-1,3))
            assert np.array_equal(p,p.astype('<f4').astype('<f8')),'Non-F32 attribute'
            i=np.asarray(mesh['completeOriginalIndex']);assert np.issubdtype(i.dtype,np.integer)
            assert i.ndim==1 and len(i)%3==0 and i.min()>=0 and i.max()<len(p)
            m=finite(mesh['matrixWorldFloat64'],(4,4)).T
            assert np.array_equal(m[3],[0,0,0,1]),'Non-affine model matrix'
            fm=m.astype('<f4')
            assert np.array_equal(finite(mesh['modelMatrixUniformFloat32'],(4,4)).T,fm)
            # Preserve THREE Vector3.applyMatrix4 operation order independently.
            q=np.empty_like(p);f=np.empty_like(p)
            for j in range(3):
                q[:,j]=m[j,0]*p[:,0]+m[j,1]*p[:,1]+m[j,2]*p[:,2]+m[j,3]
                x=(fm[j,0]*p[:,0].astype('<f4')).astype('<f4')
                x=(x+(fm[j,1]*p[:,1].astype('<f4')).astype('<f4')).astype('<f4')
                x=(x+(fm[j,2]*p[:,2].astype('<f4')).astype('<f4')).astype('<f4')
                f[:,j]=(x+fm[j,3]).astype('<f4')
            assert finite(mesh['completeNormalAttribute']).size==p.size
            assert finite(mesh['completeColorAttribute']).size==p.size
            vertices.append(q);explicit.append(f);indices.extend((i+offset).tolist());offset+=len(p)
        world=np.concatenate(vertices);f32=np.concatenate(explicit)
        assert indices==r['index']==old['index'] and len(indices)==3*r['completeFaces']
        assert np.array_equal(world,finite(r['worldPositionFloat64'],(-1,3)))
        assert np.array_equal(world,finite(old['position'],(-1,3))),'Literal mesh mismatch'
        rounded=world.astype('<f4').astype('<f8')
        assert np.array_equal(rounded,finite(r[KINDS[0]],(-1,3)))
        assert np.array_equal(f32,finite(r[KINDS[1]],(-1,3))),'Independent F32 arithmetic mismatch'
        idx=np.asarray(indices).reshape(-1,3)
        for kind,p in zip(KINDS,(rounded,f32)):
            a=p[idx];streams[kind][uid]=a
            bindings.append(dict(uid=uid,representation=kind,completeFaces=len(a),worldTrianglesSHA256=digest(a.astype('<f8').tobytes()),maximumCoordinateDifferenceFromLiteralM=float(np.abs(p-world).max())))
    return streams,bindings

def verify(export,literal,originals,forms,primary):
    streams,pins=reconstruct(export,literal);checks=[]
    for kind,meshes in streams.items():
        # Reuse the exact complete source/actual finite-contact and ordinary
        # spatial contracts, never a coordinate tolerance or parity shortcut.
        rows=[];bindings={}
        for uid,a in meshes.items():
            rows.append(dict(uid=uid,loaderPassed=True,sourceSHA256=EXPECTED[uid][1],position=a.reshape(-1).tolist(),index=list(range(a.size//3))))
            bindings[uid]=dict(original=dict(completeFaces=len(originals[uid]),worldTrianglesSHA256=digest(originals[uid].astype('<f8').tobytes())),literal=dict(completeFaces=len(a),worldTrianglesSHA256=digest(a.astype('<f8').tobytes())))
        checks.append(dict(representation=kind,completeSpatialAndExactRoleChecks=literal_measurements(originals,forms,primary,dict(rows=rows),bindings)))
    return dict(contract='lippo-complete-actual-render-attributes-explicit-f32-diagnostic-v1',completeWorldBindings=pins,completeRepresentationChecks=checks,sourceGeometryChanges=0,currentIdentityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Actual render Float32 attributes and literal model matrices independently reconstructed. Rounded-world and declared sequential Float32 model-matrix arithmetic separately satisfy complete finite role/spatial checks. GPU camera/model-view/FMA arithmetic and browser appearance are separate; no universal GPU precision guarantee, physical/support/collision or installation credit.')
