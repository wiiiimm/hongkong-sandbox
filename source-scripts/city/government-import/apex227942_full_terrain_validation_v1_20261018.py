"""Run unchanged recursive publication validator on the complete staged regional terrain."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-apex227942-overlap-rebind-v1-20261018';BATCH='government-xl-apex227942-full-terrain-validation-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 candidate=read(PRIOR/'terrain-candidates.json')[0];patch=read(ROOT/candidate['path']);parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath);validator=module('apex_full_terrain_validator',HERE/'resolve-pass.py');error=None
 try:validator.validate_patch(patch,parent)
 except AssertionError as e:error=str(e)
 report=dict(passed=error is None,error=error,children=len(patch['patches']),candidateSHA256=candidate['sha256'],parentSHA256=digest(parentpath.read_bytes()),fullAcceptance=False);save(DOC/'validation.json',report);print(report,flush=True)
 refs.extend([parentpath,ROOT/candidate['path'],HERE/'resolve-pass.py',HERE.parent/'island-detail-integration/native_terrain_validation.py',HERE.parent/'island-detail-integration/publish.py']);out=module('apex_full_validate_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-complete-regional-recursive-terrain-validation-v1',list(set(refs)),dict(uids=['landsd/227942:0'],summary=report,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
