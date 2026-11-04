"""Locate every Island Industrial crossing/contact in original source coordinates."""
from pathlib import Path
from fractions import Fraction
from collections import defaultdict
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import'
    source='government-xl-island-industrial-contact-roles-v1-20261023'
    batch='government-xl-island-industrial-interface-heights-v1-20261023'
    out=base/batch
    assert not out.exists()
    _,pins=authenticate(base/source)
    refs=[Path(__file__),base/source/'result.json']
    def take(name):
        p=base/source/name
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
        refs.append(p);return read(p)
    context=take('summary.json');rows=take('classified-contacts.json.gz')
    groups=defaultdict(list)
    for r in rows:
        points=[[Fraction(v)for v in point]for point in r['exactPoints']]
        assert points
        item=dict(sourceFaceA=r['sourceFaceA'],sourceFaceB=r['sourceFaceB'],dimension=r['dimension'],primitiveDimensions=r['primitiveDimensions'],exactPoints=r['exactPoints'],worldBounds=dict(min=[float(min(p[i]for p in points))for i in range(3)],max=[float(max(p[i]for p in points))for i in range(3)]))
        groups[r['contactRole']].append(item)
    save(out/'interfaces.json.gz',dict(groups))
    summaries={role:dict(contacts=len(items),sourceFacesA=sorted({r['sourceFaceA']for r in items}),sourceFacesB=sorted({r['sourceFaceB']for r in items}),minimumY=min(r['worldBounds']['min'][1]for r in items),maximumY=max(r['worldBounds']['max'][1]for r in items))for role,items in groups.items()}
    result=dict(uids=context['uids'],sourceSHA256ByUid=context['sourceSHA256ByUid'],allContactsAccountedFor=sum(v['contacts']for v in summaries.values())==context['contacts'],roles=summaries,sourceGeometryChanges=0,installationApproved=False,qualification='All exact pair contacts located by source face and rational endpoints. Height grouping is diagnostic only, no architectural/support interpretation or tolerance waiver.')
    save(out/'summary.json',result)
    module('island_interface_heights_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'complete-original-interface-height-accounting',refs,result)
    print({k:{n:v for n,v in r.items()if n not in ['sourceFacesA','sourceFacesB']}for k,r in summaries.items()},flush=True)


if __name__=='__main__':main()
