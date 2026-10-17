"""Run existing placement thresholds on the unchanged combined Grand Stanford source."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-stanford-current-placement-metrics-v1-20261015'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PRIOR=ROOT/'docs/astra-city/government-import/government-xl-stanford-current-loader-validation-v1-20261015'
LOCAL=HERE/'local/government-xl-stanford-current-loader-validation-v1-20261015'
def main():
 assert not DOC.exists()
 receipt=read(PRIOR/'result.json');pins={}
 for q in receipt['evidenceRefs']:
  assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 cat=read(LOCAL/'catalogue.json');assert len(cat['models'])==1
 e={**cat['models'][0],'rootTranslation':cat['rootTranslation']};forms=read(LOCAL/'source-forms.json');manifest=ROOT/'3d-viewer/city/data/manifest.json'
 row={'uid':e['uid'],'sourceSHA256':e['sha256'],'candidate':{'entry':e,'path':str((LOCAL/e['asset']).relative_to(ROOT))},'source':forms[e['uid']],'state':'runtime-validated-awaiting-acceptance'}
 DOC.mkdir();save(DOC/'selection.json.gz',{'rows':[row],'manifestSHA256':digest(manifest.read_bytes())})
 rel=lambda p:str(p.relative_to(ROOT))
 cmd=['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(PRIOR/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(DOC/'runtime-geometry.json.gz')]
 with (DOC/'metrics.log').open('w') as log:p=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900)
 save(DOC/'command.json',{'command':cmd,'exitCode':p.returncode});assert p.returncode==0
 report=read(DOC/'metrics.json')
 for path,h in report['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;pins[path]=h
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h
 module('freeze_stanford_metrics',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-original-placement-metrics-private-v5',[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]],{'uids':[e['uid']],'metrics':report['rows'],'fullAcceptance':False,'installed':False})
 print(report['rows'],flush=True)
if __name__=='__main__':main()
