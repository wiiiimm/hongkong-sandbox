"""Bind bounded original-wall/support/seam interpretations; no installation approval.

Every raw failure remains. Guarded whole-source integration and live readback
are separate requirements. Original geometry/pose and parent flags stay intact.
"""
from pathlib import Path
import sys,uuid
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-parkview256319-source-context-review-v2-20261104'
PREFIX='government-xl-parkview256319'
UID='landsd/256319:0';PARENT='landsd/254491:0';PEER='landsd/256116:0'
SOURCE_SHA='b57eab82a53c67a40eb0f94e64215ca5acbd8f4808fb90610c15425aa21c4193'

def main():
    out=BASE/BATCH;lp=HERE/'local'/(BATCH+'-control')/'reservation.json'
    resources=sorted(['building:'+u for u in [UID,PARENT,PEER]]+['terrain:city/data/terrain.json','immutable-source-proof:'+BATCH])
    if '--owned'not in sys.argv:
        assert not out.exists()and not lp.parent.exists();c=reservations.claim('parkview-bounded-context-review-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        q=BASE/batch/name;assert digest(q.read_bytes())==pins[batch][str(q.relative_to(ROOT))];refs.append(q);return read(q)
    current=PREFIX+'-after-tung-cheong-v1-20261104'
    ident=take(current+'-identity','summary.json');assert ident['rows']==[dict(uid=UID,sourceSHA256=SOURCE_SHA,passed=True,reasons=[])]
    complete_identity=take(current+'-identity','256319:0/identity.json');assert complete_identity['freshCurrentIdentity']['exactObjectAndCSUID']and complete_identity['freshCurrentIdentity']['unrelatedIntersectingForms']==0
    assert complete_identity['exactWholeCellCoverage']['covered']
    support=take(PREFIX+'-installed-support-sequence-v1-20261104-strict-support','summary.json');assert support['supportedUid']==UID and support['installedSupportUid']==PARENT
    clearance=take(PREFIX+'-compound-context-v1-20261104-clearance','summary.json');buried=take(PREFIX+'-compound-context-v1-20261104-buried','summary.json')
    for row in clearance['rows']:assert row['completeSourceFaces']==11351 and row['compoundCapPathsPassed']and row['allAffectedWallLike']and row['negativeNonWallFaces']==[]and len(row['exactAffectedFaces'])==42
    for row in buried['rows']:assert len(row['buriedFaces'])==5 and not row['uncoveredFaceIndices']and all(not f['upward']and f['normal'][1]==0 for f in row['buriedFaces'])
    for row in support['rows']:
        assert row['support']['strictContacts']==82 and row['unresolved']==row['finitePaths']==40 and not row['support']['passed']
        diagnostic=take(PREFIX+'-installed-support-sequence-v1-20261104-strict-support',row['mode']+'/diagnostic.json.gz');assert len(diagnostic['paths'])==40
        for item in diagnostic['paths']:
            path=item['verifiedPath'];assert path['withinEndpointHeight']and path['maximumResidualM']<=.001 and path['maximumPathHeightM']<=path['endpointHeightCeilingM']+1e-9 and path['contact']['dimension']>0
    seam=take(PREFIX+'-native-seam-context-v2-20261104','summary.json');assert seam['currentCompleteArraysAndEveryRawRoleVerified']and seam['contactCalculationsRepeated']==0 and len(seam['rows'])==8
    for row in seam['rows']:
        assert row['sourceSHA256']==SOURCE_SHA
        if row['nativeUid']==PEER:assert row['contactCount']==91 and row['roles']=={'shared-plane-area-contact':9,'source-edge-surface-contact':16,'surface-point-contact':18,'transverse-surface-crossing':48}and row['contactBounds'][1][2]-row['contactBounds'][0][2]<.008
        else:assert row['nativeUid']==PARENT and row['contactCount']==144
    near=take(PREFIX+'-current-neighbours-v1-20261104-basic','summary.json');assert near['foreignPairs']==0 and near['rows']==[]and{r['nativeUid']for r in near['overlappingNativeRawContexts']}=={PARENT,PEER}
    audit=take('government-xl-parkview-podium-flag-audit-v5-20261104','audit.json');assert audit['uid']==PARENT and audit['reviewState']=='installed-verified'and audit['sameCatalogueAsInstalledAcceptance']and audit['noLaterHoldOrRejection']and audit['legacyCatalogueFlagFalse']and not audit['catalogueChanged']
    browser=PREFIX+'-supported-private-preview-v1-20261104'
    for width in [1280,390]:
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
    observations=BASE/(PREFIX+'-private-inspection-sheets-v1-20261104')/'ROOT-OBSERVATIONS.json';observed=read(observations);assert observed['actuallyInspected']and observed['sourceExports']==12 and len(observed['exports'])==12;refs.append(observations)
    for item in observed['exports']+observed['sheets']:
        q=ROOT/item['path'];assert digest(q.read_bytes())==item['sha256'];refs.append(q)
    interface=BASE/(PREFIX+'-native-seam-context-v2-20261104')/'ROOT-INTERFACE-OBSERVATIONS.json';obs=read(interface);assert obs['actuallyInspected']and len(obs['images'])==2;refs.append(interface)
    for item in obs['images']:
        q=ROOT/item['path'];assert digest(q.read_bytes())==item['sha256'];refs.append(q)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==support['currentManifestSHA256']==seam['currentManifestSHA256'];refs.append(manifest)
    result=dict(uids=[UID],sourceSHA256=SOURCE_SHA,currentManifestSHA256=mh,sourceSpecificSupportInterpretationAccepted=True,sourceSpecificBuriedWallInterpretationAccepted=True,sourceSpecificAdjacentSeamInterpretationAccepted=True,rawCanonicalFailuresPreserved=True,negativeParentFlagPreserved=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,executorModelAndEffort='unverified',geometryEffort=dict(method='scripted',ai_model=None,reasoning_effort='not-applicable'),wholeSourceAcceptance=False,physicalAcceptance=False,installationApproved=False,publication=False,basis=['82strict direct contacts plus all40finite original-surface attachment paths account for the raw rim warnings in every world; no path rises beyond its own actual contact endpoint.','All42negative facets are vertical/near-vertical source walls with existing exact clear-cap paths; all5buried facets are vertical and no upward floor is buried. This is a source-ground interface interpretation, not invented engineering support.','The entire neighbouring native contact locus occupies a sub8mm rear seam. Nine area contacts are exactly shared-plane contacts; every transverse, edge and point contact remains. Complete identity places these two towers under the same original parent/reference and finds no unrelated-form excess. This is a bounded source-authored adjacent seam, not blanket permission for other collisions.','Current exact podium installed approval history is independently reconciled, while its false catalogue flag is explicitly preserved. A case-specific guarded integration contract must consume this evidence; generic checks remain unchanged.','All12actual browser exports and both diagrams were inspected; dark night surfaces and occlusion limitations remain. No asbuilt/full-facet/physical-phone performance certification.'],remainingGates=['Complete guarded source-specific installed-parent and adjacent-seam contract; no broad flag bypass','Whole-source runtime/identity/neighbour qualification and canonical publisher dry run','Distinct fenced installation, actual live inspection, independent full521/all-oldassets/global-support readback and immediate commit/push'])
    assert reservations.owns(lease)and digest(manifest.read_bytes())==mh;save(out/'ROOT-SOURCE-CONTEXT-REVIEW.json',result)
    module('parkview_bounded_source_context_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-current-original-wall-support-seam-context-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
