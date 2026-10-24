"""Fill absent recorded-source metadata from the exact current form; no geometry edits."""
from copy import deepcopy
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';prefix='government-xl-next-repairs-west-kowloon-bus-';prior=base/(prefix+'six-original-selection-v1-20261024');_,pins=authenticate(prior);p=prior/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];selected=deepcopy(read(p));assert len(selected['rows'])==6;refs=[Path(__file__),prior/'result.json',p];changes=[]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    for row in selected['rows']:
        f=row['source']['building'];tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==row['uid'])==f;refs.append(tile);entry=row['candidate']['entry'];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==entry['sha256']==row['sourceSHA256'];refs.append(asset)
        for key,field in [('recordedBaseHeight','baseHeightHKPD'),('recordedTopHeight','topHeightHKPD')]:
            if key in entry:assert entry[key]==f.get(field)
            else:
                assert row['uid']=='landsd/37934:0';entry[key]=f.get(field);changes.append(dict(uid=row['uid'],field=key,old='absent',new=entry[key]))
    assert len(changes)==2
    batch=prefix+'six-original-selection-v2-20261024';out=base/batch;assert not out.exists();save(out/'selection.json.gz',selected)
    result=dict(uids=[r['uid']for r in selected['rows']],changes=changes,sourceGeometryChanges=0,sourcePoseChanges=0,recordedSourceValuesChanged=False,loaderGuardChanged=False,installationApproved=False,publication=False,qualification='Prior appended candidate omitted required recordedBaseHeight/recordedTopHeight keys. Populate only absent fields from the exact unchanged current official form (14.7/20.4). Original asset remains at its government-authored world coordinates; no source/base/pose correction or runtime guard relaxation. Prior failed capture retained.')
    save(out/'summary.json',result);module('west_six_recorded_bindings_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'absent-exact-recorded-form-metadata-binding',refs,result)

if __name__=='__main__':main()
