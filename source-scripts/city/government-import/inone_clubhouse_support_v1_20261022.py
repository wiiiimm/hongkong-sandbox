"""Existing original-source interface check for recovered clubhouse and podium."""
import sys,subprocess,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-inone-clubhouse-support-v1-20261022';DOC=BASE/BATCH

def main():
 assert not DOC.exists();prior=BASE/'government-xl-inone-adjoining-identity-v2-20261022';_,pins=authenticate(prior);p=prior/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];rows=read(p)['rows'];assert {r['uid']for r in rows}=={'landsd/277973:0','landsd/277974:0'}
 refs=[Path(__file__),p,prior/'result.json',Path(shape_prepare.__file__)]
 for row in rows:
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);row['candidate']['entry']=shape_prepare.entry({**row['native'],'sheet':'11-NW-25B'},row['source']['building'])
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+r['uid']for r in rows],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  save(DOC/'support-inputs.json',dict(sources=rows,pairs=[dict(uid='landsd/277974:0',supportUid='landsd/277973:0')]))
  subprocess.run(['node',str(HERE/'original-support-closure-interfaces.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
  checks=read(DOC/'support-checks.json.gz')
  for path,h in checks['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
  assert reservations.owns(lease)
  module('club_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-clubhouse-podium-interface',refs,dict(uids=[r['uid']for r in rows],rows=checks['rows'],installationApproved=False,qualification='Source interface check only; podium identity, complete terrain foundations and runtime acceptance remain independent.'))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
