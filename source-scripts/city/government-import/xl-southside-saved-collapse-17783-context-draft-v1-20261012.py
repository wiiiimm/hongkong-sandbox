"""UNEXECUTED saved-data packing context; no DB, lease, source decode or replay.
Coverage failures are observations, never new terrain acceptance requirements.
"""
import gzip,hashlib,json,struct,sys
from pathlib import Path
from fractions import Fraction as F
import southside_saved_packed_collapse_context_v1_20261012 as helper
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE=ROOT/'docs/astra-city/government-import';D=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012/collapse-17783-review-draft-v1'
DOC=BASE/'government-xl-southside-315025-300867-source-local-private-terrain-diagnostic-v4-20261012'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
PINS={
 str((DOC/'saved-source-local-construction-account.json.gz').relative_to(ROOT)):'feb6e5ef770c3a6ca97b606fbfd99b6f1c89d917e4e0353041dd91496f5b5118',
 'source-scripts/city/government-import/local/government-xl-southside-315025-300867-source-local-private-terrain-diagnostic-v4-20261012/private-terrain.json':'d493c3bb9e60a076fc5c1df2a1f801dc695bcb48696f8a08d56e7be466448642',
 str((D/'saved-rank-and-lineage-inspection.json').relative_to(ROOT)):'4c85bf65e652e014223eaa5eb557ac297c502fa29a902cb4e56b99ddab8968db',
 str((D/'saved-complete-bounds-obligation-inspection.json').relative_to(ROOT)):'eda43c37ed23fb634e7cc26641064736014c00ae46bb00194219ff50bdad0df4'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):
 raw=path.read_bytes();return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)
def pin(path):return dict(path=str(path.relative_to(ROOT)),sha256=sha(path.read_bytes()))
def preflight():
 for p,h in PINS.items():assert sha((ROOT/p).read_bytes())==h
 assert sha((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 saved=read(DOC/'saved-source-local-construction-account.json.gz');a=saved['account'];p=read(ROOT/saved['privateCandidatePath']);lineage=a['completeOutputFacetLineage']
 assert a['outputFacets']==24580 and a['realOutputFacetsCollapsedByFloat32']==[17783]
 assert [q['outputFacet']for q in lineage]==list(range(24580))
 ix=p['nativeMesh']['index'];v=p['nativeMesh']['position'];assert ix==list(range(24580*3))and len(v)==24580*9
 target=lineage[17783];assert target['globalOriginalFacetId']==638485 and target['savedOriginalFragmentOutput']==54459 and target['classification']=='changed-local-collar'
 assert target['exactAlphaAffine']==['1/5','0','-321/2']and target['parentFacet']==65 and target['packedZero3DArea']is True
 rank=read(D/'saved-rank-and-lineage-inspection.json');assert rank['collapse']==target
 candidates=rank['closedPackedXZCandidateOutputIDs'];records=[]
 for i in candidates:
  q=lineage[i];t=[v[i*9+j*3:i*9+j*3+3]for j in range(3)]
  expected=[[struct.unpack('<f',struct.pack('<f',float(F(x))))[0]for x in point]for point in q['exactProposedPoints']];assert t==expected
  records.append(dict(**q,packedPoints=t))
 support=read(D/'saved-complete-bounds-obligation-inspection.json');assert not support['nominatedBasicUIDs']and not support['emptyGeometryUnresolvedUIDs']and len(support['completeBasicStrictExclusionRecords'])==1231 and len(support['ownedWholeWorldExclusions'])==8
 for q in support['inputs']:
  assert sha((ROOT/q['path']).read_bytes())==q['sha256']
  raw=read(ROOT/q['path'])
  for path,h in raw.get('inputHashes',{}).items():assert sha((ROOT/path).read_bytes())==h
 assert a['whole6649NativeDomainNomination']['nominated']==[]
 return saved,target,records,support

def main():
 saved,target,records,support=preflight()
 if '--preflight-only'in sys.argv:
  print(json.dumps(dict(noDB=True,noLease=True,noSourceDecode=True,noCoveragePredicate=True,candidateFaces=24580,closedNeighbourCandidates=len(records),currentAcceptance=False)));return
 output=D/'saved-packed-neighbour-coverage-and-plane-context.json';assert not output.exists()
 proposed=target['exactProposedPoints'];same=[q for q in records if q['globalOriginalFacetId']==638485];source=[q for q in records if q['globalOriginalFacetId']is not None];parent=[q for q in records if q['classification']=='retained-parent-exterior']
 out=dict(schema='southside-saved-packed-collapse-context-v1',targetVerbatim=target,completeClosedNeighbourRecords=records,
  sameOriginalFacetProjection=helper.coverage(proposed,same),allOriginalLayerProjection=helper.coverage(proposed,source),parentExteriorProjection=helper.coverage(proposed,parent),allPackedNeighbourProjection=helper.coverage(proposed,records),
  completeNeighbourPlaneContext=[helper.plane_context(proposed,q)for q in records],
  completeSupportBoundsNominationVerbatim=support,originalInventoryBindingsVerbatim=saved['fullOriginalInventoryVerbatim'],
  noBuildingGeometryCollapse=True,terrainFacetRetained=True,noLayerDeleted=True,nonzeroEveryTerrainFacetRequirement=False,
  projectionCoverageIsNotHeightLayerOrSeamAcceptance=True,existingRuntimeAndPlacementPoliciesUnchanged=True,
  actualWholeCandidateGroundAnd117ProtectionChecksStillPending=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,
  inputPins=[dict(path=p,sha256=h)for p,h in sorted(PINS.items())],codePins=[pin(p)for p in [Path(__file__),HERE/'southside_saved_packed_collapse_context_v1_20261012.py',HERE/'test_southside_saved_packed_collapse_context_v1_20261012.py',HERE/'exact_original_projection_coverage_v2_20261010.py',D/'METHOD.md']])
 preflight();raw=(json.dumps(out,sort_keys=True,indent=2)+'\n').encode();output.open('xb').write(raw)
 print(json.dumps(dict(path=str(output.relative_to(ROOT)),sha256=sha(raw),completeNeighbourCandidates=len(records),allPackedCoverage=out['allPackedNeighbourProjection']['wholeClosedProjectionCovered'],currentAcceptance=False)))
if __name__=='__main__':main()
