"""Enumerate exact unchanged-source interfaces to newly recovered neighbouring originals."""
import argparse
from pathlib import Path
from collections import Counter
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_primitive_contacts_v1 import exact_component_contacts_with_primitives


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','capture','acquired']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()
    refs=[Path(__file__)]
    def take(batch,filename):
        _,pins=authenticate(base/batch);p=base/batch/filename;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([base/batch/'result.json',p]);return read(p)
    selected=take(a.capture,'selection.json.gz')['rows'];recovered=take(a.acquired,'summary.json');assert recovered['sourceRecovered']
    assert 0<len(selected)<=8 and 0<len(recovered['rows'])<=8
    original=[dict(uid=r['uid'],path=r['candidate']['path'],sha256=r['sourceSHA256'],faces=r['triangles'])for r in selected]
    adjacent=[dict(uid=r['uid'],path=r['asset']['path'],sha256=r['sourceSHA256'],faces=r['completeSourceFaces'])for r in recovered['rows']]
    assert not {r['uid']for r in original}&{r['uid']for r in adjacent}
    arrays={}
    for row in original+adjacent:
        p=ROOT/row['path'];raw=p.read_bytes();assert digest(raw)==row['sha256'];refs.append(p);tri=decode_original_world_triangles(raw);assert len(tri)==row['faces'];arrays[row['uid']]=tri
    rows=[]
    for owner in original:
        for neighbour in adjacent:
            left,right=arrays[owner['uid']],arrays[neighbour['uid']]
            contacts=exact_component_contacts_with_primitives(left,range(len(left)),right,range(len(right)),maximum_pairs=1000000)
            assert contacts['allPairsExamined']
            name=owner['uid'].replace('/','-').replace(':','-')+'--'+neighbour['uid'].replace('/','-').replace(':','-')+'.json.gz';save(out/name,contacts)
            row=dict(uid=owner['uid'],adjacentUid=neighbour['uid'],sourceSHA256=owner['sha256'],adjacentSHA256=neighbour['sha256'],trianglePairsTested=contacts['trianglePairsTested'],contacts=len(contacts['contacts']),contactDimensions=dict(Counter(str(c['dimension'])for c in contacts['contacts'])),allPairsExamined=True,interfaces=name)
            rows.append(row);print(row,flush=True)
    result=dict(uids=sorted(arrays),rows=rows,sourceGeometryChanges=0,installationApproved=False,qualification='Complete exact original primitive-contact diagnostics, including zero-area primitives. Contacts alone establish neither identity, ownership, physical support nor permitted collision. No generated geometry or acceptance credit.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['exact_original_primitive_contacts_v1.py','exact_packed_world_geometry_20261009.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py'])
    module('adjacent_complete_interface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-acquired-neighbour-original-interfaces',refs,result)


if __name__=='__main__':main()
