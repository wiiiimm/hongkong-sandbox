"""Close the metadata-only correction with real runtime/Neon/count readbacks."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BATCH='government-xl-retained-installed-dependency-metadata-applied-v1-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PLAN=DOC.parent/'government-xl-one-peking-retained-installed-dependency-metadata-plan-v2-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 result=read(DOC/'result.json');sync=read(DOC/'neon-sync.json');runtime=read(DOC/'runtime-metadata-check.json');count=read(DOC/'full-xl-current-count.json');cs=read(DOC/'full-xl-count-neon-sync.json');progress=read(ROOT/'3d-viewer/city/data/building-progress.json')
 assert result['metadataCorrectionApplied'] and result['newlyInstalled']==0 and not result['nativeReacceptance'] and not result['physicalAccepted']
 assert sync['resultVerified'] and sync['jobId']==result['jobId'] and cs['resultVerified']
 assert runtime['passed'] and len(runtime['rows'])==4 and {r['uid'] for r in runtime['rows']}==set(result['uids'])
 assert count['counts']==dict(total=521,installedVerified=221,remaining=300)
 assert progress['totalForms']==346108 and progress['reviewedEnhancedForms']==4501 and progress['government']['enhanced']==4483 and progress['government']['available']==212669
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
  status,neoncount=c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(cs['jobId'],)).fetchone();assert status=='complete' and neoncount['count']==count and neoncount['newlyInstalled']==0
 save(DOC/'full-xl-count-neon-result.json',neoncount)
 for alias in result['aliases']:assert ref(ROOT/alias['archivePath'])['sha256']==alias['sha256']
 for r in result['originalActorAssets']+result['currentCatalogueRefs']:assert ref(ROOT/r['path'])==r
 for path,sha in runtime['hashes'].items():assert ref(ROOT/path)['sha256']==sha
 save(DOC/'root-verification.json',dict(metadataCorrectionApplied=True,neonResultVerified=True,fullXLCountNeonVerified=True,currentRuntimeMetadataVerified=True,independentCounterexampleTestsBefore=22,independentCounterexampleTestsAfter=22,sourceGeometryChanges=0,terrainGeometryChanges=0,newlyInstalled=0,fullXLCurrentCounts=count['counts'],wholeMapForms=346108,enhancedForms=4501,governmentEnhanced=4483,aiGeometryModelling=False,aliases=result['aliases']))
 (DOC/'README.md').write_text('Codex, 10 October 2026, HKS-203. Two stale dependency records corrected. Already installed263590→232907 and268032→101781 now have installed state and exact current government CSUID; only the former needed its missing CSUID added. All four original asset bytes, full world geometry/attribute streams, placement/source flags and current Neon installed reviews remain unchanged. No new model installation or retained-native reacceptance.\n\nImmutable metadata job '+result['jobId']+' and all521 current XL runtime/Neon count audit read back exactly. Production catalogue parser and actual loader pass for all four assets; unchanged strict dependency guard passes. Hermetic actual-source/counterexample tests pass22 before and22 after. Complete old catalogue bytes and original historical test source are archived with explicit old-path/SHA aliases; historical negative proofs remain intact. Fresh downstream catalogue bindings are required even though the manifest SHA remains unchanged.\n\nCurrent XL521 =221 installed +300 remaining; whole map346108 forms4501 enhanced, matched government4483/212669 plus18 outside. All goal processing continues. No AI geometry modelling or source/terrain geometry edits.\n')
 paths={str(p.relative_to(ROOT)) for d in [DOC,PLAN] for p in d.rglob('*') if p.is_file()}
 code=['xl-retained-installed-dependency-metadata-apply-v1-20261010.py','check-retained-installed-dependency-metadata-v1-20261010.mjs','xl-retained-installed-dependency-metadata-close-v1-20261010.py','retained_installed_dependency_metadata_plan_20261010.py','test_retained_installed_dependency_metadata_plan_20261010.py','test_retained_installed_dependency_metadata_plan_v2_20261010.py','archived_retained_installed_dependency_pre_correction_tests_20261010.py','xl-one-peking-retained-installed-dependency-metadata-plan-v1-20261010.py','xl-one-peking-retained-installed-dependency-metadata-plan-v2-20261010.py']
 paths.update(str((HERE/n).relative_to(ROOT)) for n in code)
 paths.update(r['path'] for r in result['currentCatalogueRefs'])
 paths.update(['3d-viewer/city/data/building-progress.json','3d-viewer/scripts/building-progress/review-proof.json','3d-viewer/scripts/building-progress/screening-proof.json','docs/astra-city/landmark-completion-audit/neon-snapshot.json'])
 save(DOC/'declared-scope.json',dict(closedPaths=sorted(paths),aliases=result['aliases'],newlyInstalled=0,modelGeometryChanges=0,metadataLeafPaths=[],qualification='Two exact metadata corrections and complete independent source/runtime/Neon/count readbacks. No numerical source/role/current-terrain metadata boundaries or implicit proof waiver. Every historical reference must replay from exact archive or Git bytes.'))
 print(dict(paths=len(paths),counts=count['counts'],metadataApplied=True),flush=True)
if __name__=='__main__':main()
