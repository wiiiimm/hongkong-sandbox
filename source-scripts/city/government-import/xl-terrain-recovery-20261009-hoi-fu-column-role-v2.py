"""Replayable current source-bound column role; no installation/publication."""
import json
import uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations,jobs,Jsonb,dict_row
from unchanged_closed_column_role_20261009 import context_digest
from unchanged_closed_column_role_v2_20261009 import scoped_column_role,canonical_sha
from xl_source_stream_binding_20261009 import source_stream_binding

BATCH='xl-terrain-recovery-20261009-hoi-fu-column-role-v2'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-hoi-fu-yu-complete-original-physical-v2-20261009'
GEOMETRY=HERE/'local/government-xl-hoi-fu-yu-complete-original-physical-v2-20261009/runtime-geometry.json.gz'
CONTEXT=ROOT/'docs/astra-city/government-import/government-xl-hoi-fu-current-column-context-v2-20261009/diagnostic.json.gz'

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}

def recheck():
    """Pure read-only deterministic replay; caller owns publication reservation.

    Frozen continuous contexts are usable only when every referenced current
    source, decoded world mesh, drawn ground, neighbour and catalogue hash still
    matches. This returns role proof, never approval for independent physical
    checks or publication. It acquires no lease and writes no files.
    """
    d=read(CONTEXT);geometry=read(GEOMETRY)
    rows=read(PHYSICAL/'selection.json.gz')['rows']
    row=next(r for r in rows if r['uid']==d['uid'])
    assert d['uid']=='landsd/177604:0'
    assert d['sourceSHA256']=='bf710f3c82832b8b82b85571bbda7904416ea8743a081e6aa3de321915a21122'
    g=next(r for r in geometry['rows'] if r['uid']==d['uid'])
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes()
    assert digest(raw)==d['sourceSHA256']==g['sourceSHA256']
    neighbour_path=PHYSICAL/'neighbour-inputs.json.gz';native_path=PHYSICAL/'native-neighbour-checks.json'
    neighbours=read(neighbour_path);native=read(native_path)
    assert set(neighbours['candidateIds'])=={'landsd/177604:0','landsd/177605:0'}
    assert len(neighbours['rows'])==59 and len({r['building']['uid'] for r in neighbours['rows']})==59
    assert [r['uid'] for r in native['rows']]==['landsd/239397:0'] and native['rows'][0]['passed']
    refs=d['evidenceRefs']+[
        {'path':p,'sha256':sha} for p,sha in native['inputHashes'].items()]+[
        {'path':p,'sha256':sha} for p,sha in geometry['inputHashes'].items()]+[
        {'path':p,'sha256':sha} for p,sha in neighbours['inputHashes'].items()]
    for item in refs:assert ref(ROOT/item['path'])==item,'Current receipt binding changed: '+item['path']
    current_forms={}
    for tile,sha in neighbours['inputHashes'].items():
        current_forms.update({b['uid']:b for b in read(ROOT/tile)['buildings']})
    for nr in neighbours['rows']:assert current_forms[nr['building']['uid']]==nr['building']
    tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
    ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)
    binding=source_stream_binding(raw)
    binding.update(decodedWorldTrianglesSHA256=digest(tri.tobytes()),decodedGroundTrianglesSHA256=digest(ground.tobytes()),
                   continuousFaceContextSHA256=context_digest(d['faces']))
    ids=d['column']['componentFaces']
    role={'uid':d['uid'],'role':'original-vertical-column-termination','sourceSHA256':d['sourceSHA256'],
          'columnFaces':ids,'originalBounds':d['column']['bounds'],
          'positiveOriginalRoleEvidence':{'closedOutwardEmbeddedFaces':24,'clearOriginalUpwardCapFaces':[5500,5501],
             'originalClearUndersideAttachmentFace':5418,'originalPoseAndAttributesUnchanged':True}}
    actors=[];manifest=[];extra=[asset]
    for nr in neighbours['rows']:
        form=nr['building'];uid=form['uid']
        if uid=='landsd/177604:0':continue  # Whole owned source checked by column kernel.
        if uid=='landsd/177605:0':
            paired=next(r for r in geometry['rows'] if r['uid']==uid)
            ptr=np.asarray(paired['position'],float).reshape(-1,3)[np.asarray(paired['index']).reshape(-1,3)]
            assert len(ptr)==8775
            paired_row=next(r for r in rows if r['uid']==uid);paired_asset=ROOT/paired_row['candidate']['path']
            assert digest(paired_asset.read_bytes())==paired['sourceSHA256'];extra.append(paired_asset)
            source={'runtimeGeometry':ref(GEOMETRY),'originalSourceAsset':ref(paired_asset),'currentFormSHA256':canonical_sha(form)}
            actor={'uid':uid,'worldTriangles':ptr.tolist(),'currentSourceBinding':source}
            record={'uid':uid,'worldTrianglesSHA256':digest(ptr.tobytes()),'currentSourceBinding':source}
        elif nr['existingNative']:
            assert uid=='landsd/239397:0'
            matches=[(ROOT/'3d-viewer'/url,b) for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']
                for b in read(ROOT/'3d-viewer'/url)['models'] if b['uid']==uid]
            assert len(matches)==1;catalogue,entry=matches[0];native_asset=catalogue.parent/entry['asset']
            assert digest(native_asset.read_bytes())==entry['sha256'] and entry['triangles']==10991
            extra.extend([catalogue,native_asset]);source={'currentNativeCatalogue':ref(catalogue),
                'originalSourceAsset':ref(native_asset),'wholeNativeCheck':ref(native_path),'currentFormSHA256':canonical_sha(form)}
            actor={'uid':uid,'proofType':'complete-original-native-bounds','originalWholeSourceBounds':entry['worldBounds'],'currentSourceBinding':source}
            record={'uid':uid,'proofType':actor['proofType'],'originalWholeSourceBoundsSHA256':canonical_sha(entry['worldBounds']),'currentSourceBinding':source}
        else:
            assert not form.get('modelGeometry'),'Embedded source requires actual geometry scope'
            source={'currentTileHashes':neighbours['inputHashes'],'currentFormSHA256':canonical_sha(form),'completeNeighbourInputs':ref(neighbour_path)}
            actor={'uid':uid,'proofType':'current-basic-full-footprint','originalCurrentRings':form['rings'],'currentSourceBinding':source}
            record={'uid':uid,'proofType':actor['proofType'],'originalCurrentRingsSHA256':canonical_sha(form['rings']),'currentSourceBinding':source}
        actors.append(actor);manifest.append(record)
    assert len(actors)==58
    boundary={'sourceSelection':ref(PHYSICAL/'selection.json.gz'),'completeCurrentNeighbourInputs':ref(neighbour_path),
        'wholeNativeCheck':ref(native_path),'manifest':ref(ROOT/'3d-viewer/city/data/manifest.json'),
        'ownedWholeSourceExclusion':{'uid':d['uid'],'sourceSHA256':d['sourceSHA256']},
        'pairUids':neighbours['candidateIds'],'originalSourceGroupGeometries':ref(GEOMETRY)}
    scope={'completeCurrentActorScope':True,'expectedActorManifest':sorted(manifest,key=lambda r:r['uid']),
           'actors':actors,'currentGroupBoundaryBinding':boundary}
    binding.update(originalColumnRoleSHA256=canonical_sha(role),currentForeignScopeSHA256=canonical_sha({k:scope[k] for k in
        ['expectedActorManifest','currentGroupBoundaryBinding','completeCurrentActorScope']}))
    typed=scoped_column_role(tri,ground,d['faces'],ids,expected_binding=binding,current_binding=binding,
                             expected_role=role,foreign_scope=scope)
    assert typed['verifiedColumnRole'],typed['reasons']
    assert typed['allOriginalInterfaces']==d['originalComponentInterfaces']
    paths=[CONTEXT,GEOMETRY,neighbour_path,native_path,PHYSICAL/'selection.json.gz',Path(__file__),
        HERE/'unchanged_closed_column_role_20261009.py',HERE/'test_unchanged_closed_column_role_20261009.py',
        HERE/'unchanged_closed_column_role_v2_20261009.py',HERE/'test_unchanged_closed_column_role_v2_20261009.py',
        HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_shell_context_accelerated_20261009.py',
        HERE/'original_shell_diagnostic_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',*extra]
    refs.extend(ref(p) for p in paths)
    refs=sorted({r['path']:r for r in refs}.values(),key=lambda r:r['path'])
    typed.update(uid=d['uid'],sourceSHA256=d['sourceSHA256'],evidenceRefs=refs,
                 currentNeighbourFormsAccounted=59,currentForeignActorsChecked=58,
                 scopeBreakdown={'ordinaryBasicFullFootprints':56,'pairedOriginalSourceMeshes':1,'installedWholeNativeBounds':1,'ownedWholeSourceExclusions':1},
                 requiresAI=False,requiresHumanDecision=False,sourceEvidenceInterpretationUsedAI=True,modelGeometryAI=False)
    return typed


