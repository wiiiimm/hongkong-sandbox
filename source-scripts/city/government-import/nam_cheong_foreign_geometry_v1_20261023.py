"""Bind existing V Walk and Fu Cheong roof geometry, without changing either actor."""
from pathlib import Path
import subprocess
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
B='government-xl-nam-cheong-foreign-geometry-v1-20261023'
BASE=ROOT/'docs/astra-city/government-import';D=BASE/B
S='government-xl-nam-cheong-fu-yun-joint-current-v1-20261023-scope'


def main():
    assert not D.exists()
    _,pins=authenticate(BASE/S)
    refs=[Path(__file__),BASE/S/'result.json']
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    forms={r['uid']:r for r in take(BASE/S/'form-obligations.json.gz')}
    obligations={r['uid']:r for r in take(BASE/S/'native-obligations.json.gz')}
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==pins[str(manifest.relative_to(ROOT))]
    catalogues=[ROOT/'3d-viewer'/u for u in read(manifest)['officialModelCatalogues']]
    found=[(p,m)for p in catalogues for m in read(p)['models']if m['uid']=='landsd/262871:0'];assert len(found)==1
    cat,entry=found[0];asset=cat.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256']==obligations[entry['uid']]['sourceSHA256'];refs+=[manifest,cat,asset]
    inputrefs=[ref(p)for p in refs]
    save(D/'native-input.json.gz',dict(currentManifest=ref(manifest),currentCatalogueRefs=[ref(p)for p in catalogues],evidenceRefs=inputrefs,expectedSourceByUid={entry['uid']:[entry['sha256'],entry['triangles']]},rows=[dict(uid=entry['uid'],entry=entry,building=forms[entry['uid']],path=str(asset.relative_to(ROOT)))]))
    save(D/'basic-input.json.gz',dict(currentManifest=ref(manifest),evidenceRefs=inputrefs,rows=[forms['landsd/233291:0']]))
    tools=[('selected_original_render_attributes_v1.mjs','native-input.json.gz','native-attributes.json.gz'),('current_basic_attributes_v1_20261023.mjs','basic-input.json.gz','basic-attributes.json.gz')]
    for script,inp,out in tools:
        with (D/(script+'.log')).open('w')as log:subprocess.run(['node',str(HERE/script),str((D/inp).relative_to(ROOT)),str((D/out).relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        output=read(D/out);assert output['startEndAllInputsVerified']
        for p,h in output['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
        refs.append(HERE/script)
    summary=dict(uids=['landsd/268867:0','landsd/270874:0'],foreignNativeUid=entry['uid'],foreignNativeSourceSHA256=entry['sha256'],foreignBasicUid='landsd/233291:0',foreignBasicKind=forms['landsd/233291:0']['structureType'],foreignNativeAssetPath=str(asset.relative_to(ROOT)),allForeignActorsRetained=True,sourceGeometryChanges=0,installationApproved=False,qualification='Complete existing native renderer arrays in all three shader arithmetic orders and existing production BASIC roof/post meshes with all positions/indices retained. Geometry capture only, no source/identity/collision exemption.')
    save(D/'summary.json',summary);module('nam_foreign_geometry_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'complete-current-foreign-native-and-basic-geometry',refs,summary)


if __name__=='__main__':main()
