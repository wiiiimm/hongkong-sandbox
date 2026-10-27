"""Trace represented pair crossings to original facet pairs; never approval."""
import argparse
from collections import Counter
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_native_contact_lineage_v2_20261027 import coordinate_deltas
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','attributes','roles','contacts']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    refs=[Path(__file__),HERE/'original_native_contact_lineage_v2_20261027.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    contacts=take(a.contacts,base/a.contacts/'summary.json');uids=contacts['uids'];assert len(uids)==2
    roles=take(a.roles,base/a.roles/'summary.json');assert roles['sourceSHA256ByUid']==contacts['sourceSHA256ByUid']
    selected={r['uid']:r for r in take(a.runtime,base/a.runtime/'selection.json.gz')['rows']}
    attrs_doc=take(a.attributes,base/a.attributes/'attributes.json.gz');assert attrs_doc['startEndAllInputsVerified'];attrs={r['uid']:r for r in attrs_doc['rows']}
    worlds={mode:{} for mode in ['original','literal','leftF32','balancedF32']};deltas={}
    fields=dict(literal='completeLiteralWorldPosition',leftF32='completeExplicitLeftAssociatedFloat32WorldPosition',balancedF32='completeExplicitBalancedFloat32WorldPosition')
    for uid in uids:
        row=selected[uid];path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256']==contacts['sourceSHA256ByUid'][uid]==attrs[uid]['sourceSHA256'];refs.append(path)
        original=decode_original_world_triangles(path.read_bytes());worlds['original'][uid]=original;index=np.asarray(attrs[uid]['completeOriginalIndex']).reshape(-1,3);deltas[uid]={}
        for mode,field in fields.items():
            tri=np.asarray(attrs[uid][field],dtype='<f8').reshape(-1,3)[index];worlds[mode][uid]=tri;deltas[uid][mode]=coordinate_deltas(original,tri)
    raw=take(a.roles,base/a.roles/'original.json.gz');by_pair={(r['sourceFaceA'],r['sourceFaceB']):r for r in raw};assert len(by_pair)==len(raw)
    rows=[]
    for mode,world in worlds.items():
        measured=next(r for r in contacts['rows'] if r['mode']==mode)
        assert measured['sourceWorldSHA256ByUid']=={uid:digest(world[uid].tobytes()) for uid in uids}
        represented=take(a.roles,base/a.roles/(mode+'.json.gz'));crossings=[]
        for row in represented:
            if row['contactRole']!='transverse-surface-crossing':continue
            old=by_pair.get((row['sourceFaceA'],row['sourceFaceB']))
            crossings.append(dict(sourceFaceA=row['sourceFaceA'],sourceFaceB=row['sourceFaceB'],
                 originalPairRole=old['contactRole'] if old else None,originalDimension=old['dimension'] if old else None,
                 representedBounds=row['bounds'],representedMaximumSpanM=row['maximumSpanM']))
        save(out/(mode+'.json.gz'),crossings)
        counts=dict(Counter(r['originalPairRole'] or 'no-original-facet-pair-contact' for r in crossings))
        rows.append(dict(mode=mode,crossings=len(crossings),originalPairRoles=counts,
                         crossingsWithoutOriginalPair=sum(r['originalPairRole'] is None for r in crossings)))
    result=dict(uids=uids,sourceSHA256ByUid=contacts['sourceSHA256ByUid'],rows=rows,coordinateDeltasByUid=deltas,
                allRepresentedCrossingsHaveOriginalFacetPairContact=all(r['crossingsWithoutOriginalPair']==0 for r in rows),
                sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,
                qualification='Exact complete indexed coordinate deltas and original facet-pair contact lineage. Original transverse intersections remain real raw source contacts. No generic collision exemption, role acceptance or installation credit.')
    save(out/'summary.json',result)
    module('pair_lineage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-original-pair-represented-contact-lineage',list(dict.fromkeys(refs)),result)
    print(rows,flush=True)


if __name__=='__main__':main()
