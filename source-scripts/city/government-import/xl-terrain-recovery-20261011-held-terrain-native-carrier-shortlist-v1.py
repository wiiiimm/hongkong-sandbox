"""Source-only coarse ranked leads; never contact/identity/current acceptance.

Uses saved full POSITION bounds and cached original assets. A positive box
intersection only nominates a complete exact original interface investigation.
Installed actors and root-owned active actors are excluded. No raw hold clears.
"""
import subprocess,importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-held-terrain-native-carrier-shortlist-v1';DOC=BASE/BATCH
OLD=BASE/'government-xl-current-320-blocker-families-20261009/dispositions.json.gz';INV=BASE/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v5'
EXCLUDED={'landsd/'+str(i)+':0'for i in [255647,255438,118230,278303,233985,240487,231645,233997,239465]}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(INV/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert ref(INV/'inventory.json.gz')in r['evidenceRefs'];inventory=read(INV/'inventory.json.gz');installed={p['uid']for p in inventory['rows']};dispositions=read(OLD);candidates=[p for p in dispositions['rows']if p['uid']not in installed|EXCLUDED and 'terrain-or-foundation'in p['reasonFamilies']and 'identity-or-component-coverage'not in p['reasonFamilies']]
 files=subprocess.check_output(['rg','--files','--no-ignore',str(HERE/'local'),'-g','*.glb.gz'],text=True).splitlines();assets={};wanted={p['sourceSHA256']for p in candidates}
 for p in files:
  path=Path(p);stem=path.name.removesuffix('.glb.gz')
  if stem in wanted and stem not in assets:assets[stem]=path
 rows=[];missing=[];refs=[ref(Path(__file__)),ref(OLD),ref(INV/'result.json'),ref(INV/'inventory.json.gz'),ref(HERE/'exact_packed_world_bounds_v3_20261010.py')]
 for row in candidates:
  p=assets.get(row['sourceSHA256'])
  if p is None:missing.append(row['uid']);continue
  assert digest(p.read_bytes())==row['sourceSHA256'];bounds=packed_world_bounds(p.read_bytes());bb=np.asarray(bounds['originalWholeSourceBounds']);leads=[]
  for native in inventory['rows']:
   nb=np.asarray(native['completeOriginalPOSITIONProof']['originalWholeSourceBounds']);lo=np.maximum(bb[0,[0,2]],nb[0,[0,2]]);hi=np.minimum(bb[1,[0,2]],nb[1,[0,2]]);width=hi-lo
   if np.any(width<0)or nb[0,1]>bb[1,1]:continue
   leads.append(dict(nativeUID=native['uid'],sourceSHA256=native['sourceSHA256'],completeOriginalPOSITIONBounds=native['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],boxIntersectionAreaM2=float(np.prod(width)),nativeTopMinusOwnedBaseM=float(nb[1,1]-bb[0,1]),source=native['source'],catalogue=native['catalogue'],noContactOrSupportingRoleProved=True))
  leads.sort(key=lambda p:(abs(p['nativeTopMinusOwnedBaseM']),-p['boxIntersectionAreaM2']));rows.append(dict(uid=row['uid'],name=row['name'],sourceSHA256=row['sourceSHA256'],source=ref(p),completeOriginalPOSITIONProof=bounds,historicalReasons=row['historicalReasons'],nativeBoxLeads=leads,score=abs(leads[0]['nativeTopMinusOwnedBaseM'])if leads else None));refs.append(ref(p));print(json.dumps(dict(uid=row['uid'],nativeBoxLeads=len(leads),closest=leads[0]['nativeUID']if leads else None)),flush=True)
 rows.sort(key=lambda p:(not bool(p['nativeBoxLeads']),p['score']if p['score']is not None else 1e100,p['uid']));result=dict(uids=[p['uid']for p in rows],rows=rows,missingCachedOriginalAssets=missing,excludedOwnedScopes=sorted(EXCLUDED),frozenBaselineManifest=inventory['currentManifest'],sourceOnly=True,currentAcceptance=False,noFreshCurrentCapture=True,noExactContactOrSupportProved=True,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
 for pin in refs:assert ref(ROOT/pin['path'])==pin
 s=importlib.util.spec_from_file_location('shortlist_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'held-original-full-position-to-installed-native-source-only-box-ranking-v1',[ROOT/p['path']for p in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],sourceOnly=True,currentAcceptance=False,newlyInstalled=0,noExactContactOrSupportProved=True))
if __name__=='__main__':main()
