"""Reuse exact contact math only after fresh complete current native-array replay.

Unrelated catalogue changes do not permit ignoring old input hashes. Instead,
load every nominated native from current catalogues, compare its complete actual
row with the prior capture, and bind unchanged contacts to this fresh capture.
No geometry, contact, support, identity or publication approval is granted.
"""
import argparse,copy,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','scope','runtime','attributes','historical-attributes','prior','inventory']:
        parser.add_argument('--'+key,required=True)
    a=parser.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()
    refs,pins=[Path(__file__)],{}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    scope=take(a.scope,'summary.json');selection=take(a.runtime,'selection.json.gz');sources={r['uid']:r for r in selection['rows']}
    current=take(a.attributes,'attributes.json.gz');historic=take(a.historical_attributes,'attributes.json.gz')
    assert current['startEndAllInputsVerified']and historic['startEndAllInputsVerified']
    old_source={r['uid']:r for r in historic['rows']};new_source={r['uid']:r for r in current['rows']}
    assert set(new_source)==set(sources)and all(new_source[u]==old_source[u]for u in sources),'Complete source arrays changed: do not reuse contacts'
    old=take(a.prior,'summary.json');old_input=take(a.prior,'native-input.json.gz');old_attrs=take(a.prior,'native-attributes.json.gz')
    assert old_attrs['startEndAllInputsVerified']and old_attrs['productionCataloguePreparationReplayed']
    inventory=take(a.inventory,'complete-bounds.json.gz');bounds={r['uid']:r for r in inventory['rows']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());refs.append(manifest)
    assert mh==scope['currentManifestSHA256']==selection['manifestSHA256']==pins[a.inventory][str(manifest.relative_to(ROOT))]
    for uid,row in sources.items():
        p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256']==new_source[uid]['sourceSHA256'];refs.append(p)
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];refs.append(tile)
        assert [f for f in read(tile)['buildings']if f['uid']==uid]==[row['source']['building']]
    pairs={(r['uid'],n['uid'])for r in scope['rows']for n in r['nearbyNativeActors']}
    rows=[r for r in old['rows']if r['uid']in sources]
    assert len(rows)==len(pairs)and {(r['uid'],r['nativeUid'])for r in rows}==pairs
    assert not any(r['uid']in sources for r in old['strictlySeparatedNativePairs']), 'This rebind supports overlapping nominated pairs only'
    targets={n for _,n in pairs};assert targets
    old_native={r['uid']:r for r in old_input['rows']};old_array={r['uid']:r for r in old_attrs['rows']}
    catalogue_refs=[];models={}
    for url in read(manifest)['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;catalogue_refs.append(ref(p));refs.append(p)
        for entry in read(p)['models']:
            assert entry['uid']not in models;models[entry['uid']]=(entry,p)
    native_rows=[]
    for uid in sorted(targets):
        before=old_native[uid];entry,cat=models[uid];assert entry==before['entry'],'Native metadata changed: fresh contact investigation required'
        p=ROOT/before['path'];assert digest(p.read_bytes())==entry['sha256']==bounds[uid]['sourceSHA256'];refs.append(p)
        assert cat==ROOT/before['cataloguePath']
        matches=[]
        for tile in read(manifest)['tiles']:
            path=ROOT/'3d-viewer'/tile['url']
            assert digest(path.read_bytes())==inventory['currentFormTileHashes'][str(path.relative_to(ROOT))]
            found=[f for f in read(path)['buildings']if f['uid']==uid]
            if found:matches.extend(found);refs.append(path)
        assert matches==[before['building']]
        native_rows.append(copy.deepcopy(before))
    input_path=out/'native-input.json.gz'
    save(input_path,dict(currentManifest=ref(manifest),currentCatalogueRefs=catalogue_refs,evidenceRefs=[ref(base/a.scope/'summary.json'),ref(base/a.inventory/'complete-bounds.json.gz')],expectedSourceByUid={r['uid']:[r['entry']['sha256'],r['entry']['triangles']]for r in native_rows},rows=native_rows))
    tool=HERE/'selected_original_render_attributes_v2_20261024.mjs';output=out/'native-attributes.json.gz';refs.append(tool)
    assert digest(tool.read_bytes())==pins[a.prior][str(tool.relative_to(ROOT))]
    # Original contact decoding is also unchanged, so equal original bytes and
    # equal complete literal/F32 rows bind every old coordinate representation.
    decoder=HERE/'exact_packed_world_geometry_20261009.py';assert digest(decoder.read_bytes())==pins[a.prior][str(decoder.relative_to(ROOT))];refs.append(decoder)
    with(out/'capture.log').open('w')as log:subprocess.run(['node',str(tool),str(input_path.relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    fresh=read(output);assert fresh['startEndAllInputsVerified']and fresh['productionCataloguePreparationReplayed']
    arrays={r['uid']:r for r in fresh['rows']};assert set(arrays)==targets
    for uid in targets:
        assert arrays[uid]==old_array[uid],'Complete native array row changed: do not reuse contact math'
        for i,key in enumerate(['completeLiteralWorldBounds','completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds','completeExplicitBalancedFloat32ModelMatrixWorldBounds'],1):assert arrays[uid][key]==bounds[uid]['completeFourWorldBounds'][i]
    for r in rows:
        assert r['sourceSHA256']==sources[r['uid']]['sourceSHA256']and r['rawCurrentNativeEntry']==models[r['nativeUid']][0]
        assert {m['mode']for m in r['modes']}=={'original','literal','leftF32','balancedF32'}
        for mode in r['modes']:
            assert mode['sourceFaces']==sources[r['uid']]['triangles']and mode['nativeFaces']==models[r['nativeUid']][0]['triangles']
            name=r['uid'].split('/')[1]+'--'+r['nativeUid'].split('/')[1]+'--'+mode['mode']+'.json.gz'
            proof=take(a.prior,name);assert proof['allPairsExamined']and proof['sourceFacesOmitted']==0 and len(proof['contacts'])==mode['finiteContactPairs']
            (out/name).write_bytes((base/a.prior/name).read_bytes())
    for path,sha in fresh['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    assert digest(manifest.read_bytes())==mh
    result=dict(uids=sorted(sources),rows=rows,strictlySeparatedNativePairs=[],currentManifestSHA256=mh,currentNativeActors=len(bounds),completeCurrentSourceArraysIdentical=True,completeCurrentNativeArraysIdentical=True,contactCalculationsRepeated=0,sourceGeometryChanges=0,nativeMetadataChanges=0,installationApproved=False,publication=False,qualification=__doc__)
    save(out/'summary.json',result)
    module('exact_current_native_contact_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-complete-array-replay-exact-native-contact-math-rebind',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
