"""Fence complete original footings and remaining detail diagnostics."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';PREFIX='xl-terrain-recovery-20261009-118230-'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 spec=importlib.util.spec_from_file_location('roof_detail_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 common=[Path(__file__),BASE/(PREFIX+'current-roof-perimeter-role-v1')/'result.json',BASE/(PREFIX+'current-roof-perimeter-role-v1')/'typed-role.json.gz',BASE/(PREFIX+'original-world-current-support-v1')/'result.json',BASE/(PREFIX+'original-world-current-support-v1')/'diagnostic.json.gz']
 row=read(BASE/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009/selection.json.gz')['rows'][0];common.append(ROOT/row['candidate']['path'])
 slices=[('roof-footing-topology-v1',[]),('remaining-details-visual-v1',[]),('original-underside-counterparts-v2',['exact_original_source_surface_contact_band_20261009.py','exact_original_projection_coverage_20261009.py']),('original-entrance-mount-distances-v1',['exact_original_triangle_distance_20261009.py','test_exact_original_triangle_distance_20261009.py','exact_original_shell_intersections_20261009.py'])]
 receipts=[]
 for suffix,helpers in slices:
  batch=PREFIX+suffix;folder=BASE/batch;paths=common+[HERE/(batch+'.py')]+[HERE/h for h in helpers]
  r=module.freeze(batch,'complete-original-remaining-details-diagnostic-only-v1',paths,dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],sourceOnlyDiagnostic=True,currentTypedFootingReceipt=ref(common[1]),originalSourceRootedComponents=438,currentUnresolvedComponents=[330,332,417,418,419,420,444],supportAccepted=False,fullAcceptance=False,currentHeldReason='seven-original-detached-underside-or-entrance-details-remain-unproved; source-specific finite-band rooftop proof positive but not whole-model acceptance',nextStep='Original complete counterpart/enclosure or mounted visual role evidence; preserve all ordinary clearances, original exact noncontacts, current foreign/runtime gates and fixed contact band.'))
  receipts.append(dict(batch=batch,jobId=r['jobId']))
 scope=BASE/'xl-terrain-recovery-20261009-harbourfront-roof-closed-scope-v1';assert not scope.exists();folders=[BASE/(PREFIX+x) for x,_ in slices]+[BASE/(PREFIX+'original-roof-perimeters-v1'),BASE/(PREFIX+'current-roof-perimeter-role-v1')]
 files=[Path(__file__),HERE/'exact_original_segment_surface_contact_band_20261009.py',HERE/'test_exact_original_segment_surface_contact_band_20261009.py',HERE/'original_open_roof_perimeter_band_accounting_20261009.py',HERE/'test_original_open_roof_perimeter_band_accounting_20261009.py',HERE/(PREFIX+'original-roof-perimeters-v1.py'),HERE/(PREFIX+'current-roof-perimeter-role-v1.py')]+[HERE/(PREFIX+x+'.py') for x,_ in slices]+[HERE/h for _,hs in slices for h in hs]+[p for f in folders for p in f.rglob('*') if p.is_file()]
 files=sorted(set(files));save(scope/'closed-scope.json',dict(closedExplicitPaths=[dict(ref(p),bytes=p.stat().st_size) for p in files],closedDocumentDirectories=[str(f.relative_to(ROOT)) for f in folders],neonReceipts=receipts,rawOriginalFailuresPreserved=True,sourceGeometryChanges=0,currentRemainingComponents=[330,332,417,418,419,420,444],fullAcceptance=False,installationApproved=False,activeExcludedPaths=[str(HERE/(PREFIX+'original-underside-counterparts-v1.py'))],qualification='The failed preliminary counterpart-v1 projection-key diagnostic is superseded by v2 and does not grant acceptance. Global historical manifest metadata remain leaf provenance; existing source/current dependencies are pinned by the grade and roof receipts.'))
 print(scope/'closed-scope.json',flush=True)
if __name__=='__main__':main()
