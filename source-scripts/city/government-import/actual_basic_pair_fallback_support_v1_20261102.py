"""Measure an actual current BASIC pair's fallback interface; no original-source approval."""
import argparse,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['batch','supported-capture','support-capture','uid','support']:p.add_argument('--'+key,required=True)
 p.add_argument('--owned',action='store_true');a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;lp=HERE/'local'/(a.batch+'-lease')/'reservation.json'
 assert a.batch.startswith('government-xl-')and'/'not in a.batch and a.uid!=a.support and not out.exists()
 if not a.owned:
  assert not lp.parent.exists();c=reservations.claim('actual-basic-fallback-'+str(uuid.uuid4()),['building:'+a.uid,'building:'+a.support],batch=a.batch,ttl=3600);assert c['ok'],c
  return execute_reserved(c['reservation'],lp,[sys.executable,__file__,*sys.argv[1:],'--owned'])
 lease=read(lp);assert reservations.owns(lease);refs=[Path(__file__)];pins={}
 def basic(batch,uid):
  _,bound=authenticate(base/batch);pins.update(bound);refs.append(base/batch/'result.json');path=base/batch/'basic.json';assert digest(path.read_bytes())==bound[str(path.relative_to(ROOT))];refs.append(path)
  rows=[r for r in read(path)['rows']if r['uid']==uid];assert len(rows)==1;row=rows[0];assert row['currentBuilding']['uid']==uid
  manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==bound[str(manifest.relative_to(ROOT))];refs.append(manifest)
  return row
 target=basic(a.supported_capture,a.uid);support=basic(a.support_capture,a.support)
 geometry=lambda r:dict(position=r['position'],index=r['index'])
 save(out/'mode-inputs.json.gz',dict(rows=[dict(uid=a.uid,supportUid=a.support,supportGeometry=geometry(support),modes=[dict(mode='actual-current-BASIC-fallback',geometry=geometry(target))])],evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in dict.fromkeys(refs)]))
 checker=HERE/'original_four_world_current_basic_support_v1_20261023.mjs'
 with(out/'worker.log').open('w')as log:subprocess.run(['node',str(checker),str(out.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 report=read(out/'mode-checks.json.gz');assert len(report['rows'])==1;proof=report['rows'][0]['proof']
 for name,sha in report['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
 result=dict(uids=[a.uid,a.support],supportedUid=a.uid,supportUid=a.support,currentBasicFallbackSupportPassed=proof['passed'],rawSupportProof=proof,originalSourceSupportApproved=False,geometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Actual unchanged current BASIC render meshes measured with the unchanged canonical support-interface kernel in their one real fallback coordinate stream. No government-source support or geometry approval, thresholds or fabricated four-world claim.')
 save(out/'summary.json',result);refs.append(checker);assert reservations.owns(lease);module('actual_basic_pair_fallback_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'actual-unchanged-BASIC-fallback-pair-interface',list(dict.fromkeys(refs)),result);print(dict(passed=proof['passed'],samples=proof['samples'],strictContacts=proof['strictContacts'],unresolved=len(proof['unresolved'])),flush=True)
if __name__=='__main__':main()
