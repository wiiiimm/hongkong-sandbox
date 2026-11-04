"""Exact complete ancillary-to-remainder contacts in four source representations.

All component faces and every other original face participate. Contacts do not
identify an architectural role or confer structural root/installation approval.
"""
import argparse
import uuid
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_low_face_group_views_v2_20261026 import groups


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','roof-context','uid']:
        p.add_argument('--'+key,required=True)
    p.add_argument('--component',type=int,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch
    assert not doc.exists()
    refs=[Path(__file__)];pins={}
    for name in [a.runtime,a.attributes,a.roof_context]:
        directory=base/name;_,bound=authenticate(directory);refs.append(directory/'result.json')
        for path,sha in bound.items():
            assert path not in pins or pins[path]==sha
            pins[path]=sha
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(base/a.runtime/'selection.json.gz')
    source=next(r for r in selection['rows'] if r['uid']==a.uid)
    attributes=take(base/a.attributes/'attributes.json.gz')
    assert attributes['startEndAllInputsVerified']
    attr=next(r for r in attributes['rows'] if r['uid']==a.uid)
    context=take(base/a.roof_context/'roof-context.json.gz')
    assert source['sourceSHA256']==attr['sourceSHA256']==context['sourceSHA256']
    chosen=next(r for r in context['completeOriginalComponents'] if r['component']==a.component)
    ids=chosen['completeOriginalFaceIds']
    assert ids==sorted(set(ids)) and ids
    path=ROOT/source['candidate']['path'];assert digest(path.read_bytes())==source['sourceSHA256'];refs.append(path)
    claim=reservations.claim('original-component-attachment-'+str(uuid.uuid4()), ['building:'+a.uid],batch=a.batch,ttl=1800)
    assert claim['ok'];lease=claim['reservation']
    try:
        original=decode_original_world_triangles(path.read_bytes())
        assert digest(original.astype('<f8').tobytes())==context['originalWorldSHA256']
        assert groups(original,list(range(len(original))))[a.component]==ids
        index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
        worlds=dict(original=original,**{name:np.asarray(attr[field],dtype='<f8').reshape(-1,3)[index]
            for name,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]})
        other=sorted(set(range(len(original)))-set(ids));assert other
        summaries=[]
        for mode,tri in worlds.items():
            assert len(tri)==source['triangles']
            proof=exact_finite_contacts(tri,ids,tri,other)
            assert proof['allPairsExamined'] and proof['sourceFacesOmitted']==0
            save(doc/(mode+'.json.gz'),proof)
            contacts=proof['contacts']
            peers=sorted({r['sourceFaceB'] for r in contacts})
            summaries.append(dict(mode=mode,sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),
                completeAncillaryFaces=len(ids),completeOtherSourceFaces=len(other),
                allFiniteContacts=len(contacts),positiveDimensionalContacts=sum(r['dimension']>0 for r in contacts),
                areaContacts=sum(r['dimension']==2 for r in contacts),
                contactedOtherOriginalFaces=peers,
                otherFaceContext=[dict(sourceFace=i,vertices=tri[i].tolist()) for i in peers]))
            assert reservations.owns(lease)
        out=dict(uids=[a.uid],sourceSHA256=source['sourceSHA256'],component=a.component,
            completeAncillaryFaceIds=ids,completeOtherFaceIds=other,rows=summaries,
            sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAccepted=False,
            structuralRootCredit=False,installationApproved=False,
            qualification='Exact finite ancillary/remainder contacts; each complete named component face and every other original source face retained in original/literal/two explicit Float32 representations. Self/component-internal contacts excluded. A contact is not proof that the remainder is rooted, a source role is correct, or a BASIC actor may be hidden.')
        save(doc/'summary.json',out)
        refs.extend(HERE/name for name in ['exact_packed_world_geometry_20261009.py',
            'exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py',
            'exact_original_component_contacts_20261009.py','original_low_face_group_views_v2_20261026.py'])
        module('original_component_attachment_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            a.batch,'four-world-complete-original-ancillary-remainder-attachment-context',list(dict.fromkeys(refs)),out)
        print([dict(mode=r['mode'],contacts=r['allFiniteContacts'],positive=r['positiveDimensionalContacts']) for r in summaries],flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__=='__main__':
    main()
