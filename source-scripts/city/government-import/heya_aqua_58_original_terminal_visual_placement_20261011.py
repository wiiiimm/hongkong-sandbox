"""Named original terminal facade placement; no engineering or root credit.

Same source-authored visual interpretation used for King Cheung's named
terminal roof/facade pieces. No distance band, contact threshold or physical
gate is changed. Provider-original proposal only; actual current worlds need
their own complete source/pose/finite/foreign/runtime bindings.
"""
import hashlib,json
import numpy as np
UID='landsd/184286:0';PODIUM='landsd/184285:0'
SOURCE='f9c73a61b679ebc18df1741c01c7e98463a4269928a38b882e3a41d268646155'
WORLD='64083b7a54fc708319aa92abb8948beacf689c0b8928dd431ef470d50540c18d'
NAMED=[93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,140,141,142,143,144,145,146,147,148,149,150,189,190,191,194,273,274,275,279,280,281,285,286,287,291,292,293,297,298,299,303,304,305,309,310,311,315,316,317,321,322,323]
IMAGES=[('complete-58-terminal-source-facade-orthographic-3000x1800.png','d5002de94f81b1ddf01ef7ec7e7de5290704890e3d5b1ec4dc4dadc785fc8c93'),('complete-repeat-A-122-facet-source-context-3000x1800.png','a675b5c87f2077c31a7fa03a78ae33327c89ae65c90203c900ae96ec903c0ca4'),('complete-repeat-B-16-facet-source-context-3000x1800.png','b23d878c2e860fcc2af60ba5793b47c1e1993881ed5d6e59f3f78a4ce3f2dfb4')]
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(*,census,world,context,image_refs):
    assert canonical(census)=='9fbf8cbde9bd993600c6440c8b2aadea7b5c02ce1ad766d90861c485ac5b31eb'
    assert canonical(context)=='abe32a26cb40876cb7a6b2875847493c6c5616e534c3d208a801be2b846860b0'
    assert census['uids']==[UID,PODIUM] and not census['currentAcceptance'] and not census['installationApproved']
    assert census['sourceGeometryChanges']==census['terrainGeometryChanges']==census['sourceFacesOmitted']==0
    assert census['groundRootsAccepted'] is census['visualRolesAccepted'] is census['structuralSupportAccepted'] is False
    source=census['actors'][UID]['sourceTuple']
    assert source==dict(modelId='B339682218601063C0',csuid='3396822186T20151008',faces=17910,sourceSHA256=SOURCE,worldSHA256=WORLD)
    w=np.asarray(world,dtype='<f8');assert w.shape==(17910,3,3)and np.isfinite(w).all()and hashlib.sha256(w.tobytes()).hexdigest()==WORLD
    topology=census['actors'][UID]['completeOriginalTopology'];parts=topology['sharedEdgeConnectedComponents']
    assert len(parts)==574 and topology['exactNonrenderingOriginalFaces']==[] and topology['completeOriginalFaceIds']==list(range(17910))
    families=[f for f in census['completePositiveRealFacetInterfaceFamilies']if any(n[0]==UID for n in f)and not any(n[0]==PODIUM for n in f)]
    assert sorted(n[1]for f in families for n in f if n[0]==UID)==NAMED
    ids=sorted(i for k in NAMED for i in parts[k]);assert len(ids)==1312 and len(set(ids))==1312
    assert context['uids']==[UID,PODIUM] and context['complete58TerminalFaceIds']==ids
    assert context['sourceGeometryChanges']==0 and context['currentAcceptance'] is context['visualRolesAccepted'] is context['groundRootsAccepted'] is False
    assert image_refs==IMAGES==[(r['filename'],r['sha256'])for r in context['images']]
    assert context['images'][0]['completeHighlightedOriginalFaceIds']==ids
    raw=census['rawTwoResidualRimFailuresRetained'];assert raw['uid']==UID and raw['supportUid']==PODIUM and raw['unresolved']==2 and raw['unchangedInterfacePassed']is False
    assert len(census['residualSourceIncidences'])==2
    for r in census['residualSourceIncidences']:
        assert r['unalteredRawWitness']in raw['samples'] and r['completeSourceComponentIds']==[4] and not r['pointSupportCredit']
    records=[]
    for k in NAMED:
        boundary=census['actors'][UID]['completeBodyBoundaryCensus'][k]
        assert boundary['completeOriginalFaceIds']==parts[k] and boundary['visualRoleAccepted'] is boundary['structuralRootOrBridgeCredit'] is False
        records.append(dict(originalComponent=k,completeOriginalFaceIds=parts[k],
            completeOriginalGeometry=w[parts[k]].tolist(),completeOriginalGeometrySHA256=hashlib.sha256(w[parts[k]].tobytes()).hexdigest(),
            completeOriginalBoundaryRecordSHA256=canonical(boundary),
            namedSourceVisualRole='original-repeated-upper-facade-surface-detail',
            nonstructuralVisualInterpretationProposed=True,mountCertified=False,functionCertified=False,
            loadBearingClaim=False,structuralRootCredit=False,structuralBridgeCredit=False))
    return dict(uids=[UID],sourceSHA256=SOURCE,completeOriginalWorldSHA256=WORLD,
        completeNamedTerminalComponents=NAMED,completeNamedTerminalFaces=ids,complete58PlacementRecords=records,
        rawTwoRimFailuresPreservedSHA256=canonical(raw),completeSourceCensusSHA256=canonical(census),
        completeSourceImages=image_refs,providerOriginalInterpretationOnly=True,
        structuralRootCredit=False,structuralBridgeCredit=False,loadBearingClaim=False,
        currentAcceptance=False,physicalAccepted=False,installationApproved=False)
