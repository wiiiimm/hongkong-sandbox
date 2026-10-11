"""Read-only publication-validator replay of the exact frozen Park final proposal."""
import copy,importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import'
PHYS=BASE/'government-xl-terrain-recovery-park-haven-overlapping-native-parent-original-pair-current-physical-v4-20261010'
BATCH='government-xl-terrain-recovery-park-haven-final-native-validation-v1-20261010';DOC=BASE/BATCH

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def recheck():
 receipt=read(PHYS/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert ref(ROOT/r['path'])==r
 rows=read(PHYS/'terrain-candidates.json');assert len(rows)==1;row=rows[0];path=ROOT/row['path'];assert ref(path)==dict(path=row['path'],sha256=row['sha256']);patch=read(path)
 parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parentpath)
 approval=patch['nativeMesh']['sourceOverlap'];auditpath=ROOT/approval['evidencePath'];assert ref(auditpath)['sha256']==approval['evidenceSHA256'];audit=read(auditpath)
 payload=copy.deepcopy(patch);payload['nativeMesh'].pop('sourceOverlap');canonical=digest((json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n').encode());assert canonical==audit['stagedGeometrySha256']
 validatorpath=HERE.parent/'island-detail-integration/native_terrain_validation.py';module('park_final_native_validation',validatorpath).validate_native_mesh(patch,parent)
 refs=[ref(p) for p in [Path(__file__),PHYS/'result.json',PHYS/'terrain-candidates.json',path,parentpath,auditpath,validatorpath]]+[ref(ROOT/s['path']) for s in audit['source']['files']]
 return dict(contract='park-haven-final-frozen-native-publication-validator-v1',uids=['landsd/246467:0','landsd/320705:0'],validationPassed=True,finalNativePayloadSHA256=canonical,auditedNativePayloadSHA256=audit['stagedGeometrySha256'],independentRays=audit['float32HighestRayAgreement']['samples'],maximumRayError=audit['float32HighestRayAgreement']['maxError'],proposal=ref(path),parent=ref(parentpath),evidenceRefs=refs,proposalMetadataChanges=0,proposalGeometryChanges=0,sourceGeometryChanges=0,publication=False,newlyInstalled=0)

def main():
 assert not DOC.exists();result=recheck();save(DOC/'diagnostic.json',result);f=module('park_validation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f.freeze(BATCH,'final-frozen-native-publication-validator-replay-v1',[ROOT/r['path'] for r in result['evidenceRefs']],result);print(dict(validationPassed=True,proposal=result['proposal']['sha256'],rays=result['independentRays']),flush=True)
if __name__=='__main__':main()
