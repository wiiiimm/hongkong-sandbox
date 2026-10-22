"""Rebind exact cached source selection to current forms; no acceptance transfer."""
import argparse
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--capture',required=True);p.add_argument('--uid',required=True);a=p.parse_args();assert a.batch.startswith('government-xl-') and '/' not in a.batch
 base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;assert not doc.exists();prior=base/a.capture;_,pins=authenticate(prior);selection=prior/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
 rows=[r for r in read(selection)['rows']if r['uid']==a.uid];assert len(rows)==1;row=rows[0];asset=ROOT/row['candidate']['path'];tile=ROOT/'3d-viewer'/row['source']['tile'];manifest=ROOT/'3d-viewer/city/data/manifest.json'
 assert digest(asset.read_bytes())==row['sourceSHA256']==row['candidate']['entry']['sha256'];assert row['candidate']['entry']['uid']==a.uid;assert [b for b in read(tile)['buildings']if b['uid']==a.uid]==[row['source']['building']];assert row['source']['tile']in {t['url']for t in read(manifest)['tiles']}
 output=doc/'selection.json.gz';save(output,dict(rows=rows,manifestSHA256=digest(manifest.read_bytes())))
 result=dict(uids=[a.uid],sourceSHA256ByUid={a.uid:row['sourceSHA256']},sourceSelectionOnly=True,installationApproved=False,publication=False,newlyInstalled=0,qualification='Exact historical selection/source bytes and current form tuple rebound. Historical terrain, physical, neighbour and publication acceptance do not transfer.')
 refs=[Path(__file__),prior/'result.json',selection,output,asset,tile,manifest];save(doc/'summary.json',result);module('current_source_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'current-exact-original-source-selection',refs,result)
if __name__=='__main__':main()
