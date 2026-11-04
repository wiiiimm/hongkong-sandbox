"""Read-only actual complete renderer streams/matrices, not physical approval."""
import importlib.util,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-owned-actual-render-capture-v1';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-parkview-block11-authentic-retained-current-physical-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(PHYSICAL/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selection=read(PHYSICAL/'selection.json.gz');assert len(selection['rows'])==1;row=selection['rows'][0];assert row['uid']=='landsd/255647:0'
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert selection['manifestSHA256']==ref(manifest)['sha256'];current=read(manifest)
 refs=[ref(p)for p in [Path(__file__),PHYSICAL/'result.json',PHYSICAL/'selection.json.gz',PHYSICAL/'identity-proofs.json',ROOT/row['candidate']['path'],ROOT/'3d-viewer'/row['source']['tile'],HERE/'xl-terrain-recovery-20261011-parkview-owned-actual-render-attributes-v1.mjs',HERE/'actual_float32_model_matrix_bounds_20261011.mjs',HERE/'test_actual_float32_model_matrix_bounds_20261011.mjs']]
 save(DOC/'literal-source-inputs.json.gz',dict(rows=[dict(uid=row['uid'],path=row['candidate']['path'],entry=row['candidate']['entry'],building=row['source']['building'])],currentManifest=ref(manifest),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in current['officialModelCatalogues']],evidenceRefs=refs))
 output=DOC/'actual-render-geometry.json.gz';subprocess.run(['node',str(HERE/'xl-terrain-recovery-20261011-parkview-owned-actual-render-attributes-v1.mjs'),str((DOC/'literal-source-inputs.json.gz').relative_to(ROOT)),str(output.relative_to(ROOT))],cwd=ROOT,check=True)
 r=read(output);refs.extend(dict(path=p,sha256=h)for p,h in r['inputHashes'].items());refs.extend([ref(output),ref(DOC/'literal-source-inputs.json.gz')]);refs=list({r['path']:r for r in refs}.values())
 for x in refs:assert ref(ROOT/x['path'])==x
 s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-parkview-owned-actual-renderer-all-POSITION-attributes-model-matrices-f32-orders-v1',[ROOT/x['path']for x in refs],dict(uids=[row['uid']],completeOriginalFaces=10679,sourceSHA256=row['sourceSHA256'],currentManifest=ref(manifest),actualAttributesMatricesCaptured=True,explicitArithmeticNotUniversalGPUCameraGuarantee=True,currentAcceptance=False,fullAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
