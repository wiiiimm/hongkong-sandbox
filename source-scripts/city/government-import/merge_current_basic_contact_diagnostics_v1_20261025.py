"""Combine exact authenticated current BASIC diagnostics without altering results."""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--contacts',action='append',required=True);a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
 base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists()and len(set(a.contacts))==len(a.contacts)
 refs=[Path(__file__)];rows=[];uids=set();hashes={}
 for name in a.contacts:
  _,pins=authenticate(base/name);refs.append(base/name/'result.json');path=base/name/'checks.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);report=read(path)
  for key,h in report['inputHashes'].items():
   assert key not in hashes or hashes[key]==h;assert digest((ROOT/key).read_bytes())==h;hashes[key]=h;refs.append(ROOT/key)
  for row in report['rows']:assert row['uid']not in uids;uids.add(row['uid']);rows.append(row)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==hashes[str(manifest.relative_to(ROOT))]
 save(out/'checks.json.gz',dict(rows=rows,inputHashes=hashes));result=dict(uids=sorted(uids),inputs=a.contacts,allCanonicalContactPassed=all(r['canonicalContactPassed']for r in rows),physicalAcceptance=False,installationApproved=False,publication=False,sourceGeometryChanges=0)
 save(out/'summary.json',result);module('merged_basic_diagnostic_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'combined-unchanged-current-basic-contact-diagnostics',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
