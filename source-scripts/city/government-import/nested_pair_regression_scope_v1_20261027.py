"""Prepare complete affected-actor regressions from exact nested edit separation."""
import argparse
import json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from nested_pair_changed_regions_v1_20261027 import verify_changed_regions
from primrose_compound_foundation_v2_20261015 import module


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','candidate','separations','inventory']:parser.add_argument('--'+key,required=True)
    a=parser.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not out.exists()
    refs=[Path(__file__),HERE/'nested_pair_changed_regions_v1_20261027.py'];receipts={};pins={}
    for name in [a.candidate,a.separations,a.inventory]:
        receipts[name],bound=authenticate(base/name);refs.append(base/name/'result.json')
        for path,sha in bound.items():assert path not in pins or pins[path]==sha;pins[path]=sha
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    rec=receipts[a.candidate];separation=take(base/a.separations/'summary.json')
    assert rec['status']=='private-nested-coordinated-surface-validator-passed' and separation['allCurrentInstalledAssetBytesVerified']
    inventory=take(base/a.inventory/'complete-bounds.json.gz');assert separation['completeInstalledActorsAccounted']==len(inventory['rows'])
    oldinfo=rec['replacedNativeTerrain'];assert len(oldinfo)==1;oldinfo=oldinfo[0]
    oldpath=ROOT/'3d-viewer'/oldinfo['url'];old=take(oldpath);new=take(ROOT/rec['candidate']['path'])
    changed=verify_changed_regions(old,new,rec);assert changed['closedChangedRegions']==separation['changedClosedXZRegions']
    refs.extend(ROOT/name for name in changed['inputPaths'])
    support_rows=take(base/a.separations/'basic-support-separations.json')
    affected_supports=[r for r in support_rows if not r['wholeSupportFootprintOutsideEveryChangedRegion']]
    affected_owners={uid for r in affected_supports for uid in r['owners']}
    required=set(separation['affectedNativeUids'])|set(oldinfo['retainedUids'])|affected_owners
    assert required<={r['uid'] for r in inventory['rows']}
    regions=[shapely.box(*bounds).buffer(.5,join_style='mitre') for bounds in changed['closedChangedRegions']]
    region=shapely.union_all(regions);forms={};mp=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(mp)
    explicit=required|set(rec['uids'])|{r['uid'] for r in affected_supports}
    for tile in manifest['tiles']:
        path=ROOT/'3d-viewer'/tile['url'];key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==inventory['currentFormTileHashes'][key]
        found=False
        for form in read(path)['buildings']:
            points=np.asarray([p for ring in form.get('rings',[]) for p in ring])
            if form['uid'] not in explicit:
                if not len(points):continue
                lo,hi=points.min(0),points.max(0)
                if not region.intersects(shapely.box(*lo,*hi)):continue
            assert form['uid'] not in forms;forms[form['uid']]=form;found=True
        if found:refs.append(path)
    assert explicit<=set(forms)
    builder=module('nested_scope_extent',HERE/'resolve-pass-indexed-parent-clipping.py');refs.append(HERE/'resolve-pass-indexed-parent-clipping.py')
    root=take(ROOT/'3d-viewer/city/data/terrain.json');bounds=builder.extent(old['coarseCells'],root)
    contacts=[]
    for entry in manifest['terrainPatches']:
        path=ROOT/'3d-viewer'/entry['url'];node=read(path)
        domain=shapely.box(*builder.extent(node['coarseCells'],root));area=domain.intersection(region).area
        if area>0:contacts.append(dict(url=entry['url'],coarseOverlapAreaM2=area,packedContacts=[]));refs.append(path)
    assert {r['url'] for r in contacts}=={oldinfo['url']},'Every affected terrain parent must be retained explicitly'
    scope=dict(uids=rec['uids'],touchingNativeUids=sorted(required),regionalParentExtent=bounds,
               regionalCoarseCells=new['coarseCells'],terrainContacts=contacts,intersectingForms=len(forms),
               changedClosedXZRegions=changed['closedChangedRegions'],
               scopePolicy='All actors outside changed facets accounted by exact whole-source separation; every intersecting native, retained group target, affected BASIC support owner and intersecting BASIC form included.')
    candidate=dict(**rec['candidate'],replaces=dict(url=oldinfo['url'],sha256=oldinfo['sha256'],retainedUids=oldinfo['retainedUids']),uids=rec['uids'],bounds=bounds)
    save(out/'scope.json',scope);save(out/'form-obligations.json.gz',list(forms.values()))
    result=dict(uids=rec['uids'],candidate=candidate,requiredNativeUids=sorted(required),forms=len(forms),
                affectedRegisteredBasicSupportUids=separation['affectedRegisteredBasicSupportUids'],
                allInstalledActorsAccounted=separation['completeInstalledActorsAccounted'],
                sourceGeometryChanges=0,installationApproved=False,publication=False,
                qualification='Complete script regression inputs after exact unchanged-outside-edit proof. Every affected dependency owner included. This prepares checks; it does not grant regression or installation approval.')
    for path,sha in pins.items():assert digest((ROOT/path).read_bytes())==sha
    result=json.loads(json.dumps(result));save(out/'summary.json',result)
    module('nested_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-exact-nested-edit-retained-and-affected-regression-inputs',list(dict.fromkeys(refs)),result)
    print(dict(forms=len(forms),requiredNativeUids=sorted(required),affectedSupports=result['affectedRegisteredBasicSupportUids']),flush=True)


if __name__=='__main__':main()
