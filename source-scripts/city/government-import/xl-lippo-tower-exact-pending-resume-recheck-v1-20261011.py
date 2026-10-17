"""Read-only recheck of existing stage-v2 under exact captured pending phase.
No staging, review writes, reseeding or live publication can run in this module.
"""
import importlib.util,json,os,subprocess,sys,shutil,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from dependency_preflight import from_catalogues
import lippo_tower_current_basic_complete_role_current_bound_v4_20261011 as bound
BATCH='government-xl-lippo-tower-current-basic-unchanged-stage-v2-20261011';DOC=bound.BASE/BATCH;STAGE=HERE/'accepted'/BATCH
LEASE=HERE/'local'/BATCH/'install-reservation.json';ROLE=bound.BASE/'government-xl-lippo-tower-only-current-complete-role-acceptance-v3-20261011'
BROWSER=HERE/'xl-lippo-current-basic-solid-browser-v1-20261011.mjs';UID='landsd/239465:0';CARRIER='landsd/231645:0';RETAINED=['landsd/21915:0']
def ref(p):return dict(path=str(Path(p).relative_to(ROOT)),sha256=digest(Path(p).read_bytes()))
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def recheck(local):
 receipt=read(ROLE/'result.json');bound.receipt_pins(receipt)
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 role,entry=bound.verify_files(local,pending_attempt=bound.PENDING_CONTEXT)
 saved=read(ROLE/'acceptance.json')
 # Additional separately executed support/budget/loader fields are pinned by
 # the receipt; the whole mathematical/current role must replay exactly.
 assert {k:saved[k] for k in role}==role and role['reasons']==[] and role['scriptChecksPassed'] and role['acceptanceReadyForStaging']
 assert role['installationApproved'] is False and role['wholeBasicReaccepted'] is False and role['originalGovernmentPodiumUsedAsRuntimeSupport'] is False
 assert entry==read(ROLE/'staged-entry.json')
 report=read(ROLE/'production-support-budget-loader.json');assert report['checksPassed']==19 and report['ordinaryBudgetLimitsUnchanged'] and report['currentManifest']==role['currentManifest']
 return role,entry
def retained_snapshot():
 result={}
 for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid'] in RETAINED:
    assert e['uid'] not in result;asset=p.parent/e['asset'];assert digest(asset.read_bytes())==e['sha256'];result[e['uid']]=dict(entry=e,asset=ref(asset),catalogue=ref(p))
 assert set(result)==set(RETAINED);return result
