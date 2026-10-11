"""Declare complete HKDI B current source/physics/roots/caps and all raw negatives.

No numerical dependency is made archival. Root closes every transitive reference
before any browser or publication; frozen old global manifest bytes are explicit.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
BASE=ROOT/'docs/astra-city/government-import';OUT=BASE/'xl-terrain-recovery-20261010-hkdi-block-b-source-scope-declaration-v1';ROLE=BASE/'government-xl-terrain-recovery-hkdi-block-b-current-qualified-native-role-v3-20261010'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();typed=read(ROLE/'typed-role.json.gz');result=read(ROLE/'result.json');assert typed['currentTypedPhysicalAccepted']is True and typed['currentNativeWholeLandmarkAccepted']is False and typed['currentNativeReacceptance']is False and typed['completeOriginalFaces']==11593 and typed['completeOriginalComponents']==345
 with connect() as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 dirs=[d for d in BASE.glob('*hkdi*20261010*')if d.is_dir() and not any(x in d.name for x in ['stage','installed','scope-declaration'])]
 paths={str(p.relative_to(ROOT))for d in dirs for p in d.rglob('*')if p.is_file()}
 files={p for pattern in ['*hkdi*20261010*']for p in HERE.glob(pattern)if p.is_file()and not any(x in p.name for x in ['stage-install','live-install','scope-declaration'])};files.add(Path(__file__));paths.update(str(p.relative_to(ROOT))for p in files)
 old=read(BASE/'xl-terrain-recovery-20261010-park-haven-source-scope-declaration-v3/declared-scope.json');aliases=list(old['historicalManifestAliases']);leaves=set(old['metadataLeafPaths'])
 raw=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()
 if digest(raw)!=typed['currentManifest']['sha256']:
  matches=[x for x in aliases if x['sha256']==typed['currentManifest']['sha256']];assert matches,'Exact pre-publication archive required';raw=(ROOT/matches[0]['archive']['path']).read_bytes()
 assert digest(raw)==typed['currentManifest']['sha256'];OUT.mkdir();archive=OUT/'acceptance-manifest.json';archive.write_bytes(raw);paths.add(str(archive.relative_to(ROOT)));leaves.add(str(archive.relative_to(ROOT)));aliases.append(dict(originalPath='3d-viewer/city/data/manifest.json',sha256=digest(raw),archive=ref(archive)))
 manifest=read(archive);leaves.update('3d-viewer/'+u for u in manifest['officialModelCatalogues']);leaves.update('3d-viewer/'+e['url']for e in manifest['terrainPatches'])
 save(OUT/'declared-scope.json',dict(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p)for p in sorted(paths)],historicalManifestAliases=aliases,metadataLeafPaths=sorted(leaves),metadataLeafJsonPointers=[],currentRoleNeon=result['jobId'],sourceGeometryChanges=0,terrainProposalChanged=False,stageAndLiveExcluded=True,qualification='Complete11593original/literal ownedBfaces and345parts via346 exact positive-dimensional original+actual attachments, strict native144 actualgroundroot and native131 strictlyclear9caps. Full3965native retained,61raw affectedfaces/46remainingclearance/27unrootedparts preserved; no nativewholelandmarkreacceptance. UninstalledA/ramp128/failed147155 roots never bridge. Fullcurrent2forms/provider/source/native/wholefoundation/runtime and all rawfailures recursive. Declared source closure must pass unchanged independent verifier before any installation; no new numerical archival exception.'))
 print(dict(paths=len(paths),currentRoleNeon=result['jobId']),flush=True)
if __name__=='__main__':main()
