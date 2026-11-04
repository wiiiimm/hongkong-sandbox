"""Compare existing fallback interfaces with captured original-source contacts."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-namcheong244683-baseline-contacts-v1-20261017';DOC=BASE/BATCH;CAP=BASE/'government-xl-namcheong244683-baseline-geometry-v1-20261017/geometry.json.gz';AFTER=BASE/'government-xl-namcheong244683-neighbour-contacts-v1-20261017'
def main():
 assert not DOC.exists();capture=read(CAP);r=read(AFTER/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins=dict(capture['inputHashes'])
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 own=next(r for r in capture['rows']if r['uid']=='landsd/244683:0');tri=lambda r:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];a=tri(own);results=[]
 for f in capture['rows']:
  if f['uid']==own['uid']:continue
  b=tri(f);before=exact_finite_contacts(a,list(range(len(a))),b,list(range(len(b))));assert before['allPairsExamined'];p=AFTER/(f['uid'].replace('/','-').replace(':','-')+'.json.gz');after=read(p)['contacts'];cs=before['contacts'];ac=after['contacts'];summary=dict(uid=f['uid'],baselineContacts=len(cs),originalContacts=len(ac),baselineHeightRange=[min(c['bounds'][0][1]for c in cs),max(c['bounds'][1][1]for c in cs)]if cs else None,originalHeightRange=[min(c['bounds'][0][1]for c in ac),max(c['bounds'][1][1]for c in ac)]if ac else None,existingInterfacePresent=bool(cs),fullAcceptance=False);results.append(summary);save(DOC/p.name,dict(before=before,afterReference=str(p.relative_to(ROOT)),summary=summary));print(summary,flush=True)
 save(DOC/'summary.json',dict(rows=results,fullAcceptance=False,qualification='Existing surface interaction is context only: counts/height ranges do not prove unchanged volume or architectural ownership. No suppression or geometry modification.'))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 result=module('yoho_baseline_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'namcheong244683-current-baseline-interface-comparison-v1',[Path(__file__),CAP,AFTER/'result.json',HERE/'namcheong244683_baseline_geometry_v1_20261017.mjs',HERE/'exact_original_finite_triangle_contacts_20261010.py',*[ROOT/p for p in pins]],dict(uids=[own['uid']],fullAcceptance=False,newlyInstalled=0));print(result['jobId'],flush=True)
if __name__=='__main__':main()
