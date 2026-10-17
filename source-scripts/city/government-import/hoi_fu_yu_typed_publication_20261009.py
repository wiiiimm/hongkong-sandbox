"""Replay original pair roles without editing sources or discarding raw failures."""
import importlib.util
import json
import numpy as np
from run import ROOT, HERE, read, digest, connect, jobs
from original_component_support_20261009 import verify

PODIUM='landsd/177604:0'
TOWER='landsd/177605:0'
SHAS={PODIUM:'bf710f3c82832b8b82b85571bbda7904416ea8743a081e6aa3de321915a21122',
      TOWER:'f328bad9be002308e9fd1b1108feb510ceb56a92a7518e9c5804a5ddcc2684b2'}

def ref(path):
    return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}

def pinned_receipt(doc):
    result=read(doc/'result.json')
    assert read(doc/'neon-sync.json')=={'jobId':result['jobId'],'resultVerified':True}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    for evidence in result['evidenceRefs']:
        assert ref(ROOT/evidence['path'])==evidence
    return result

def recheck_roles(source, fresh_interfaces):
    assert source.name=='government-xl-hoi-fu-yu-complete-original-physical-v2-20261009'
    parent=ROOT/'docs/astra-city/government-import'
    column_doc=parent/'xl-terrain-recovery-20261009-hoi-fu-column-role-v2'
    support_doc=parent/'government-xl-hoi-yu-attached-support-proof-20261009'
    pinned_receipt(column_doc);pinned_receipt(support_doc)
    runner=HERE/'xl-terrain-recovery-20261009-hoi-fu-column-role-v2.py'
    spec=importlib.util.spec_from_file_location('current_pair_column_role',runner)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    # Match persisted JSON representation (shell vertex-map integer keys become
    # strings on storage), retaining every value and exact receipt binding.
    column=json.loads(jobs.encode(module.recheck()))
    assert column==read(column_doc/'typed-role.json.gz')
    old=read(support_doc/'proof.json');interfaces=read(fresh_interfaces)
    for path,sha in interfaces['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    historical=read(parent/'government-xl-hoi-yu-component-interfaces-20261009/diagnostic.json.gz')
    assert interfaces['rows']==historical['rows'], 'Original component interfaces changed'
    census=read(parent/'government-xl-hoi-yu-source-components-20261009/components.json.gz')
    geometry_path=HERE/'local'/source.name/'runtime-geometry.json.gz'
    geometry=read(geometry_path)
    for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    g=next(r for r in geometry['rows'] if r['uid']==TOWER)
    assert g['sourceSHA256']==SHAS[TOWER]==old['sourceSHA256']
    tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    # Source-decoded exact contacts are replayed over the very geometry used by
    # current physical checks, not a favourable subset of a historical source.
    witnesses=[{k:r[k] for k in ['component','anchorComponent','sourceFace','anchorFace']}
               for r in old['verifiedAttachments']]
    support=verify(tri,[c['originalSourceFaces'] for c in census['components']],
                   [r['interface'] for r in interfaces['rows']],witnesses)
    for key in support:
        if key!='verifiedAttachments':
            assert support[key]==old[key], 'Current complete support differs: '+key
    # Exact contact is freshly proved on the renderer's complete original mesh.
    # NumPy and Three.js evaluate the unchanged root transform in different
    # orders (7.1e-15m diagnostic delta). Rational intersection coordinates can
    # consequently differ. Require identical original face/component ownership
    # and positive-length contact anew, without rounding or distance tolerances.
    assert [{k:r[k] for k in witnesses[0]} for r in support['verifiedAttachments']]==witnesses
    support.update(uid=TOWER,supportUid=PODIUM,sourceSHA256=SHAS[TOWER],supportSHA256=SHAS[PODIUM])
    return {'column':column,'support':support,'physicalSource':ref(source/'result.json'),
            'freshInterfaces':ref(fresh_interfaces),'runtimeGeometry':ref(geometry_path),
            'columnReceipt':ref(column_doc/'result.json'),'supportReceipt':ref(support_doc/'result.json'),
            'originalGeometryChanges':0,'aiGeometryModelling':False}

def resolve_pair_member(uid,sha,raw,warnings,foundation,roles):
    assert uid in SHAS and sha==SHAS[uid]==foundation['sourceSHA256']
    assert foundation['uid']==uid
    column,support=roles['column'],roles['support']
    assert column['sourceSHA256']==SHAS[PODIUM] and column['uid']==PODIUM
    assert column['contract']=='unchanged-closed-column-termination-v2'
    assert column['verifiedColumnRole'] and not column['reasons']
    assert column['wholeOriginalFaces']==14627 and len(column['originalColumnFaces'])==24
    assert column['currentNeighbourFormsAccounted']==59 and column['currentForeignActorsChecked']==58
    assert column['sourceGeometryChanges']==0 and not column['foreignIntersections']
    assert column['independentPhysicalGatesStillRequired'] and not column['installationApproved']
    assert support['uid']==TOWER and support['supportUid']==PODIUM
    assert support['sourceSHA256']==SHAS[TOWER] and support['supportSHA256']==SHAS[PODIUM]
    assert support['supportInterfaceAccepted'] and not support['reasons']
    assert support['completeFaceAccounting'] and support['sourceFaces']==8775
    assert support['componentCount']==32 and support['anchorComponents']==[2,3]
    assert len({r['component'] for r in support['verifiedAttachments']})==30
    assert support['geometryChanges']==0 and not support['fullAcceptance']
    f=foundation['foundation'];count=14627 if uid==PODIUM else 8775
    assert f['triangles']==f['completeTerrainTriangles']==count
    assert not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedUpwardAreaM2']==0
    if uid==PODIUM:
        assert raw==['terrain-intersects-source-over-0.5m'] and warnings==[]
        assert not foundation['strictFoundationAccepted']
        assert f['fullyBuriedTriangles']==2 and len(f['components'])==1
        assert f['components'][0]['triangles']==2 and f['components'][0]['upwardTriangles']==0
        assert f['fullyBuriedAreaFraction']==6.985671484870568e-05
        assert set(column['rawStrictBurialFaceFailures'])<=set(column['originalColumnFaces'])
    else:
        assert raw==['ground-contact-unresolved'] and warnings==['sampled-ground-gap-below-model-bottom']
        assert foundation['strictFoundationAccepted'] and f['fullyBuriedTriangles']==0
        assert f['fullyBuriedAreaFraction']==0 and f['minimumGapM']>=-.5
    return {'uid':uid,'sourceSHA256':sha,'passed':True,'remaining':[],
            'rawNumericReasons':raw,'rawDiagnosticReasons':warnings,
            'rawFoundationAccepted':foundation['strictFoundationAccepted'],
            'policy':'hoi-fu-yu-current-unchanged-typed-pair-v1',
            'independentIdentityNeighbourRuntimeBrowserPublicationRequired':True,
            'publication':False,'modelGeometryChanges':0}
