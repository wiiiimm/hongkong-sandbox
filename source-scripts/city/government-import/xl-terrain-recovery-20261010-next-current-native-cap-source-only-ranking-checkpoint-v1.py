"""Fence the completed exact source-cap shortlist, without approval credit."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read,digest
BATCH='xl-terrain-recovery-20261010-next-current-native-cap-source-only-ranking-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH
p=read(DOC/'diagnostic.json.gz');assert p['sourceOnly']is True and p['fullAcceptance']is False and p['newlyInstalled']==0 and p['nativeReacceptance']is False
refs=p['evidenceRefs']+[dict(path=str(Path(__file__).relative_to(ROOT)),sha256=digest(Path(__file__).read_bytes())),p['manifestAtSourceProbe']]
for r in p['rows']:
 refs.extend([r['cachedSelection'],r['cachedSource']])
 for n in r['completeCandidateNativeInventory']:refs.extend([n['asset'],n['catalogue']])
refs=list({(r['path'],r['sha256']):r for r in refs}.values())
for r in refs:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
s=importlib.util.spec_from_file_location('nativecap_shortlist_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.freeze(BATCH,'exact-source-only-current-native-cap-shortlist-v1',[ROOT/r['path']for r in refs],dict(uids=[r['uid']for r in p['rows']],diagnosticOnly=True,sourceOnly=True,fullAcceptance=False,nativeReacceptance=False,newlyInstalled=0,remainingTerrainFamily=p['remainingTerrainFamily'],boundedCandidatesExamined=len(p['rows']),exactPositiveCapCases=sum(bool(r['exactOriginalNativeCapContacts'])for r in p['rows']),sourceGeometryChanges=0))
