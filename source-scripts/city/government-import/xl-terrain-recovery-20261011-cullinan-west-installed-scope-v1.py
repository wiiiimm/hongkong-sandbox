"""Read-only installed closure draft; execute only after root verified receipt."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';STAGED='government-xl-terrain-recovery-cullinan-west-two-qualified-native-stage-v1-20261011';INSTALLED='government-xl-cullinan-west-two-unchanged-installed-v1-20261011';DOC=BASE/'xl-terrain-recovery-20261011-cullinan-west-installed-scope-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();folder=BASE/INSTALLED;r=read(folder/'result.json');assert r['publication']and r['newlyInstalled']==2 and set(r['installedUids'])=={'landsd/161931:0','landsd/120158:0'}and r['nativeReacceptance']is False
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 source=read(BASE/'xl-terrain-recovery-20261011-cullinan-west-source-stage-scope-v1/declared-scope.json');paths=set(source['closedPaths']);leaves=set(source['metadataLeafPaths']);aliases=list(source['historicalManifestAliases'])
 for d in [folder,BASE/STAGED,HERE/'accepted'/STAGED,HERE/'local'/INSTALLED]:paths.update(str(p.relative_to(ROOT))for p in d.rglob('*')if p.is_file())
 paths.update(str(p.relative_to(ROOT))for p in (ROOT/'3d-viewer/city/data/official-models'/STAGED).rglob('*')if p.is_file());paths.update(str(p.relative_to(ROOT))for p in HERE.glob('xl-cullinan-west-two-unchanged-live-install-*-20261011.py'));paths.add(str(Path(__file__).relative_to(ROOT)))
 for p in [BASE/'xl-terrain-recovery-20261011-cullinan-west-source-stage-scope-v1/declared-scope.json',ROOT/'3d-viewer/city/data/manifest.json',ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json']:paths.add(str(p.relative_to(ROOT)))
 pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json');assert pointer['snapshotId']==r['snapshotId'];paths.add(pointer['inventory'])
 for n in ['3d-viewer/city/data/building-progress.json','3d-viewer/scripts/building-progress/review-proof.json','3d-viewer/scripts/building-progress/screening-proof.json','docs/astra-city/landmark-completion-audit/neon-snapshot.json']:
  paths.add(n);leaves.add(n)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==r['manifest'];raw=manifest.read_bytes();DOC.mkdir();archive=DOC/'historical-installed-manifest.json';archive.write_bytes(raw);paths.add(str(archive.relative_to(ROOT)));leaves.add(str(archive.relative_to(ROOT)))
 old=HERE/'local'/INSTALLED/'manifest-before-installation.json';assert digest(old.read_bytes())=='3a2f56f7980954ff3493aba5e8a015ca79153f81da55bb580e26bf5b2cdb2ee8';leaves.add(str(old.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=ref(old)['sha256'],archive=ref(old)))
 aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(raw),archive=ref(archive)))
 save(DOC/'declared-scope.json',dict(source,closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],metadataLeafPaths=sorted(leaves),historicalManifestAliases=aliases,sourceStageInheritedExactly=True,liveExcluded=False,verifiedInstalledNeonJob=r['jobId'],installedSnapshot=r['snapshotId'],sourceGeometryChanges=0,terrainProposalGeometryChanged=False,qualification='Root installed two unchanged sources after all current and staged/live gates. All numerical/source/ground/kernel/role/native-carrier evidence remains recursively bound. Global progress metadata and exact manifest archives only are metadata leaves. Existing VWalk flag and all legacy negatives remain unchanged; installed dependency state means current native availability, never whole native reacceptance.'))
 print(dict(paths=len(paths),verifiedInstalledNeonJob=r['jobId']),flush=True)
if __name__=='__main__':main()
