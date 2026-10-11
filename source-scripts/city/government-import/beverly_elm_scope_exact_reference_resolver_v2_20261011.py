"""DRAFT exact historical-byte resolver and narrowly typed registry prepared-file metadata.
No numerical/source/actor exemption, new mesh, download, current write or acceptance.
Execution requires root review. Preserves failed v1 declaration.
"""
import json,subprocess
from pathlib import Path
from run import ROOT,HERE,read,save,digest
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-beverly-elm-held-source-checkpoint-scope-v1-20261011/declared-scope.json';DOC=B/'government-xl-beverly-elm-exact-reference-resolution-v2-20261011';LOCAL=HERE/'local'/DOC.name
REG=B/'government-xl-beverly-podium233218-70279-original-registry-farpoint-attribution-v1-20261011/diagnostic.json.gz';DIRECTORY=B/'government-xl-beverly-70279-primary-directory-absence-checkpoint-v1-20261011/diagnostic.json.gz'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def main():
 assert not DOC.exists()and not LOCAL.exists();prior=read(PRIOR);assert not prior['declaredReferencesClosed'];registry=read(REG);directory=read(DIRECTORY);unknown=prior['unboundExactReferenceVersions'];contracts=[];allowed=set();refs=[ref(Path(__file__)),ref(PRIOR),ref(REG),ref(DIRECTORY)]
 # Only these four full fixed-run registry snapshots are used for model namespaces,
 # object/CSUID matching and cached directory equality. Their prepared terrain file
 # records are unused metadata: neither body coordinates nor source actor evidence.
 for s in registry['completeFourSheetNativeRegistrySnapshots']:
  p=ROOT/s['snapshot']['path'];assert ref(p)==s['snapshot'];v=read(p);n=v['exactNativeResult'];assert v['sheet']==s['sheet']and v['cacheKey']==s['cacheKey']and v['resultSHA256']==s['resultSHA256'];models=n['models'];names=sorted(m['modelId']for m in models);assert len(names)==len(set(names))==s['completeRegistryModels'];assert not[m for m in models if m['modelId'][1:11]=='3716415011'];assert not[m for m in models if any(x.get('objectId')==70279 and x.get('buildingCSUID')=='3716415011T20080220'for x in m.get('matching',{}).get('officialCandidates',[]))]
  d=next(x for x in directory['allFourRelevantCachedPrimaryProviderDirectories']if x['sheet']==s['sheet']);dp=ROOT/d['cachedProviderDirectorySnapshot']['path'];assert ref(dp)==d['cachedProviderDirectorySnapshot'];provider=read(dp);assert sorted(m['modelId']for m in provider['models'])==names;assert len(names)==d['completeCachedProviderModels']==d['completeNativeModels'];assert d['providerNativeNameSetsEqual']is True
  assert len(n['terrain'])==1;prepared=n['terrain'][0]['preparedFiles'];assert len(prepared)==3
  for entry in prepared:
   assert isinstance(entry['bytes'],int)and entry['bytes']>0;assert len(entry['sha256'])==64;assert entry['path']=='manifest.json'or entry['path'].startswith('TERRAIN(TB)/');allowed.add((str(p.relative_to(ROOT)),entry['path'],entry['sha256']))
  contracts.append(dict(path=str(p.relative_to(ROOT)),documentSHA256=ref(p)['sha256'],boundary=dict(pointer='/exactNativeResult/terrain/0/preparedFiles',canonicalSHA256=canonical(prepared)),namespaceRecomputed=dict(sheet=s['sheet'],modelCount=len(names),completeModelNamesSHA256=canonical(names),exactPrefixHits=0,exactObjectAndCSUIDHits=0,cachedPrimaryNameSetEqual=True),qualification='Only unused provider-relative prepared-terrain file records; snapshot names and all matching object/CSUID evidence remain fully inspected. No actor/source/body/cap/ground/numerical evidence classified as metadata. Bounded cached absence only.'));refs.extend([ref(p),ref(dp)])
 unresolved=[];targets={}
 for x in unknown:
  if (x['origin'],x['path'],x['sha256'])in allowed:continue
  assert '/registry/'not in x['origin'],'Unexpected registry reference cannot be classified';targets.setdefault(x['path'],set()).add(x['sha256'])
 aliases=[]
 # Search exact historical blobs only at the declared original path. A commit is
 # provenance for actual bytes, never authority to substitute a near version.
 for path,wanted in sorted(targets.items()):
  revisions=git('log','--all','--format=%H','--',path).decode().splitlines();seen=set()
  for revision in revisions:
   if not wanted:break
   try:blob=git('rev-parse',revision+':'+path).decode().strip()
   except subprocess.CalledProcessError:continue
   if blob in seen:continue
   seen.add(blob);raw=git('cat-file','blob',blob);h=digest(raw)
   if h not in wanted:continue
   dest=LOCAL/'historical-bytes'/h/Path(path).name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);assert ref(dest)['sha256']==h;aliases.append(dict(originalPath=path,sha256=h,archive=ref(dest),gitRevision=revision,gitBlobId=blob,exactHistoricalBytes=True));refs.append(ref(dest));wanted.remove(h)
  unresolved.extend(dict(path=path,sha256=h)for h in sorted(wanted))
 save(DOC/'resolution.json',dict(sourceOnly=True,currentAcceptance=False,installationApproved=False,failedDeclaration=ref(PRIOR),historicalManifestAliases=aliases,metadataLeafJsonPointers=contracts,newMetadataLeafPaths=[],unresolvedExactVersions=unresolved,resolutionComplete=not unresolved,allRegistryUnknownsExactlyClassified=len(allowed)==12,geometryExemptions=0,qualification='Only exact historical Git blobs and exact four-registry unused prepared-file pointer metadata. No synthesized aliases, provider downloads, actor geometry exemption or installation credit.',evidenceRefs=refs));print(json.dumps(dict(historicalExactAliases=len(aliases),registryPreparedMetadataPointers=len(contracts),unresolved=unresolved,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
