"""Rebind original overlap evidence after parent metadata change; preserve every geometry value."""
from pathlib import Path
import copy,json
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-apex227942-original-terrain-capture-v3-20261018';BATCH='government-xl-apex227942-overlap-rebind-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def canonical(x):return (json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode()
def main():
 assert not DOC.exists()and not LOCAL.exists();r=read(CAP/'result.json');pins={};refs=[Path(__file__),CAP/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 candidate=read(CAP/'terrain-candidates.json')[0];wrapper=read(ROOT/candidate['path']);child=next(p for p in wrapper['patches']if p.get('meta',{}).get('targetUids')==['landsd/227942:0']);priorpath=HERE/'local/government-xl-apex-nested-current-terrain-20261007/terrain-central-with-sun-yat-sen.json';prior=next(p for p in read(priorpath)['patches']if p.get('meta',{}).get('targetUids')==['landsd/227942:0']);assert child['nativeMesh']==prior['nativeMesh']
 normalized=copy.deepcopy(child);normalized['meta']['parentTerrain']=prior['meta']['parentTerrain'];normalized['meta']['parentSha256']=prior['meta']['parentSha256'];assert normalized==prior
 approval=child['nativeMesh']['sourceOverlap'];oldpath=Path(approval['evidencePath']);assert digest(oldpath.read_bytes())==approval['evidenceSHA256'];audit=read(oldpath);oldraw=copy.deepcopy(prior);oldraw['nativeMesh'].pop('sourceOverlap');assert digest(canonical(oldraw))==audit['stagedGeometrySha256']
 raw=copy.deepcopy(child);raw['nativeMesh'].pop('sourceOverlap');audit['stagedGeometrySha256']=digest(canonical(raw));save(DOC/'native-overlap.json',audit);approval['evidencePath']=str((DOC/'native-overlap.json').relative_to(ROOT));approval['evidenceSHA256']=digest((DOC/'native-overlap.json').read_bytes())
 validator=module('apex_rebound_validate',HERE/'resolve-pass.py');validator.validate_patch(child,wrapper)
 path=LOCAL/'terrain-apex-current-parent.json';save(path,wrapper);candidate.update(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()));save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'rebind-proof.json',dict(priorCandidate=read(CAP/'terrain-candidates.json')[0],newCandidate=candidate,nativeMeshCoordinatesAndIndicesUnchanged=True,onlyParentMetadataAndOverlapReceiptChanged=True,localCanonicalTerrainValidatorPassed=True,fullWrapperValidatorPassed=False,fullAcceptance=False))
 refs.extend([priorpath,oldpath,path,HERE.parent/'island-detail-integration/native_terrain_validation.py',HERE.parent/'island-detail-integration/publish.py']);out=module('apex_rebind_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'apex-exact-original-overlap-parent-metadata-rebind-v1',list(set(refs)),dict(uids=['landsd/227942:0'],geometryChanges=0,localCanonicalTerrainValidatorPassed=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
