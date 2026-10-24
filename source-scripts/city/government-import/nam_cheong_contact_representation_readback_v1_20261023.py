"""Trace every literal crossing to its exact unchanged original contact pair.

Numeric representation evidence only; original crossings remain unapproved.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BATCH='government-xl-nam-cheong-contact-representation-readback-v1-20261023'
FOUR='government-xl-nam-cheong-pair-four-world-contacts-v1-20261023'
OLD='government-xl-nam-cheong-fu-yun-contact-roles-v1-20261023'
CAP='government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'
ATTR='government-xl-nam-cheong-fu-yun-joint-attributes-v1-20261023'


def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH
    assert not doc.exists()
    refs,pins=[Path(__file__)],{}
    for name in [FOUR,OLD,CAP,ATTR]:
        _,pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    four=take(FOUR,base/FOUR/'summary.json')
    original=take(OLD,base/OLD/'classified-contacts.json.gz')
    literal=take(FOUR,base/FOUR/'literal-classified-contacts.json.gz')
    old={(r['sourceFaceA'],r['sourceFaceB']):r for r in original}
    assert len(old)==len(original)
    attrs=take(ATTR,base/ATTR/'attributes.json.gz');assert attrs['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs['rows']}
    selected=take(CAP,base/CAP/'selection.json.gz');bounds=[]
    worldhashes={}
    for r in selected['rows']:
        a=attrs[r['uid']];asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256']==a['sourceSHA256'];refs.append(asset)
        originaltri=decode_original_world_triangles(raw);literaltri=np.asarray(a['completeLiteralWorldPosition']).reshape(-1,3)[np.asarray(a['completeOriginalIndex']).reshape(-1,3)]
        assert originaltri.shape==literaltri.shape
        exactmax=[max(abs(Fraction(float(x))-Fraction(float(y))) for x,y in zip(originaltri[:,:,axis].ravel(),literaltri[:,:,axis].ravel())) for axis in range(3)]
        assert exactmax[0]==exactmax[2]==0
        bounds.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],completeFaces=len(originaltri),exactMaximumCoordinateDeltaByAxisM=list(map(str,exactmax)),exactMaximumCoordinateDeltaM=str(max(exactmax)),floatingMaximumCoordinateDeltaM=float(max(exactmax)),noGeometryOrPoseEdit=True))
        worldhashes[r['uid']]={'original':digest(originaltri.tobytes()),'literal':digest(literaltri.tobytes())}
    for mode in ['original','literal']:
        row=next(r for r in four['rows'] if r['mode']==mode)
        assert row['sourceWorldSHA256ByUid']=={u:h[mode] for u,h in worldhashes.items()}
    crossings=[]
    for record in literal:
        if record['contactRole']!='transverse-surface-crossing':continue
        pair=(record['sourceFaceA'],record['sourceFaceB']);assert pair in old
        previous=old[pair]
        assert previous['contactRole'] in ['surface-point-contact','source-edge-surface-contact','transverse-surface-crossing']
        crossings.append(dict(sourceFaceA=pair[0],sourceFaceB=pair[1],originalRole=previous['contactRole'],originalDimension=previous['dimension'],originalExactPoints=previous['exactPoints'],literalExactPoints=record['exactPoints'],literalRole=record['contactRole'],rawLiteralCrossingPreserved=True,acceptableContact=False))
    counts=dict(Counter(r['originalRole'] for r in crossings))
    assert len(crossings)==111 and counts=={'surface-point-contact':62,'source-edge-surface-contact':27,'transverse-surface-crossing':22}
    assert {(r['sourceFaceA'],r['sourceFaceB']) for r in original if r['contactRole']=='transverse-surface-crossing'}=={(r['sourceFaceA'],r['sourceFaceB']) for r in crossings if r['originalRole']=='transverse-surface-crossing'}
    save(doc/'literal-crossing-original-pair-trace.json.gz',crossings)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==four['currentManifestSHA256'];refs.append(manifest)
    result=dict(uids=four['uids'],sourceSHA256ByUid=four['sourceSHA256ByUid'],currentManifestSHA256=selected['manifestSHA256'],exactSourceCoordinateDeltas=bounds,literalCrossings=len(crossings),originalRoleBreakdown=counts,newUnmatchedContactPairs=0,originalCrossingsNeedingPhysicalReview=22,changedPointOrEdgeClassifications=89,sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='All111literalcrossings trace to alreadyexistingoriginalcontactpairs:62points,27edges,22crossings. Completeoriginal/literal arrays share exactXZ; exactYdelta bounds are recorded, not rounded or used as a new collision tolerance. No crossing is deleted/relabelled as passed. This distinguishes numeric representation effects for review; all22original physical crossing cases and full source identity/support remain independent obligations.')
    save(doc/'summary.json',result)
    refs.append(HERE/'exact_packed_world_geometry_20261009.py')
    module('nam_contact_representation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-to-literal-contact-pair-representation-readback',refs,result)


if __name__=='__main__':
    main()
