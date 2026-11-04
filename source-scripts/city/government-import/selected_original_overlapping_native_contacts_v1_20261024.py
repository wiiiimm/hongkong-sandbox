"""Bind current installed overlapping natives and measure exact before/after contacts.

Diagnostic only. Existing installed dependencies and every raw contact are retained;
no source, support metadata, acceptance policy or production asset is changed.
"""
import argparse
from pathlib import Path
import subprocess
import numpy as np
from urllib.parse import urljoin
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts

FIELDS = [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','scope','runtime','attributes','neighbours']: p.add_argument('--'+k,required=True)
    a=p.parse_args(); assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base=ROOT/'docs/astra-city/government-import'; out=base/a.batch; assert not out.exists()
    refs=[Path(__file__)]; pins={}
    def take(batch,name):
        if batch not in pins: pins[batch]=authenticate(base/batch)[1]; refs.append(base/batch/'result.json')
        path=base/batch/name; assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    scope=take(a.scope,'summary.json'); selection=take(a.runtime,'selection.json.gz')
    attrs={r['uid']:r for r in take(a.attributes,'attributes.json.gz')['rows']}
    neighbours=take(a.neighbours,'neighbour-inputs.json.gz')
    manifest=ROOT/'3d-viewer/city/data/manifest.json'; manifest_sha=digest(manifest.read_bytes())
    assert manifest_sha==scope['currentManifestSHA256']==selection['manifestSHA256']
    refs.append(manifest); forms={r['building']['uid']:r['building'] for r in neighbours['rows']}
    for path,sha in neighbours['inputHashes'].items():
        assert digest((ROOT/path).read_bytes())==sha; refs.append(ROOT/path)
    entries={}; catalogues=[]
    for url in read(manifest)['officialModelCatalogues']:
        path=ROOT/'3d-viewer'/url; catalogues.append(path)
        for e in read(path)['models']:
            assert e['uid'] not in entries
            entries[e['uid']]=(e,path)
    wanted={}; separated=[]; pairs=[]
    for source in scope['rows']:
        lo,hi=np.asarray(source['completeSourceFourWorldBounds'])
        for native in source['nearbyNativeActors']:
            ns=np.asarray(native['completeFourWorldBounds']).reshape(-1,3); gaps=np.maximum(ns.min(0)-hi,lo-ns.max(0))
            if np.any(gaps>0):
                separated.append(dict(uid=source['uid'],nativeUid=native['uid'],axisGapsM=gaps.tolist(),sourceSHA256=native['sourceSHA256']))
            else:
                uid=native['uid']; entry,cat=entries[uid]; assert entry['sha256']==native['sourceSHA256']
                assert uid in forms and entry['buildingCSUID']==forms[uid]['buildingCSUID']
                asset=(cat.parent/entry['asset']).resolve(); assert asset.is_relative_to(ROOT)
                assert digest(asset.read_bytes())==entry['sha256']; refs.extend([cat,asset])
                wanted[uid]=dict(uid=uid,entry=entry,building=forms[uid],path=str(asset.relative_to(ROOT)))
                pairs.append((source['uid'],uid))
    assert wanted and pairs
    def ref(path): return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    input_path=out/'native-input.json.gz'
    save(input_path,dict(currentManifest=ref(manifest),currentCatalogueRefs=[ref(p) for p in catalogues],evidenceRefs=[ref(base/a.scope/'summary.json'),ref(base/a.neighbours/'neighbour-inputs.json.gz')],expectedSourceByUid={uid:[r['entry']['sha256'],r['entry']['triangles']] for uid,r in wanted.items()},rows=list(wanted.values())))
    tool=HERE/'selected_original_render_attributes_v1.mjs'; output=out/'native-attributes.json.gz'
    with (out/'capture.log').open('w') as log: subprocess.run(['node',str(tool),str(input_path.relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    native_output=read(output); native_attrs={r['uid']:r for r in native_output['rows']}
    def worlds(row,asset):
        index=np.asarray(row['completeOriginalIndex']).reshape(-1,3)
        return {'original':decode_original_world_triangles(asset.read_bytes()),**{mode:np.asarray(row[field]).reshape(-1,3)[index] for mode,field in FIELDS}}
    source_rows={r['uid']:r for r in selection['rows']}; results=[]
    for uid,other in pairs:
        source=source_rows[uid]; asset=ROOT/source['candidate']['path']; assert digest(asset.read_bytes())==source['sourceSHA256']; refs.append(asset)
        sw=worlds(attrs[uid],asset); nw=worlds(native_attrs[other],ROOT/wanted[other]['path']); modes=[]
        for mode,tri in sw.items():
            target=nw[mode]; proof=exact_finite_contacts(tri,list(range(len(tri))),target,list(range(len(target))))
            name=uid.split('/')[1]+'--'+other.split('/')[1]+'--'+mode+'.json.gz'; save(out/name,proof)
            positive=[c for c in proof['contacts'] if c['sourcePrimitiveDimensionA']==2 and c['sourcePrimitiveDimensionB']==2 and c['dimension']>0]
            modes.append(dict(mode=mode,sourceFaces=len(tri),nativeFaces=len(target),finiteContactPairs=len(proof['contacts']),positiveSurfaceContactPairs=len(positive),areaContactPairs=sum(c['dimension']==2 for c in positive)))
            print(dict(uid=uid,nativeUid=other,**modes[-1]),flush=True)
        results.append(dict(uid=uid,nativeUid=other,sourceSHA256=source['sourceSHA256'],nativeSHA256=wanted[other]['entry']['sha256'],rawCurrentNativeEntry=wanted[other]['entry'],modes=modes))
    for path,sha in native_output['inputHashes'].items(): assert digest((ROOT/path).read_bytes())==sha; refs.append(ROOT/path)
    assert digest(manifest.read_bytes())==manifest_sha
    result=dict(uids=selection['uids'] if 'uids' in selection else [r['uid'] for r in selection['rows']],rows=results,strictlySeparatedNativePairs=separated,sourceGeometryChanges=0,nativeMetadataChanges=0,installationApproved=False,publication=False,qualification='All overlapping nominated installed native actors captured through current production loader with exact unchanged current entry/form/asset bytes. Every complete source/native finite triangle pair tested in four world representations; disjoint nominations retain exact strict box separation. Positive contacts need source relationship and replacement support review. No installed dependency removed, no support or collision approval.')
    save(out/'summary.json',result); refs.extend([tool,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py'])
    module('overlapping_native_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-proposed-original-current-overlapping-native-contacts',list(dict.fromkeys(refs)),result)

if __name__=='__main__': main()
