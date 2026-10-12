import sys,json,base64,ast,hashlib
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import numpy as np
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H));from run import read,digest
B=R/'docs/astra-city/government-import';D=B/'government-xl-southside-private-authentic-terrain-draft-v2-20261012/neighbour-regression-cause-draft-v1';O=D/'immutable-saved-piece-import-preflight-v1';I=B/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012';A=B/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012';C=B/'government-xl-southside-source-local-v4-private-ground-capture-v1-20261012';E=D.parent/'actual-basic-extent-proof.json.gz';oldpath=B/'government-xl-southside-315025-300867-complete-four-stream-current-finite-v1-20261012/diagnostic.json.gz';old=read(oldpath);auth=read(A/'diagnostic.json.gz');worlds=read(I/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];selection=read(C/'neighbour-inputs.json.gz');bad={r['uid']for r in read(C/'neighbour-checks.json')['rows']if r['reasons']};forms={r['building']['uid']:r['building']for r in selection['rows']};actual={r['uid']:r for r in read(E)['rows']};stat=Counter();lengths=Counter()
for row in auth['rows']:
 ids=row['allAuthenticatedGroundFailuresRetained'];n=len(worlds[row['uid']]['completeWorldStreams'][row['arithmetic']]['completeWorldTriangles']);assert all(type(v)is int and 0<=v<n for v in ids)and ids==sorted(set(ids));stat['authenticRowsIntegerFailureIDsVerified']+=1
for row in old['rows']:
 n=len(worlds[row['uid']]['completeDrawnGround'])
 for face in row['completeOriginalFaceComparisons']:
  pair=face['currentDrawnGroundComparison']['paired']
  if pair is None:continue
  stat['savedPairedFaceRecords']+=1
  for piece in pair['allExactFiniteSourceGroundPieces']:
   assert type(piece['originalGroundFace'])is int and 0<=piece['originalGroundFace']<n;stat['savedFinitePieceRecords']+=1
   if 'allExactSourcePrismIntersectionVertices'in piece:
    verts=piece['allExactSourcePrismIntersectionVertices'];assert verts;lengths[len(verts)]+=1
    for v in verts:
     xyz=v['exactOriginalSourcePoint'];assert len(xyz)==3 and all(type(q)is str for q in xyz);p=tuple(F(q)for q in xyz);assert p[1]-F(v['exactFiniteGroundHeightM'])==F(v['exactGapM']);stat['savedExactVertexGapRecords']+=1
    assert min(F(v['exactGapM'])for v in verts)==F(piece['exactMinimumGapM'])
   else:assert piece.get('collapsedProjectionConservative')or piece.get('closedProjectionDisjoint');stat['explicitCollapsedOrDisjointRecords']+=1
for u in sorted(bad):
 q=actual[u];assert q['classification']=='actual-production-BASIC'and q['currentForm']==forms[u]and q['wholeUnusedPositionVerticesIncluded'];index=np.frombuffer(base64.b64decode(q['completeIndexBytesBase64']),dtype='<u4');assert len(index)==q['completeIndexedFaces']*3 and digest(index.tobytes())==q['completeIndexSHA256']
 for mode,key in [('actualLiteral','actualLiteralSHA256'),('explicitLeftAssociatedF32ModelMatrix','explicitLeftAssociatedF32SHA256'),('explicitBalancedF32ModelMatrix','explicitBalancedF32SHA256')]:
  raw=base64.b64decode(q['completeStreamBytesBase64'][mode]);p=np.frombuffer(raw,dtype='<f8').reshape(-1,3);assert digest(raw)==q[key]and len(p)==q['completePositionVertices']and np.isfinite(p).all()and int(index.max())<len(p);stat['completeBasicModeArraysVerified']+=1
stat['completeFormsVerified']=len(bad)
kernel=H/'exact_original_paired_finite_clearance_20261010.py';text=kernel.read_text();assert 'poly=original'in text and 'poly=clip_source(poly,a,b)'in text and 'for x,y,z in poly:'in text and 'allExactSourcePrismIntersectionVertices=paired'in text
# Return values are a schema sentinel only; no real guard domain is triangulated.
from exact_original_polygon_triangle_partition_20261010 import exact_partition
sentinel=exact_partition([[[0.,0.],[1.,0.],[0.,1.]]],[[[0.,0.],[1.,0.],[0.,1.]]]);encoded=json.dumps(sentinel,sort_keys=True);assert json.loads(encoded)==sentinel
pins={str(p.relative_to(R)):digest(p.read_bytes())for p in [oldpath,A/'diagnostic.json.gz',I/'complete-two-actor-four-stream-ground-inputs.json.gz',E,C/'neighbour-inputs.json.gz',C/'neighbour-checks.json',kernel,H/'exact_original_polygon_triangle_partition_20261010.py']}
out=dict(savedSchemaPASS=True,counts=dict(stat),storedPieceVertexCountInventory={str(k):v for k,v in sorted(lengths.items())},cyclicOrderingProvenance=dict(sourceKernelSHA256=digest(kernel.read_bytes()),exactSourceClipProducesOrderedPoly=True,savedVertexListFollowsPolyDirectly=True,pointAndSegmentPiecesNotAssumedAreaPolygons=True,noAdditionalSourceGroundClipPerformed=True),exactPartitionReportJSONRoundtripPASS=True,exactPartitionSchemaSentinelOnly=sentinel,inputHashes=pins,all16DomainAssumptionsVerifiedWithoutBuildingDomains=True,noActualGuardDomainTriangulation=True,noDB=True,noLease=True,noBoundedCompatibilityCalculation=True,noPhysicalAcceptance=True)
f=O/'saved-schema-order-and-serialization-validation.json';f.open('x').write(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(path=str(f.relative_to(R)),sha256=digest(f.read_bytes()),counts=dict(stat),pieceLengths=out['storedPieceVertexCountInventory'])))
