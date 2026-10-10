"""Mei source declaration using existing certified disjoint-provenance boundaries.
Only archived acquisition metadata at exact routing entry/source pointers is
nonrecursive; every current routing asset, bounds and own numeric input remains.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from original_disjoint_routing_metadata_scope_20261010 import boundaries,verify_boundaries
BASE=ROOT/'docs/astra-city/government-import';OUT=BASE/'xl-terrain-recovery-20261010-mei-yat-source-scope-declaration-v4'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();prior=BASE/'xl-terrain-recovery-20261010-mei-yat-source-scope-declaration-v2/declared-scope.json';scope=read(prior);paths=set(scope['closedPaths']);paths.update(str(p.relative_to(ROOT)) for p in [prior,Path(__file__),HERE/'xl-terrain-recovery-20261010-mei-yat-source-scope-declaration-v3.py',HERE/'original_disjoint_routing_metadata_scope_20261010.py',HERE/'test_original_disjoint_routing_metadata_scope_20261010.py'])
 aliases={r['sha256']:r['archive'] for r in scope['historicalManifestAliases']};declared=[];certificate_rows=[]
 for physical in ['government-xl-terrain-recovery-mei-yat-original-terrain-current-v4-20261010']:
  p=BASE/physical/'current-source-terrain-preflight.json';d=read(p);sha=d['currentManifest']['sha256'];archive=ROOT/aliases[sha]['path'];assert digest(archive.read_bytes())==sha
  manifest=read(archive);bs=boundaries(d,manifest);assert verify_boundaries(d,manifest,bs)=={r['pointer'] for r in bs};assert all(r['pointer'].startswith('/completeCurrentTerrainRouting/') and r['pointer'].endswith('/entry/source') for r in bs)
  for row in d['completeCurrentTerrainRouting']:
   a=row['asset'];assert ref(ROOT/a['path'])==a,'Complete actual disjoint routing asset remains mandatory'
  candidates=read(BASE/physical/'terrain-candidates.json');assert len(candidates)==1 and candidates[0]['uids']==['landsd/183776:0'] and candidates[0]['sha256']=='236965084f218668079721d9197867bf04fcf93bc6491ab7a08cd8a9096520e7' and candidates[0]['bounds']==d['immutableTerrainProposal']['bounds'];assert digest((ROOT/candidates[0]['path']).read_bytes())==candidates[0]['sha256']
  declared.extend(dict(path=str(p.relative_to(ROOT)),documentSHA256=digest(p.read_bytes()),boundary=b) for b in bs);certificate_rows.append(dict(preflight=ref(p),manifestArchive=ref(archive),proposal=ref(BASE/physical/'terrain-candidates.json'),boundaries=bs,actualRoutingAssetsFullyHashValidated=True,completeBoundsStrictDisjoint=True))
 save(OUT/'existing-contract-boundaries.json',dict(contract=ref(HERE/'original_disjoint_routing_metadata_scope_20261010.py'),rows=certificate_rows,noNewVerifierRule=True,numericSourceGeometryOrGroundLeaves=0));paths.add(str((OUT/'existing-contract-boundaries.json').relative_to(ROOT)))
 scope.update(closedPaths=sorted(paths),closedExplicitPaths=sorted(paths),presentFileBindings=[ref(ROOT/p) for p in sorted(paths)],metadataLeafJsonPointers=declared,existingMetadataBoundaryContract=ref(HERE/'original_disjoint_routing_metadata_scope_20261010.py'),exactOwnSourceGeometryAndTINRemainRecursive=True,qualification='Existing reviewed typed contract only. The byte-pinned current routing assets and every measured complete strictly disjoint bound remain recursive numerical evidence. Only exact frozen manifest acquisition metadata under routing entry/source pointers is nonrecursive. Source9-SE8D, all original/literal10209faces, complete actual ground,413facetproposal/provider/host/current actors and raw failures remain fully recursive. Prior failed scopes and exact11SW10D restoration remain unchanged. Root independent verifier required.')
 save(OUT/'declared-scope.json',scope);print(dict(paths=len(paths),certifiedProvenancePointers=len(declared)))
if __name__=='__main__':main()