def main():
    assert not DOC.exists()
    claim=reservations.claim('xl-terrain-recovery-hoi-fu-column-v2-'+str(uuid.uuid4()),
        ['building:landsd/177604:0','building:landsd/177605:0'],batch=BATCH,ttl=1800)
    assert claim['ok'],claim;lease=claim['reservation']
    try:
        proof=recheck();save(DOC/'typed-role.json.gz',proof)
        stage='current-original-closed-column-role-v2'
        payload={'uid':proof['uid'],'sourceSHA256':proof['sourceSHA256'],'evidenceRefs':proof['evidenceRefs']+[ref(DOC/'typed-role.json.gz')]}
        jid=jobs.enqueue(BATCH,stage,payload);job=jobs.claim(BATCH,lease['owner'],[stage],lease_seconds=1800)
        assert job and job['id']==jid
        result={**payload,'jobId':jid,'batch':BATCH,'stage':stage,'verifiedColumnRole':True,
            'contract':proof['contract'],'currentNeighbourFormsAccounted':59,'currentForeignActorsChecked':58,
            'rawStrictBurialFaceFailures':proof['rawStrictBurialFaceFailures'],'sourceGeometryChanges':0,
            'newlyInstalled':0,'publication':False,'installationApproved':False,'requiresAI':False,'requiresHumanDecision':False,
            'nextStep':'Replay source-bound typed role under atomic pair publication lease alongside independent physical/support/browser checks.'}
        with connect() as c:
            c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));assert reservations._current(c,lease)
            for item in payload['evidenceRefs']:assert ref(ROOT/item['path'])==item
            assert c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jid,job['owner'],job['token'])).rowcount==1
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jid,)).fetchone()==('complete',result)
        save(DOC/'result.json',result);save(DOC/'neon-sync.json',{'jobId':jid,'resultVerified':True})
        print(json.dumps({'jobId':jid,'verifiedColumnRole':True,'formsAccounted':59,'foreignActorsChecked':58,'newlyInstalled':0}),flush=True)
    finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
