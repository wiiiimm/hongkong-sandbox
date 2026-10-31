"""Bind an already validated retained candidate to the runtime adapter's scope contract."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--prior',required=True);a=ap.parse_args();assert a.batch.startswith('government-xl-')and'/'not in a.batch
 base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists();prior=base/a.prior;r,pins=authenticate(prior)
 for name,sha in pins.items():assert digest((ROOT/name).read_bytes())==sha
 assert r['status']=='private-terrain-validator-passed';path=ROOT/r['candidate']['path'];assert digest(path.read_bytes())==r['candidate']['sha256'];patch=read(path);rootpath=ROOT/'3d-viewer/city/data/terrain.json';builder=module('scoped_boundary_builder',HERE/'resolve_pass_indexed_parent_clipping_v2.py');scope=doc/'scope.json';save(scope,dict(uids=r['uids'],cells=patch['coarseCells'],bounds=builder.extent(patch['coarseCells'],read(rootpath))))
 result=dict(uids=r['uids'],status=r['status'],candidate=r['candidate'],scopeReceiptOnly=True,newlyInstalled=0,installationApproved=False,retainedUids=r['retainedUids'])
 refs=[Path(__file__),prior/'result.json',prior/'summary.json',rootpath,scope,HERE/'resolve_pass_indexed_parent_clipping_v2.py',*[ROOT/n for n in pins]];save(doc/'summary.json',result);module('scoped_boundary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'retained-boundary-scoped-receipt',refs,result)
if __name__=='__main__':main()
