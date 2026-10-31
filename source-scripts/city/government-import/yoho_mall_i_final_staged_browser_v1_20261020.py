"""Recheck final publication metadata privately, one viewport per existing harness call."""
from pathlib import Path
import os,subprocess
from run import ROOT,HERE,read,save
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-final-staged-browser-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
cfg=read(HERE/'accepted/government-xl-yoho-mall-i-qualified-publication-plan-v1-20261020/browser-config.json')
for width in [390,1280]:
 p=LOCAL/f'config-{width}.json';save(p,{**cfg,'viewportWidths':[width],'doc':str((DOC/str(width)).relative_to(ROOT))+'/'})
 r=subprocess.run(['node',str(HERE/'yoho_mall_i_settled_joint_browser_v1_20261020.mjs'),'staged',str(p.relative_to(ROOT))],cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'},timeout=1200)
 assert r.returncode==0
 report=read(DOC/str(width)/'staged-browser.json');assert report['passed']and not report['errors']
print('Both final catalogue viewport checks passed',flush=True)
