"""Rebind private terrain diagnostics after the verified additive direct imports.

Only the authenticated 21-source additive manifest change is permitted. Reuses
exact old complete bounds, freshly captures additions, and includes whole-source
native nominations alongside all existing affected BASIC forms. No publication.
"""
from pathlib import Path
import subprocess
from islands_direct_stage import ROOT,HERE,read,save,sha,rel
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds


def main():
    base=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-terrain-20261106-v1'
    out=base/'runtime-after-direct-21';assert not out.exists()
    installed_doc=ROOT/'docs/astra-city/government-import/government-islands-peng-chau-direct-20261106-v1'
    installed=read(installed_doc/'integration.json');checked=read(installed_doc/'independent-installed-readback.json')
    assert installed['neonVerified'] and checked['passed'] and installed['snapshotId']==checked['snapshotId']
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path)
    old=read(HERE/'local/government-islands-peng-chau-direct-20261106-v1/manifest-before.json')
    added_url='city/data/official-models/government-islands-peng-chau-direct-20261106-v1/catalogue.json'
    assert manifest=={**old,'officialModelCatalogues':old['officialModelCatalogues']+[added_url]}
    assert sha(manifest_path)==installed['manifestSHA256']==checked['manifestSha256']
    source=read(base/'terrain-stage.json')
    assert source['inputHashes']['3d-viewer/city/data/manifest.json']==installed['oldManifestSHA256']
    for p,h in source['inputHashes'].items():
        if p!='3d-viewer/city/data/manifest.json':assert sha(ROOT/p)==h,p
    for p,h in read(installed_doc/'retained-inputs.json').items():assert sha(ROOT/p)==h,p
    prior=ROOT/'docs/astra-city/government-import/government-xl-after-parkview16-current-native-bounds-v1-20261104'
    oldbounds=read(prior/'complete-bounds.json.gz');oldinput=read(prior/'input.json.gz');oldruntime=read(prior/'inventory.json.gz')
    assert oldinput['currentBoundOnly'] and oldruntime['startAndEndInputHashesVerified'] and not oldruntime['errors']
    assert oldruntime['wholeUnusedPositionVerticesIncluded']
    oldrows={r['uid']:r for r in oldbounds['rows']};inputs={r['uid']:r for r in oldinput['rows']}
    assert len(oldrows)==7109 and set(oldrows)==set(inputs)
    for p,h in oldruntime['inputHashes'].items():
        if p.startswith('3d-viewer/')and not p.startswith('3d-viewer/city/data/'):assert sha(ROOT/p)==h,p
    models={};catalogues=[]
    for url in manifest['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;catalogues.append({'path':rel(p),'sha256':sha(p)})
        for e in read(p)['models']:
            assert e['uid']not in models
            models[e['uid']]={'entry':e,'path':rel(p.parent/e['asset'])}
    additions=set(models)-set(oldrows);assert additions==set(installed['uids']) and len(additions)==21
    forms={};tilepins={}
    for tile in manifest['tiles']:
        p=ROOT/'3d-viewer'/tile['url'];tilepins[rel(p)]=sha(p)
        for form in read(p)['buildings']:
            if form['uid']in models:
                assert form['uid']not in forms;forms[form['uid']]=form
    assert set(forms)==set(models)
    for uid,r in inputs.items():
        assert models[uid]['entry']==r['rawCurrentEntry'] and forms[uid]==r['currentBuilding']
        assert sha(ROOT/models[uid]['path'])==oldrows[uid]['sourceSHA256']==r['source']['sha256']
    captured_input={'currentManifest':{'path':rel(manifest_path),'sha256':sha(manifest_path)},'currentCatalogueRefs':catalogues,
        'evidenceRefs':[{'path':rel(installed_doc/'independent-installed-readback.json'),'sha256':sha(installed_doc/'independent-installed-readback.json')}],
        'expectedSourceByUid':{uid:[models[uid]['entry']['sha256'],models[uid]['entry']['triangles']]for uid in sorted(additions)},
        'rows':[{'uid':uid,**models[uid],'building':forms[uid]}for uid in sorted(additions)]}
    save(out/'addition-input.json.gz',captured_input)
    subprocess.run(['node',str(HERE/'selected_original_render_attributes_v1.mjs'),rel(out/'addition-input.json.gz'),rel(out/'addition-attributes.json.gz')],cwd=ROOT,check=True)
    attrs=read(out/'addition-attributes.json.gz');assert attrs['startEndAllInputsVerified']
    bounds=list(oldrows.values())
    for row in attrs['rows']:
        proof=packed_world_bounds((ROOT/models[row['uid']]['path']).read_bytes())
        assert proof['completeOriginalTriangles']==models[row['uid']]['entry']['triangles']
        bounds.append({'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'completeFourWorldBounds':[proof['originalWholeSourceBounds'],
            row['completeLiteralWorldBounds'],row['completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds'],row['completeExplicitBalancedFloat32ModelMatrixWorldBounds']],
            'completeOriginalPOSITIONProof':proof})
    assert len(bounds)==7130
    save(out/'complete-bounds.json.gz',{'rows':bounds,'currentManifest':captured_input['currentManifest'],'oldExactBoundsReused':7109,'freshAdditions':21})
    neighbours=read(base/'neighbour-inputs.json.gz');patches=neighbours['patches'];rows={r['building']['uid']:r for r in neighbours['rows']};native_nominations={}
    for row in bounds:
        hit=set()
        for lo,hi in row['completeFourWorldBounds']:
            for i,p in enumerate(patches):
                a,b,c,d=p['bounds']
                if hi[0]>=a and lo[0]<=c and hi[2]>=b and lo[2]<=d:hit.add(i)
        if hit:
            uid=row['uid'];native_nominations[uid]=sorted(hit)
            if uid not in rows:rows[uid]={'building':forms[uid],'patchIndexes':sorted(hit),'existingNative':True}
            else:rows[uid]['patchIndexes']=sorted(set(rows[uid]['patchIndexes'])|hit);rows[uid]['existingNative']=True
    currentpins={p:h for p,h in neighbours['inputHashes'].items()if p!='3d-viewer/city/data/manifest.json'}
    currentpins[rel(manifest_path)]=sha(manifest_path)
    for p in [out/'complete-bounds.json.gz',out/'addition-attributes.json.gz',installed_doc/'independent-installed-readback.json',Path(__file__)]:currentpins[rel(p)]=sha(p)
    save(out/'neighbour-inputs.json.gz',{**neighbours,'rows':list(rows.values()),'inputHashes':currentpins,'fullSourceNativeNominations':native_nominations})
    selection=read(base/'selection.json.gz');selection.update(manifestSHA256=sha(manifest_path),previousManifestSHA256=selection['manifestSHA256'])
    identities={r['uid']:r for r in read(ROOT/'docs/astra-city/government-import/government-islands-peng-chau-identity-20261106-v1/identities.json.gz')['rows']}
    for row in selection['rows']:
        if identities[row['uid']]['passed']:row['identityProof']=identities[row['uid']]['proof']
    save(out/'selection.json.gz',selection)
    save(out/'rebind.json',{'onlyContextChange':'21 independently verified additive originals; terrain and every prior actor unchanged',
        'previousManifestSHA256':installed['oldManifestSHA256'],'currentManifestSHA256':sha(manifest_path),'nativeActors':7130,'nominatedNatives':native_nominations,
        'affectedForms':len(rows),'modelGeometryChanges':0,'terrainChanges':0,'publication':False})
    print({'reboundCandidates':len(selection['rows']),'affectedForms':len(rows),'nominatedNatives':len(native_nominations),'publication':False},flush=True)


if __name__=='__main__':main()
