"""Freeze exact current catalogue bytes for hermetic adversarial tests only."""
from pathlib import Path
import json
from run import ROOT,HERE,read,save,digest
from lippo_current_bound_six_roof_identity_v4_20261011 import DOC as INPUT,module
from lippo_three_original_current_inventory_20261010 import catalogue_inventory
BATCH='government-xl-lippo-current-binding-hermetic-fixtures-v4-20261011';DOC=INPUT.parent/BATCH

def main():
 assert not DOC.exists()
 capture=read(INPUT/'current-inputs.json.gz');manifest=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()
 assert digest(manifest)==capture['manifestSHA256'] and catalogue_inventory(manifest)==capture['catalogueInventory']
 paths=['3d-viewer/city/data/manifest.json']+['3d-viewer/'+p for p in capture['catalogueInventory']['completeCatalogueHashes']]
 raws={p:(ROOT/p).read_bytes() for p in paths}
 save(DOC/'manifest-and-catalogue-bytes.json.gz',dict(rawStrings={p:b.decode() for p,b in raws.items()},hashes={p:digest(b) for p,b in raws.items()},identityAccepted=False,physicalAccepted=False,installationApproved=False))
 assert all((ROOT/p).read_bytes()==b for p,b in raws.items())
 result=module('lippo_hermetic_current_fixture_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'byte-bound-current-catalogue-hermetic-fixture-v4',[Path(__file__),INPUT/'result.json']+[ROOT/p for p in paths],dict(uids=['landsd/231645:0','landsd/233997:0','landsd/239465:0'],manifestSHA256=digest(manifest),identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Exact current bytes frozen for hermetic counterexamples only; separate unmocked production identity replay is mandatory.'))
 print(json.dumps(dict(jobId=result['jobId'],catalogues=len(paths)-1)),flush=True)
if __name__=='__main__':main()
