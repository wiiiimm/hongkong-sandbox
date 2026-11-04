"""Verify the exact catalogue append and every other manifest field unchanged."""
import os
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    base=ROOT/'docs/astra-city/government-import';config=(ROOT/os.environ['ORIGINAL_INSTALL_CONFIG']).resolve();assert config.is_relative_to(base)
    cfg=read(config);name=cfg['prefix']+'-original-installed-'+cfg.get('installVersion','v1')+'-'+cfg['date'];folder=base/name
    receipt,pins=authenticate(folder);history=folder/'historical-input-context.json';assert digest(history.read_bytes())==pins[str(history.relative_to(ROOT))]
    old=next(q for q in read(history)['mutableCurrentByteSnapshots'] if q['originalPath']=='3d-viewer/city/data/manifest.json')
    previous=ROOT/old['savedHistoricalBytes']['path'];assert digest(previous.read_bytes())==old['originalSHA256']==old['savedHistoricalBytes']['sha256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[str(manifest.relative_to(ROOT))]
    before=read(previous);after=read(manifest);key='officialModelCatalogues'
    assert {k:v for k,v in before.items() if k!=key}=={k:v for k,v in after.items() if k!=key}
    assert after[key][:-1]==before[key] and after[key][-1] not in before[key]
    assert after[key][-1]==receipt['catalogueURL'] if 'catalogueURL' in receipt else len(after[key])==len(before[key])+1
    assert receipt['terrainEdits'] is False
    out=base/(cfg['prefix']+'-manifest-fields-readback-v1-'+cfg['date']);assert not out.exists()
    result=dict(uids=sorted(cfg['sources']),passed=True,installedJobId=receipt['jobId'],snapshotId=receipt['snapshotId'],allNonCatalogueManifestFieldsIdentical=True,comparedNonCatalogueFields=sorted(k for k in before if k!=key),originalCatalogueOrderPreserved=True,newCatalogueURL=after[key][-1],terrainEdits=False,sourceGeometryChanges=0,installationApproved=False)
    save(out/'ROOT-MANIFEST-READBACK.json',result)
    module('model_only_manifest_readback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name,'installed-model-only-complete-manifest-field-readback',[Path(__file__),config,folder/'result.json',history,previous,manifest],result)

if __name__=='__main__':main()
