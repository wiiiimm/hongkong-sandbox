"""Archive exact unchanged installed actors required by an authenticated terrain scope."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','scope','inventory']:ap.add_argument('--'+key,required=True)
    a=ap.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.scope,a.inventory])and not out.exists()
    refs=[Path(__file__)];pins={}
    for name in [a.scope,a.inventory]:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
    def take(n,file):
        p=base/n/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    scope=take(a.scope,'scope.json');forms={r['uid']:r for r in take(a.scope,'form-obligations.json.gz')};inventory=take(a.inventory,'complete-bounds.json.gz');indexed={r['uid']:r for r in inventory['rows']}
    wanted=set(scope['touchingNativeUids']);assert wanted and wanted<=set(forms)&set(indexed)
    mp=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(mp.read_bytes());assert msha==pins[a.scope][str(mp.relative_to(ROOT))]==pins[a.inventory][str(mp.relative_to(ROOT))];refs.append(mp)
    rows=[];all_uids=set()
    for url in read(mp)['officialModelCatalogues']:
        cp=ROOT/'3d-viewer'/url
        for entry in read(cp)['models']:
            uid=entry['uid'];assert uid not in all_uids;all_uids.add(uid)
            if uid not in wanted:continue
            path=(cp.parent/entry['asset']).resolve();assert path.is_relative_to(ROOT)and digest(path.read_bytes())==entry['sha256']==indexed[uid]['sourceSHA256'];refs.extend([cp,path])
            rows.append(dict(uid=uid,building=forms[uid],entry=entry,path=str(path.relative_to(ROOT)),cataloguePath=str(cp.relative_to(ROOT))))
    assert len(all_uids)==scope['currentNativeActors']==len(inventory['rows']) and {r['uid']for r in rows}==wanted and len(rows)==len(wanted)
    save(out/'native-input.json.gz',dict(rows=rows,currentManifest=dict(path=str(mp.relative_to(ROOT)),sha256=msha)))
    result=dict(uids=sorted(wanted),currentManifestSHA256=msha,currentNativeActors=len(all_uids),sourceGeometryChanges=0,nativeMetadataChanges=0,installationApproved=False,publication=False,qualification='Exact current entries/assets/forms for already installed scoped actors; no old flags, geometry, approvals or catalogue metadata modified. Preview input only, not source or physical reacceptance.')
    save(out/'summary.json',result)
    module('scope_native_input_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unchanged-current-terrain-scope-native-preview-inputs',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
