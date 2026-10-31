"""Source-bound Yoho Block6 original horizontal heading proof; no source or policy edits."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from original_source_ownership import document,graph_reasons
from miami_original_yaw_root_20261009 import frame_measurement
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-next-repairs-yoho-56771-original-yaw-v1-20261024';DOC=BASE/BATCH;ID=BASE/'government-xl-next-repairs-yoho-five-current-identity-v1-20261024';CAP=BASE/'government-xl-next-repairs-yoho-five-inset-runtime-v1-20261024'
def main():
 assert not DOC.exists();receipt=read(ID/'result.json');pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 ip=ID/'56771:0/identity.json';sel=CAP/'selection.json.gz'
 for p in [ip,sel]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 prior=read(ip);assert 'original-unit-hkpd-root-pose' in prior['reasons']
 row=next(r for r in read(sel)['rows'] if r['uid']=='landsd/56771:0');asset=ROOT/row['candidate']['path'];raw=asset.read_bytes()
 assert digest(raw)==row['sourceSHA256']=='f96ce65998446a8de280c071a9e367bfbe58bbc17969857c4fa7dd4acae19a45'
 assert row['modelId']=='B218993350001063C0'
 g=document(raw);t=decode_original_world_triangles(raw);assert len(t)==16022 and graph_reasons(g,row['modelId'],len(t))==['original-unit-hkpd-root-pose']
 root=g['nodes'][g['scenes'][0]['nodes'][0]];frame=frame_measurement(root['matrix'],document(raw)['nodes'][g['scenes'][0]['nodes'][0]]['matrix']);bounds=np.array([t.min((0,1)),t.max((0,1))]);err=float(np.max(np.abs(bounds-np.array(row['native']['model']['worldBounds']))))
 assert frame['passed'] and err<.002
 proof=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],originalRoot=root,legacyIdentityReasons=prior['reasons'],frame=frame,completeNativeBoundsErrorM=err,sourceBoundRootFramePassed=True,remainingIdentityReasons=[r for r in prior['reasons'] if r!='original-unit-hkpd-root-pose'],sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,qualification='Only the fixed-axis root pattern is replaced for these exact bytes by verified unchanged unit horizontal yaw and HKPD up. Exact current identity/georef/projection evidence remains bound; full physical/runtime checks remain required.')
 save(DOC/'proof.json',proof)
 refs=[Path(__file__),ID/'result.json',ip,sel,asset,HERE/'original_source_ownership.py',HERE/'miami_original_yaw_root_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']
 module('yoho56771_yaw_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-bound-unchanged-original-podium-unit-yaw',refs,dict(uids=[row['uid']],proof=proof,installationApproved=False))
 print(dict(sourceBoundRootFramePassed=True,remainingIdentityReasons=[r for r in prior['reasons'] if r!='original-unit-hkpd-root-pose'],boundsError=err,frame=frame),flush=True)
if __name__=='__main__':main()
