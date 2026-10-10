"""Exact rational source/literal interface exposure; retains prior whole-face failures."""
import importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_original_rational_interface_segment_clearance_20261011 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-cullinan-west-current-carrier-interface-exposure-v1';DOC=BASE/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261010-cullinan-west-current-carrier-chain-finite-v3';PROBE=BASE/'government-xl-terrain-recovery-cullinan-west-three-complete-original-current-probe-v2-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();prior=read(PRIOR/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for r in prior['evidenceRefs']:assert ref(ROOT/r['path'])==r
 runtimepath=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';ground=np.asarray(read(runtimepath)['rows'][0]['drawnGroundGeometry']).reshape(-1,3,3);d=read(PRIOR/'diagnostic.json.gz');rows=[]
 for mode in d['rows']:
  proofs=[]
  for contact in mode['interfaces']:
   assert len(contact['exactIntersectionPoints'])==2 and contact['positiveDimensionOriginalContact'];proof=verify(contact['exactIntersectionPoints'],ground);proofs.append(dict(originalContact=contact,completeExactRationalInterfaceExposure=proof));print(dict(mode=mode['mode'],components=contact['components'],wholePositiveInterfaceStrictlyExposed=proof['strictlyExposedWholePositiveInterface'],exactMinimumGapM=proof['exactMinimumGapM']),flush=True)
  rows.append(dict(mode=mode['mode'],interfaces=proofs,allWholePositiveInterfacesStrictlyExposed=all(p['completeExactRationalInterfaceExposure']['strictlyExposedWholePositiveInterface']for p in proofs),priorFullFaceNegativesPreserved=mode['faceProofs']))
 refs=[ref(p)for p in [Path(__file__),PRIOR/'diagnostic.json.gz',PRIOR/'result.json',runtimepath,HERE/'exact_original_rational_interface_segment_clearance_20261011.py',HERE/'test_exact_original_rational_interface_segment_clearance_20261011.py']]
 result=dict(uids=d['uids'],rows=rows,priorCarrierCapsAndActualRootReceipts=ref(PRIOR/'diagnostic.json.gz'),noRoundedIntersectionCoordinates=True,wholeNativeNegativesPreserved=True,nativeReacceptance=False,diagnosticOnly=True,fullAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'bounded-exact-rational-original-literal-native-interface-current-finite-exposure-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=d['uids'],allWholePositiveInterfacesStrictlyExposed=all(r['allWholePositiveInterfacesStrictlyExposed']for r in rows),nativeReacceptance=False,fullAcceptance=False))
if __name__=='__main__':main()
