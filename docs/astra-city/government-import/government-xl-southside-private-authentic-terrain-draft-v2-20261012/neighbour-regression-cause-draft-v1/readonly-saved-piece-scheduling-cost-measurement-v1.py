import json,gzip,base64,hashlib,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');B=R/'docs/astra-city/government-import';D=B/'government-xl-southside-private-authentic-terrain-draft-v2-20261012';C=D/'neighbour-regression-cause-draft-v1'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def bnd(ps):return tuple((min(p[k]for p in ps),max(p[k]for p in ps))for k in range(2))
def meet(a,b):return not any(a[k][1]<b[k][0]or b[k][1]<a[k][0]for k in range(2))
start=time.monotonic();cap=B/'government-xl-southside-source-local-v4-private-ground-capture-v1-20261012';oldp=B/'government-xl-southside-315025-300867-complete-four-stream-current-finite-v1-20261012/diagnostic.json.gz';actp=D/'actual-basic-extent-proof.json.gz';inputs=[oldp,actp,cap/'neighbour-inputs.json.gz',cap/'neighbour-checks.json',R/'3d-viewer/city/data/manifest.json'];pins={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in inputs};assert pins['3d-viewer/city/data/manifest.json']=='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
forms={r['building']['uid']:r['building']for r in read(inputs[2])['rows']};bad=sorted(r['uid']for r in read(inputs[3])['rows']if r['reasons']);assert len(bad)==16;actual={r['uid']:r for r in read(actp)['rows']};actors={}
for uid in bad:
 a=actual[uid];assert a['currentForm']==forms[uid];index=np.frombuffer(base64.b64decode(a['completeIndexBytesBase64']),dtype='<u4');bbs=[]
 for mode in ['actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']:
  p=np.frombuffer(base64.b64decode(a['completeStreamBytesBase64'][mode]),dtype='<f8').reshape(-1,3);tris=p[index].reshape(-1,3,3)[:,:,[0,2]]
  bbs.extend(bnd([[F(float(v))for v in pt]for pt in t])for t in tris)
  bbs.extend(bnd([[F(float(p[i,0])),F(float(p[i,2]))]])for i in sorted(set(range(len(p)))-set(map(int,index))))
 ringbb=bnd([[F(v)for v in pt]for ring in forms[uid]['rings']for pt in ring]);allbb=bbs+[ringbb];union=tuple((min(b[k][0]for b in allbb),max(b[k][1]for b in allbb))for k in range(2));ringtri=sum(len(r)for r in forms[uid]['rings'])+2*(len(forms[uid]['rings'])-1)-2
 actors[uid]=dict(primitives=bbs,union=union,ringBounds=ringbb,ringTriangleEstimatedUpper=ringtri)
counts=dict(finitePieces=0,nonFinitePieces=0,actorPairChecks=0,actorPairsNominated=0,primitivePairsUnpruned=0,primitivePairsAfterActorPrune=0,primitivePairsNominated=0,ringTrianglePairsUnprunedEstimated=0,ringTrianglePairsAfterRingBoundsEstimated=0);per={u:dict(piecesNominated=0,primitiveCandidates=0,ringBoundsNominations=0,actualPrimitives=len(v['primitives']),estimatedGuardTriangles=v['ringTriangleEstimatedUpper'])for u,v in actors.items()}
for row in read(oldp)['rows']:
 for q in row['completeOriginalFaceComparisons']:
  cmp=q['currentDrawnGroundComparison']
  if cmp['completeFiniteOrdinaryBoundProved']or cmp['paired']is None:continue
  for piece in cmp['paired']['allExactFiniteSourceGroundPieces']:
   if 'allExactSourcePrismIntersectionVertices'not in piece:counts['nonFinitePieces']+=1;continue
   counts['finitePieces']+=1;bb=bnd([[F(v['exactOriginalSourcePoint'][k])for k in (0,2)]for v in piece['allExactSourcePrismIntersectionVertices']])
   for uid,a in actors.items():
    counts['actorPairChecks']+=1;counts['primitivePairsUnpruned']+=len(a['primitives']);counts['ringTrianglePairsUnprunedEstimated']+=a['ringTriangleEstimatedUpper']
    if not meet(bb,a['union']):continue
    counts['actorPairsNominated']+=1;counts['primitivePairsAfterActorPrune']+=len(a['primitives']);per[uid]['piecesNominated']+=1;n=sum(meet(bb,p)for p in a['primitives']);counts['primitivePairsNominated']+=n;per[uid]['primitiveCandidates']+=n
    if meet(bb,a['ringBounds']):counts['ringTrianglePairsAfterRingBoundsEstimated']+=a['ringTriangleEstimatedUpper'];per[uid]['ringBoundsNominations']+=1
for p,h in pins.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
out=dict(schema='southside-saved-piece-scheduling-cost-measurement-v1',counts=counts,actors=per,elapsedSeconds=time.monotonic()-start,inputHashes=pins,strictExactClosedAABBOnly=True,touchesRetained=True,guardTriangleCountsEstimateOnly=True,noClippingNoTriangulationNoPredicateReplay=True,noDB=True,noLease=True,currentAcceptance=False);dest=C/'saved-piece-scheduling-cost-measurement-v1.json';dest.open('x').write(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(path=str(dest.relative_to(R)),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),counts=counts,elapsedSeconds=out['elapsedSeconds'])))
