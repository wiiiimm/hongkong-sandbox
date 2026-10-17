"""Close exact dependency metadata work with runtime/Neon/count readbacks."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BATCH='government-xl-all-installed-dependency-metadata-applied-v1-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PLAN=DOC.parent/'government-xl-all-installed-dependency-metadata-proposal-v2-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 result=read(DOC/'result.json');runtime=read(DOC/'runtime-metadata-check.json');count=read(DOC/'full-xl-current-count.json');cs=read(DOC/'full-xl-count-neon-sync.json');progress=read(ROOT/'3d-viewer/city/data/building-progress.json')
 assert result['metadataCorrectionApplied'] and result['newlyInstalled']==0 and result['dependencyChanges']==210 and result['catalogueChanges']==28
 assert not result['nativeReacceptance'] and not result['physicalAccepted'] and not result['installationApproved']
 assert runtime['passed'] and len(runtime['rows'])==254 and {r['uid'] for r in runtime['rows']}==set(result['uids']) and runtime['correctedDependencies']==210
 assert cs['resultVerified'] and read(DOC/'neon-sync.json')['resultVerified']
 assert read(DOC/'tests-before.json')['passed'] and read(DOC/'tests-after.json')['passed']
 assert count['counts']==dict(total=521,installedVerified=221,remaining=300)
 assert progress['totalForms']==346108 and progress['reviewedEnhancedForms']==4501 and progress['government']['enhanced']==4483 and progress['government']['available']==212669
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  status,neoncount=c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(cs['jobId'],)).fetchone();assert status=='complete' and neoncount['count']==count and neoncount['newlyInstalled']==0
 save(DOC/'full-xl-count-neon-result.json',neoncount)
 for a in result['aliases']:assert ref(ROOT/a['archivePath'])['sha256']==a['sha256']
 for r in result['originalActorAssets']+result['currentCatalogueRefs']:assert ref(ROOT/r['path'])==r
 for p,sha in runtime['hashes'].items():assert ref(ROOT/p)['sha256']==sha
 save(DOC/'root-verification.json',dict(metadataCorrectionApplied=True,neonResultVerified=True,fullXLCountNeonVerified=True,currentRuntimeMetadataVerified=True,independentCounterexampleTestsBefore=21,independentCounterexampleTestsAfter=21,sourceGeometryChanges=0,terrainGeometryChanges=0,newlyInstalled=0,fullXLCurrentCounts=count['counts'],wholeMapForms=346108,enhancedForms=4501,governmentEnhanced=4483,aliases=result['aliases'],aiGeometryModelling=False))
 (DOC/'README.md').write_text('Codex, 10 October 2026, HKS-203. Corrected210 stale candidate dependency states between254 unique already installed original government actors across206 owner entries and28 catalogues. Added108 missing exact government CSUIDs; all existing fields, edge directions, source bytes, root placements and installed review states retained. The27 intentional fallback/legacy relations stay unchanged. This is metadata repair, with zero new installation or identity/terrain/native acceptance.\n\nImmutable Neon metadata job '+result['jobId']+' read back exactly. Production parser and actual loader pass for all254 complete assets and210 corrected edges. Actual-catalogue/adversarial tests pass21 before and21 after. Full521 runtime/current-Neon audit retains221 installed and300 remaining; whole map346108 source forms,4501 enhanced (4483 matched government plus18 outside).\n\nOriginal frozen test and all28 old catalogue byte streams archived explicitly. Earlier unfenced producer/apply guard failures are preserved; v2 fixes scope/order bookkeeping only. Manifest unchanged; fresh downstream catalogue captures required. No AI geometry modelling or government mesh changes. XL processing continues.\n')
 paths={str(p.relative_to(ROOT)) for d in [DOC,PLAN] for p in d.rglob('*') if p.is_file()}
 code=['verified_installed_dependency_metadata_20261010.py','test_verified_installed_dependency_metadata_20261010.py','test_verified_installed_dependency_metadata_v2_20261010.py','archived_verified_installed_dependency_metadata_tests_v1_20261010.py','xl-all-installed-dependency-metadata-proposal-v1-20261010.py','xl-all-installed-dependency-metadata-proposal-v2-20261010.py','xl-all-installed-dependency-metadata-apply-v1-20261010.py','xl-all-installed-dependency-metadata-apply-v2-20261010.py','check-all-installed-dependency-metadata-v1-20261010.mjs','check-all-installed-dependency-metadata-v2-20261010.mjs','xl-all-installed-dependency-metadata-close-v1-20261010.py']
 paths.update(str((HERE/n).relative_to(ROOT)) for n in code);paths.update(r['path'] for r in result['currentCatalogueRefs'])
 paths.update(['3d-viewer/city/data/building-progress.json','3d-viewer/scripts/building-progress/review-proof.json','3d-viewer/scripts/building-progress/screening-proof.json','docs/astra-city/landmark-completion-audit/neon-snapshot.json'])
 save(DOC/'declared-scope.json',dict(closedPaths=sorted(paths),aliases=result['aliases'],metadataLeafPaths=[],newlyInstalled=0,modelGeometryChanges=0,qualification='Exact metadata correction with complete archived historical source, production loader and current Neon/count proofs. No numerical metadata evidence waivers.'))
 print(dict(paths=len(paths),counts=count['counts'],metadataApplied=True),flush=True)
if __name__=='__main__':main()
