"""DRAFT narrowly typed root-verifier extension, not geometry or numerical acceptance.
Only four exact frozen registry preparedFiles pointers. Complete namespaces/object/CSUID
absence and cached provider-directory equality are rederived before any pointer exclusion.
"""
import json
from run import ROOT,read,digest
B=ROOT/'docs/astra-city/government-import';REG=B/'government-xl-beverly-podium233218-70279-original-registry-farpoint-attribution-v1-20261011/diagnostic.json.gz';PRIMARY=B/'government-xl-beverly-70279-primary-directory-absence-checkpoint-v1-20261011/diagnostic.json.gz'
def canonical(v):return digest(json.dumps(v,sort_keys=True,separators=(',',':')).encode())
def exact(r):
 p=ROOT/r['path'];assert digest(p.read_bytes())==r['sha256'];return read(p)
def validated_pointer_map(contracts):
 registry=read(REG);primary=read(PRIMARY);snapshots=registry['completeFourSheetNativeRegistrySnapshots'];assert len(snapshots)==4 and {s['sheet']for s in snapshots}=={'11-SW-15A','11-SW-15B','11-SW-15C','11-SW-15D'};assert len(contracts)==4;by_path={c['path']:c for c in contracts};assert len(by_path)==4 and set(by_path)=={s['snapshot']['path']for s in snapshots};out={};total=0
 for s in snapshots:
  v=exact(s['snapshot']);n=v['exactNativeResult'];assert v['sheet']==s['sheet']and v['cacheKey']==s['cacheKey']and v['resultSHA256']==s['resultSHA256'];models=n['models'];names=sorted(m['modelId']for m in models);assert len(names)==len(set(names))==s['completeRegistryModels'];assert not[m for m in models if m['modelId'][1:11]=='3716415011'];assert not[m for m in models if any(x.get('objectId')==70279 and x.get('buildingCSUID')=='3716415011T20080220'for x in m.get('matching',{}).get('officialCandidates',[]))];total+=len(names)
  d=next(x for x in primary['allFourRelevantCachedPrimaryProviderDirectories']if x['sheet']==s['sheet']);provider=exact(d['cachedProviderDirectorySnapshot']);assert sorted(m['modelId']for m in provider['models'])==names;assert len(names)==d['completeCachedProviderModels']==d['completeNativeModels'];assert d['providerNativeNameSetsEqual']is True
  assert len(n['terrain'])==1;files=n['terrain'][0]['preparedFiles'];assert len(files)==3
  for r in files:assert isinstance(r['bytes'],int)and r['bytes']>0 and len(r['sha256'])==64 and(r['path']=='manifest.json'or r['path'].startswith('TERRAIN(TB)/'))
  c=by_path[s['snapshot']['path']];assert c['documentSHA256']==s['snapshot']['sha256'];assert c['boundary']==dict(pointer='/exactNativeResult/terrain/0/preparedFiles',canonicalSHA256=canonical(files));assert c['namespaceRecomputed']==dict(sheet=s['sheet'],modelCount=len(names),completeModelNamesSHA256=canonical(names),exactPrefixHits=0,exactObjectAndCSUIDHits=0,cachedPrimaryNameSetEqual=True);out[c['path']]={c['boundary']['pointer']:c['boundary']}
 assert total==1430;return out

def check_boundary(pointer_map,document,pointer,value):
 """Root recursion calls before generic ref traversal; false means recurse unchanged."""
 r=pointer_map.get(document,{}).get(pointer)
 if r is None:return False
 assert pointer=='/exactNativeResult/terrain/0/preparedFiles'and canonical(value)==r['canonicalSHA256'];return True
