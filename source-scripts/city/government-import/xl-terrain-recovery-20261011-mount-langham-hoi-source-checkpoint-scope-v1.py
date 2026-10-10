"""Additive closed SOURCE-ONLY evidence; no new numerical metadata exemptions."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-langham-hoi-source-checkpoint-scope-v1';DOC=BASE/BATCH
OLD=BASE/'xl-terrain-recovery-20261011-langham-hoi-source-checkpoint-scope-v2/declared-scope.json'
ADDITIONS=(
 'xl-terrain-recovery-20261011-langham-fourteen-unchanged-method-disposition-v1',
 'xl-terrain-recovery-20261011-mount-verdant-two-original-complete-interfaces-v1',
 'xl-terrain-recovery-20261011-mount-verdant-complete-original-edge-contact-graph-v1',
 'government-xl-terrain-recovery-mount-verdant-two-original-current-probe-v1-20261011',
 'xl-terrain-recovery-20261011-mount-verdant-podium-authentic-tin-finite-v1',
 'xl-terrain-recovery-20261011-mount-verdant-podium-authentic-tin-paired-refinement-v1',
 'xl-terrain-recovery-20261011-mount-verdant-podium-grade-cap-lower-loops-v2',
 'xl-terrain-recovery-20261011-mount-verdant-two-details-complete-finite-hosts-v1',
 'xl-terrain-recovery-20261011-mount-verdant-two-details-finite-host-edge-facets-v1',
 'xl-terrain-recovery-20261011-mount-verdant-two-details-piecewise-finite-host-edge-facets-v1',
 'xl-terrain-recovery-20261011-mount-verdant-specific-back-attachments-v1',
 'xl-terrain-recovery-20261011-mount-verdant-specific-back-attachments-v2',
 'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1',
 'xl-terrain-recovery-20261011-mount-verdant-four-stream-back-visual-proposals-v1',
 'xl-terrain-recovery-20261011-mount-verdant-podium-current-inputs-v1',
 'government-xl-terrain-recovery-mount-verdant-podium-authentic-current-v1-20261011',
 'xl-terrain-recovery-20261011-mount-verdant-podium-current-four-stream-finite-v1',
 'xl-terrain-recovery-20261011-mount-verdant-podium-current-paired-refinement-v1',
 'xl-terrain-recovery-20261011-hoi-shing-nine-upward-exact-terrain-feasibility-v2')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(OLD);assert old['sourceOnly']and not old['newMetadataLeaves'];paths=set(old['closedExplicitPaths']);paths.update([str(OLD.relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]);receipts=list(old['completedFencedSourceReceipts'])
 for batch in ADDITIONS:
  folder=BASE/batch;r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  # All explicit numeric-producing inputs remain recursive, including failures.
  for p in r['evidenceRefs']:
   assert (ROOT/p['path']).is_file(),p['path'];paths.add(p['path'])
  paths.update(str(p.relative_to(ROOT))for p in folder.rglob('*')if p.is_file());receipts.append(dict(batch=batch,receipt=ref(folder/'result.json'),jobId=r['jobId']))
 extra=['mount_verdant_original_two_back_mounted_visual_proposals_v1_20261011.py','test_mount_verdant_original_two_back_mounted_visual_proposals_v1_20261011.py','exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011.py','test_exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011.py','xl-terrain-recovery-20261011-mount-verdant-podium-grade-cap-lower-loops-v1.py']
 paths.update(str((HERE/n).relative_to(ROOT))for n in extra)
 DOC.mkdir();archive=DOC/'historical-current-manifest.json';original=BASE/'government-xl-terrain-recovery-mount-verdant-podium-authentic-current-v1-20261011/historical-current-manifest.json';archive.write_bytes(original.read_bytes());assert digest(archive.read_bytes())=='4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285';paths.add(str(archive.relative_to(ROOT)))
 aliases=list(old['historicalManifestAliases']);aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(archive.read_bytes()),archive=ref(archive)))
 readme=DOC/'README.md';readme.write_text('''# Mount Verdant / Langham / Hoi Shing source checkpoint\n\nZero installations or current-role acceptance. Original government building bytes, roots and poses remain unchanged. Every numeric source, actual geometry, candidate terrain, failed diagnostic and exact helper remains recursively bound; inherited metadata boundaries are unchanged. The exact archived current baseline is 4a6756…, superseded publications cannot make these facts fresh current acceptance.\n\nMount Verdant retains its complete tower14938/podium641 originals. The podium has a576-face genuine body, four attached10-face bodies, two detached visual details (10 and12 faces), and three exact non-rendering faces. All72 grade-crossing walls have source-only cap paths;183 authentic-TIN grade interfaces exist. Complete original/literal/two explicit F32 back-opening/back-side associations support conditional visual proposals only. P-only current identity passes and the fresh candidate loader/runtime/whole foundation pass, with13 complete current forms and no native overlap. The government original-TIN terrain candidate changes the former terrain; this is an explicit candidate proposal, never unchanged-terrain credit. Its foreign BASIC tower261717 retains a genuine terrain-gap warning. All645 sampled tower-floor points are covered by the original podium, but only6 strict contacts; gap−3.61000061..+.33999634m fails existing support. No neighbour exemption or installation is granted. Complete641-facet four-stream proof retains72 real wall failures and zero up/down failures after exact paired refinement. The tower's207 detached original components remain independently unresolved.\n\nLangham's14 complete details/54 faces are held under the completed unchanged-source mounting methods. All source/current finite successes and full865-host plus five-new-host negatives remain; this is not permanent corruption or an AI-remodelling requirement. Revisit with independently proved actual source mounting/roles, a new complete fixed-band certificate or an authenticated source revision.\n\nHoi Shing preserves every original9 upward failure beside the separately mapped stair/path context. Source-only feasibility nominates17 original terrain vertices (116 duplicate records), maximum downward correction0.5839543343m, and exactly certifies all949 finite-column constraints after Float32 Y packing under the explicit hypothetical≤.65m correction cap. Original government TIN is untouched and no terrain asset is emitted. This describes altered-terrain feasibility only. Whole72/P/T/current/foreign/seams/runtime/root proof and reviewed actual terrain construction are mandatory before promotion. Initial missing-solver import failure is preserved; pinned scipy merely nominates values and exact Fraction replay decides feasibility.\n\nRoot owns independent review, Git and publication.\n''');paths.add(str(readme.relative_to(ROOT)))
 out=dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],historicalManifestAliases=aliases,metadataLeafPaths=old['metadataLeafPaths'],metadataLeafJsonPointers=old['metadataLeafJsonPointers'],completedFencedSourceReceipts=receipts,inheritedMetadataScope=old['inheritedMetadataScope'],immutablePriorScope=ref(OLD),additiveCompletedSlices=list(ADDITIONS),fullNumericalSourceClosureRequired=True,newMetadataLeaves=False,newMetadataPointerContract=False,oneNewByteExactHistoricalGlobalManifestAlias=ref(archive),sourceGeometryChanges=0,sourceOnly=True,currentAcceptance=False,stageAndLiveExcluded=True,newlyInstalled=0)
 assert out['metadataLeafPaths']==old['metadataLeafPaths']and out['metadataLeafJsonPointers']==old['metadataLeafJsonPointers'];save(DOC/'declared-scope.json',out);print(dict(paths=len(paths),completedFencedReceipts=len(receipts),newNumericLeaves=False),flush=True)
if __name__=='__main__':main()
