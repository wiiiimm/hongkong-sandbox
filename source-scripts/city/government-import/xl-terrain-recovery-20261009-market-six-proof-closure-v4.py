"""Separate present byte/git verified dependencies from unavailable old archive metadata."""
from pathlib import Path
import json,subprocess
from run import ROOT,HERE,read,save,digest
BATCH='xl-terrain-recovery-20261009-market-six-proof-closure-v4';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PRIOR=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-proof-closure-v3/closure.json'
TARGET='source-scripts/city/assembly-support-review/native-terrain-extra/staged/11-NE-25A/TERRAIN(TB)/T43500186000106E10/T43500186000106E10-geometry.gltf'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();old=read(PRIOR);present=[];gitbound=[];unavailable=[];aliases=[]
 critical=read(ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-current-role-v10/typed-role.json.gz')['evidenceRefs'];critical_keys={(r['path'],r['sha256']) for r in critical}
 for r in old['transitiveVerifiedDependencies']:
  original=r['path'];path='3d-viewer/'+original if original.startswith('city/') else original;p=ROOT/path
  if p.exists() and digest(p.read_bytes())==r['sha256']:
   present.append({**r,'path':path,'historicalOnly':False,'verification':'actual-file-bytes'})
   if path!=original:aliases.append(dict(historicalPath=original,actualVerifiedPath=path,sha256=r['sha256']))
  elif r.get('verifiedHistoricalGitCommit'):
   raw=subprocess.check_output(['git','show',r['verifiedHistoricalGitCommit']+':'+original],cwd=ROOT);assert digest(raw)==r['sha256'];gitbound.append({**r,'verification':'exact-historical-git-bytes'})
  else:
   assert r.get('historicalOnly') and (original,r['sha256']) not in critical_keys
   unavailable.append({**r,'verification':'unavailable-archival-metadata-only','notCurrentNumericAcceptanceInput':True})
 archives=[ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-disjoint-current-rebind-v3/historical-manifest.json',ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-proof-closure-v3/market-preinstallation-manifest.json']
 witnesses=[]
 def walk(value,pointer,archive):
  if isinstance(value,dict):
   for k,v in value.items():walk(v,pointer+'/'+k.replace('~','~0').replace('/','~1'),archive)
  elif isinstance(value,list):
   for i,v in enumerate(value):walk(v,pointer+'/'+str(i),archive)
  elif value==TARGET:witnesses.append(dict(archive=ref(archive),jsonPointer=pointer))
 for archive in archives:walk(read(archive),'',archive)
 assert witnesses and any(r['path']==TARGET and r['sha256']=='510d79c3a05d4263e907e34666ba1eb0a15e598e51fd711126939ceebf11b191' for r in unavailable)
 save(DOC/'closure.json',{**old,'transitiveVerifiedDependencies':sorted(present,key=lambda r:r['path']),'historicalGitVerifiedDependencies':gitbound,'unavailableHistoricalDiagnosticInputs':unavailable,'verifiedCityPathAliases':aliases,'archivalTargetClassification':dict(path=TARGET,sha256='510d79c3a05d4263e907e34666ba1eb0a15e598e51fd711126939ceebf11b191',fileAbsent=True,canonicalJSONHashClaimed=False,notCurrentRoleEvidenceRef=True,notCurrentNumericAcceptanceInput=True,actualMarketTerrainSheet='11-NW-13A',historicalArchiveTerrainSheet='11-NE-25A',historicalManifestPointerWitnesses=witnesses),'priorImmutableClosure':ref(PRIOR),'classificationScript':ref(Path(__file__)),'currentAcceptanceInputsAllVerified':True,'qualification':'Exact present bytes and historical git bytes are separated from unavailable transitive raw territorial archive metadata. Frozen global manifest archives preserve exact historical provenance references; they are not treated as live numeric source/ground inputs. No frozen source/physical/role/browser receipt changed.'})
 print(json.dumps(dict(presentVerified=len(present),gitVerified=len(gitbound),archivalUnavailable=len(unavailable),targetWitnesses=witnesses)),flush=True)
if __name__=='__main__':main()
