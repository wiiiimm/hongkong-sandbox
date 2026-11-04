"""Complete exact pair contacts in every distinct original/renderer stream.

Reuse an existing exhaustive proof only under byte-for-byte coordinate equality.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives
from exact_original_shell_intersections_20261009 import rational_face
from exact_contact_role_context_v1_20261023 import contact_role

BATCH='government-xl-nam-cheong-pair-four-world-contacts-v1-20261023'
CAP='government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'
ATTR='government-xl-nam-cheong-fu-yun-joint-attributes-v1-20261023'
REUSE='government-xl-nam-cheong-current-exact-context-reuse-v1-20261023'
ORIGINAL='government-xl-nam-cheong-fu-yun-complete-interface-v2-20261023'
ROLES='government-xl-nam-cheong-fu-yun-contact-roles-v1-20261023'
UIDS=['landsd/268867:0','landsd/270874:0']


def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH
    assert not doc.exists()
    refs,pins=[Path(__file__)],{}
    for name in [CAP,ATTR,REUSE,ORIGINAL,ROLES]:
        _,pins[name]=authenticate(base/name);refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(CAP,base/CAP/'selection.json.gz');selected={r['uid']:r for r in selection['rows']}
    attr=take(ATTR,base/ATTR/'attributes.json.gz');assert attr['startEndAllInputsVerified'];attrs={r['uid']:r for r in attr['rows']}
    reuse=take(REUSE,base/REUSE/'summary.json');assert reuse['currentManifestSHA256']==selection['manifestSHA256']
    original=take(ORIGINAL,base/ORIGINAL/'complete-contacts.json.gz');oldsummary=take(ORIGINAL,base/ORIGINAL/'summary.json')
    roles=take(ROLES,base/ROLES/'classified-contacts.json.gz');assert original['allPairsExamined'] and len(roles)==len(original['contacts'])
    modes={k:[] for k in ['original','literal','left','balanced']}
    shas={}
    for uid in UIDS:
        r=selected[uid];asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256']==attrs[uid]['sourceSHA256']==oldsummary['sourceSHA256ByUid'][uid];refs.append(asset);shas[uid]=r['sourceSHA256']
        modes['original'].append(decode_original_world_triangles(raw))
        ix=np.asarray(attrs[uid]['completeOriginalIndex']).reshape(-1,3)
        for name,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:
            modes[name].append(np.asarray(attrs[uid][key]).reshape(-1,3)[ix])
    results=[]
    for mode,triangles in modes.items():
        equal=all(np.array_equal(t,old) for t,old in zip(triangles,modes['original']))
        hashes={uid:digest(t.tobytes()) for uid,t in zip(UIDS,triangles)}
        if equal:
            report=original;classified=roles
            provenance=dict(exactCoordinateEqualityToOriginal=True,reusedContactProofBatch=ORIGINAL,reusedRolesBatch=ROLES,originalCompleteContactLeafSHA256=digest((base/ORIGINAL/'complete-contacts.json.gz').read_bytes()))
        else:
            a,b=triangles
            report=exact_component_contacts_with_primitives(a,range(len(a)),b,range(len(b)),maximum_pairs=1000000)
            assert report['allPairsExamined']
            save(doc/(mode+'-complete-contacts.json.gz'),report)
            classified=[]
            for c in report['contacts']:
                points=[tuple(Fraction(v) for v in p) for p in c['exactPoints']]
                role=contact_role(rational_face(a[c['sourceFaceA']]),rational_face(b[c['sourceFaceB']]),points,c['dimension'],c['primitiveDimensions'])
                classified.append(dict(c,contactRole=role))
            save(doc/(mode+'-classified-contacts.json.gz'),classified)
            provenance=dict(exactCoordinateEqualityToOriginal=False,independentlyEnumeratedEveryInclusiveAABBPair=True)
        summary=dict(mode=mode,completeSourceFaces=[len(t) for t in triangles],sourceWorldSHA256ByUid=hashes,allPairsExamined=report['allPairsExamined'],trianglePairsTested=report['trianglePairsTested'],contactCount=len(classified),roles=dict(Counter(c['contactRole'] for c in classified)),transverseSourceFaces=sorted({c['sourceFaceA'] for c in classified if c['contactRole']=='transverse-surface-crossing'}),provenance=provenance,acceptableContacts=False)
        results.append(summary);print(summary,flush=True)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    summary=dict(uids=UIDS,sourceSHA256ByUid=shas,rows=results,currentManifestSHA256=selection['manifestSHA256'],allFourRepresentationsAccounted=True,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Everydistinctsourcecoordinatepair exhaustivelychecked. Original/left/balancedproof reusedonlyaftercompletearrayequality; literalFloat64 stream independentlyenumerated. Allcontactsanddegenerateprimitives retained; differentcountsare notsilentlyequated. Contactroles do not establishidentity, ownership, architecturalintent, supportoracceptablecollision.')
    save(doc/'summary.json',summary)
    refs.extend(HERE/name for name in ['exact_original_primitive_contacts_v1.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','exact_contact_role_context_v1_20261023.py','exact_packed_world_geometry_20261009.py'])
    module('nam_pair_four_world_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-exact-four-world-original-assembly-contacts',refs,summary)


if __name__=='__main__':
    main()
