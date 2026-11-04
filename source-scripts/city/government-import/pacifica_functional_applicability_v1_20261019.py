"""Exact original Pacifica applicability; never rewrites raw numeric failures."""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-pacifica-functional-applicability-v1-20261019'
DOC = BASE / BATCH
POD, T1, T2, T3, T5 = ['landsd/'+k+':0' for k in ['283036','77826','79250','75351','77278']]
UIDS = {POD,T1,T2,T3,T5}
MODES = {'original','literal','explicitLeftF32','explicitBalancedF32'}
FACES = {T1:[7774,7775,7787,7788,7789,8356,8357,8358,8364,8365,8366,8367,8368,8460,8582,8970,8974,8975,8976,9081,9084,9085,9255,9256,9257,9261,9291,9292,9293,9297,9354,9355,9359],T3:[6680,6681,6682,8442]}
def folder(name):
    return BASE / ('government-xl-pacifica-'+name+'-20261019')

def qualify(physical, binding, facade, overlap, foundations):
    assert physical['completeLoaderChecksPassed'] and physical['completeNeighbourChecksPassed']
    assert not any(r['remainingReasons'] for r in physical['neighbours'])
    rows={r['uid']:r for r in physical['rows']}
    assert set(rows)==UIDS and len(physical['rows'])==5
    tuples={(u,m)for u in UIDS for m in MODES}
    assert len(binding['bindings'])==20 and {(r['uid'],r['mode'])for r in binding['bindings']}==tuples
    assert len(foundations)==20 and {(r['uid'],r['mode'])for r in foundations}==tuples
    assert len(binding['descriptors'])==8
    assert {(r['uid'],r['mode'])for r in binding['descriptors']}=={(u,m)for u in FACES for m in MODES}
    decisions={r['uid']:r for r in facade['rows']}
    assert set(decisions)==set(FACES)
    for uid,r in rows.items():
        assert r['identityAccepted']
        assert r['remainingPolicyReasons']==(['ground-contact-unresolved'] if uid in FACES else [])
        assert r['remainingDiagnosticReasons']==(['sampled-ground-gap-below-model-bottom'] if uid in FACES else [])
        assert set(r['failedFoundationModes'])==(MODES if uid==T3 else set())
        if uid in FACES:
            d=decisions[uid]
            assert d['reviewer']=='Codex ROOT' and d['sourceFunctionalInterpretationAccepted']
            assert d['sourceFaceIds']==FACES[uid] and d['sourceSHA256']==r['sourceSHA256']
            assert d['modelGeometryChanges']==0 and d['aiGeometryModelling'] is False
            assert d['physicalAccepted'] is False and d['installationApproved'] is False
            s=r['rawStrictSupport'];assert s==d['rawStrictInterfaceVerbatim']
            assert s['passed'] is False and s['wallIntersections']==0
            assert (s['samples'],s['strictContacts'],len(s['unresolved']))==((23,0,23)if uid==T1 else(147,140,7))
            assert d['supportSHA256']==rows[POD]['sourceSHA256']
        elif uid!=POD:
            s=r['rawStrictSupport'];assert s['passed'] and s['samples']==s['strictContacts'] and not s['unresolved'] and s['wallIntersections']==0
    assert overlap['uid']==T3 and overlap['reviewer']=='Codex ROOT'
    assert overlap['sourceFaceIds']==[3028,3029] and overlap['sourceFunctionalInterpretationAccepted']
    assert overlap['strictFoundationAccepted'] is False and overlap['rawNumericalFailuresRemainFailed']
    assert overlap['sourceGeometryChanges']==overlap['sourcePoseChanges']==0 and overlap['aiGeometryModelling'] is False
    assert len(overlap['exactFourModeEvidence'])==4
    for b in binding['bindings']:
        uid,mode=b['uid'],b['mode']
        f=next(r for r in foundations if (r['uid'],r['mode'])==(uid,mode))
        assert b['sourceSHA256']==f['sourceSHA256']==rows[uid]['sourceSHA256']
        assert b['wholeWorldSHA256']==f['wholeWorldSHA256']
        assert f['foundation']['triangles']==f['foundation']['completeTerrainTriangles']==b['completeFaces']
        if uid==T3:
            e=next(r for r in overlap['exactFourModeEvidence']if r['binding']['mode']==mode)
            assert e['binding']==b and e['rawFoundation']==f
            assert [r['faceId']for r in f['buriedFaces']]==[3028,3029]
            assert e['exactAttribution']['terrainOnlyFoundation']['fullyBuriedTriangles']==0
            assert e['exactAttribution']['terrainOnlyFoundation']['completeTerrainTriangles']==b['completeFaces']
        else:
            assert f['strictFoundationAccepted'] is True
            assert f['foundation']['fullyBuriedAreaFraction']==0 and f['foundation']['fullyBuriedUpwardTriangles']==0
        if uid in FACES:
            d=next(r for r in binding['descriptors']if (r['uid'],r['mode'])==(uid,mode))
            assert d['wholeWorldSHA256']==b['wholeWorldSHA256']
            assert [r['originalFaceID']for r in d['faces']]==FACES[uid]
            assert [r['originalFaceID']for r in d['additionalBuriedFaceDescriptors']]==([3028,3029]if uid==T3 else[])
    return dict(uids=sorted(UIDS),sourceScopedApplicabilityAccepted=True,
        qualification='Exact original facade/trim interpretation only. All raw contact and compound-foundation failures remain failed; no independent support for the failed samples is asserted. No generic numeric threshold or model geometry changed.',
        rawPhysicalReconciliation=physical,sourceBindings=binding['bindings'],
        remainingPhysicalReasons=[],strictInterfacePassed=False,strictAllFoundationsPassed=False,
        rawNumericalFailuresRemainFailed=True,sourceGeometryChanges=0,sourcePoseChanges=0,
        aiGeometryModelling=False,publicationApproved=False,installationApproved=False,
        stagedAndLiveBrowserStillRequired=True)

def inputs():
    return [read(folder('physical-reconciliation-v1')/'physical-reconciliation.json'),
        read(folder('wall-binding-v1')/'exact-source-face-bindings.json.gz'),
        read(folder('source-interpretation-v1')/'ROOT-SOURCE-INTERPRETATION.json'),
        read(folder('tower3-overlap-review-v1')/'ROOT-SOURCE-INTERPRETATION.json'),
        [read(folder('four-mode-foundations-v1')/(u.split('/')[1]+'-'+m+'.json'))for u in sorted(UIDS)for m in sorted(MODES)]]

def main():
    assert not DOC.exists()
    pins,refs={},[Path(__file__)]
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        for name in ['physical-reconciliation-v1','wall-binding-v1','source-interpretation-v1','tower3-overlap-review-v1','four-mode-foundations-v1']:
            d=folder(name);receipt=read(d/'result.json')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
            refs.append(d/'result.json')
            for e in receipt['evidenceRefs']:
                assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
    result=qualify(*inputs());save(DOC/'qualification.json',result)
    for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
    module('pacifica_functional_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-five-original-functional-applicability',list(dict.fromkeys(refs)),dict(uids=sorted(UIDS),sourceScopedApplicabilityAccepted=True,strictInterfacePassed=False,strictAllFoundationsPassed=False,installationApproved=False))

if __name__=='__main__':main()
