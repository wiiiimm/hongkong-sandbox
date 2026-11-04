"""DRAFT exact, resumable positive-overlap and atomic-edge inventory.
Spatial buckets nominate candidates only; integer AABB/SAT rejects are exact.
Every remaining pair uses the existing Fraction clipping kernel. No geometry edits.
"""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import gzip, hashlib, json, math, os
from exact_source_core_ten_metre_transition_domain_v1_20261011 import polygon, intersection
from exact_original_projection_coverage_v2_20261010 import signed_area
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on, at

def encoded(x):
 if isinstance(x,F):return {'exactFraction':str(x)}
 if isinstance(x,dict):return {k:encoded(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [encoded(v)for v in x]
 return x
def decoded(x):
 if isinstance(x,dict):
  if set(x)=={'exactFraction'}:return F(x['exactFraction'])
  return {k:decoded(v)for k,v in x.items()}
 if isinstance(x,list):return [decoded(v)for v in x]
 return x
def raw(x):return json.dumps(encoded(x),sort_keys=True,separators=(',',':')).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def atomic_write(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.tmp')
 with temp.open('wb')as f:f.write(gzip.compress(raw(value),mtime=0));f.flush();os.fsync(f.fileno())
 os.replace(temp,path)
def read(path):return decoded(json.loads(gzip.decompress(Path(path).read_bytes())))

class Checkpoints:
 def __init__(self,folder,polygons,input_bindings,check_inputs,chunk_size=512):
  assert type(chunk_size)is int and 1<=chunk_size<=512
  self.folder=Path(folder);self.check_inputs=check_inputs;self.chunk_size=chunk_size
  self.contract=dict(schema='exact-projected-inventory-v1',helperSHA256=sha(Path(__file__).read_bytes()),polygonsSHA256=sha(raw(polygons)),completePolygons=len(polygons),inputBindings=input_bindings,chunkSize=chunk_size)
  self.check_inputs();p=self.folder/'contract.json.gz'
  if p.exists():assert read(p)==self.contract,'Changed checkpoint contract'
  else:atomic_write(p,self.contract)
 def map(self,label,items,compute):
  result=[];plan=sha(raw(items));count=len(items)
  for start in range(0,count,self.chunk_size):
   end=min(start+self.chunk_size,count);part=items[start:end];binding=dict(contractSHA256=sha(raw(self.contract)),label=label,completeItems=count,completeOrderedItemsSHA256=plan,start=start,end=end,chunkItemsSHA256=sha(raw(part)))
   path=self.folder/label/f'{start:09d}-{end:09d}.json.gz';self.check_inputs()
   cached=path.exists()
   if cached:
    saved=read(path);assert saved['binding']==binding and saved['payloadSHA256']==sha(raw(saved['payload'])),'Changed checkpoint payload/binding';payload=saved['payload']
   else:
    payload=decoded(encoded(compute(part)));self.check_inputs();atomic_write(path,dict(binding=binding,payload=payload,payloadSHA256=sha(raw(payload))))
   result.extend(payload);print(json.dumps(dict(exactInventoryChunk=label,completeItems=count,completedItems=end,cached=cached,currentAcceptance=False)),flush=True)
  self.check_inputs();return result

def integer_coordinates(polygons):
 denominator=1
 for p in polygons:
  for q in p:
   for v in q:denominator=math.lcm(denominator,F(v).denominator)
 return [[tuple(int(F(v)*denominator)for v in q)for q in p]for p in polygons],denominator
def boxes(polygons):return [(min(q[0]for q in p),max(q[0]for q in p),min(q[1]for q in p),max(q[1]for q in p))for p in polygons]
def cells(box,width):
 a,b,c,d=box
 for x in range(a//width,b//width+1):
  for z in range(c//width,d//width+1):yield x,z
def candidate_pairs(integer_polygons,denominator):
 # Five metres is an index bucket size, never a geometry/domain/tolerance change.
 # Closed exact bucket inclusion ensures every overlapping AABB shares a bucket.
 width=5*denominator;b=boxes(integer_polygons);buckets=defaultdict(list);pairs=set()
 for i,box in enumerate(b):
  for key in cells(box,width):
   for j in buckets[key]:pairs.add((j,i))
   buckets[key].append(i)
 return sorted(pairs,key=lambda p:(p[1],p[0])),b
def positive_aabb(a,b):return max(a[0],b[0])<min(a[1],b[1])and max(a[2],b[2])<min(a[3],b[3])
def interiors_separated(a,b):
 # For convex positive-area polygons, a separating edge-normal axis with
 # disjoint OR touching projection intervals proves zero positive area.
 for p in [a,b]:
  for u,v in zip(p,p[1:]+p[:1]):
   axis=(v[1]-u[1],u[0]-v[0]);assert axis!=(0,0)
   aa=[q[0]*axis[0]+q[1]*axis[1]for q in a];bb=[q[0]*axis[0]+q[1]*axis[1]for q in b]
   if max(aa)<=min(bb)or max(bb)<=min(aa):return True
 return False
def overlaps(polygons,checkpoints):
 polygons=[polygon(p)for p in polygons];ints,den=integer_coordinates(polygons);pairs,b=candidate_pairs(ints,den)
 def compute(part):
  out=[]
  for j,i in part:
   if not positive_aabb(b[j],b[i]):out.append(dict(pair=[j,i],disposition='exact-AABB-zero-positive-area'));continue
   if interiors_separated(ints[j],ints[i]):out.append(dict(pair=[j,i],disposition='exact-integer-SAT-zero-positive-area'));continue
   area=signed_area(intersection(polygons[j],polygons[i]));assert area>0,'SAT nomination disagrees with exact clip'
   out.append(dict(pair=[j,i],disposition='exact-positive-overlap',exactPositiveAreaM2=area))
  return out
 rows=checkpoints.map('positive-overlap-pairs',pairs,compute)
 assert [r['pair']for r in rows]==[list(p)for p in pairs]
 bad=[dict(pieces=r['pair'],exactPositiveOverlapM2=r['exactPositiveAreaM2'])for r in rows if r['disposition']=='exact-positive-overlap']
 return bad,dict(completePieces=len(polygons),completeUnorderedPairs=len(polygons)*(len(polygons)-1)//2,completeClosedBucketCandidatePairs=len(pairs),excludedExactBucketDisjointPairs=len(polygons)*(len(polygons)-1)//2-len(pairs),exactAABBZeroPositivePairs=sum(r['disposition']=='exact-AABB-zero-positive-area'for r in rows),exactSATZeroPositivePairs=sum(r['disposition']=='exact-integer-SAT-zero-positive-area'for r in rows),exactClippedPositivePairs=len(bad),integerCoordinateDenominator=den,bucketWidthM=5)
def atomic(polygons,checkpoints):
 polygons=[polygon(p)for p in polygons];bad,accounting=overlaps(polygons,checkpoints);ints,den=integer_coordinates(polygons);width=5*den;points=sorted({q for p in ints for q in p});point_buckets=defaultdict(list)
 for p in points:point_buckets[(p[0]//width,p[1]//width)].append(p)
 edges=[dict(piece=i,start=a,end=b)for i,p in enumerate(polygons)for a,b in zip(p,p[1:]+p[:1])]
 def compute(part):
  rows=[]
  for edge in part:
   a,b=edge['start'],edge['end'];ia=tuple(int(v*den)for v in a);ib=tuple(int(v*den)for v in b);box=(min(ia[0],ib[0]),max(ia[0],ib[0]),min(ia[1],ib[1]),max(ia[1],ib[1]));cuts={F(0),F(1)}
   for key in cells(box,width):
    for q in point_buckets[key]:
     if not(box[0]<=q[0]<=box[1]and box[2]<=q[1]<=box[3]):continue
     t=on(a,b,tuple(F(v,den)for v in q))
     if t is not None:cuts.add(t)
   rows.append(dict(edge=edge,cuts=sorted(cuts)))
  return rows
 rows=checkpoints.map('whole-source-edge-cuts',edges,compute);assert len(rows)==len(edges)and all(raw(r['edge'])==raw(e)for r,e in zip(rows,edges));atoms=defaultdict(list)
 for r in rows:
  e=r['edge'];cuts=r['cuts'];assert cuts==sorted(set(cuts))and cuts[0]==0 and cuts[-1]==1
  for lo,hi in zip(cuts,cuts[1:]):
   u,v=at(e['start'],e['end'],lo),at(e['start'],e['end'],hi);assert u!=v;atoms[tuple(sorted((u,v)))].append(dict(piece=e['piece'],start=u,end=v))
 boundary=[];invalid=[]
 for key,inc in sorted(atoms.items()):
  row=dict(endpoints=key,incidences=inc)
  if len(inc)==1:boundary.append(row)
  elif len(inc)!=2 or inc[0]['start']!=inc[1]['end']or inc[0]['end']!=inc[1]['start']:invalid.append(row)
 outgoing=defaultdict(list);incoming=defaultdict(list)
 for i,r in enumerate(boundary):e=r['incidences'][0];outgoing[e['start']].append(i);incoming[e['end']].append(i)
 branches=[dict(point=p,outgoing=outgoing[p],incoming=incoming[p])for p in sorted(set(outgoing)|set(incoming))if len(outgoing[p])!=1 or len(incoming[p])!=1];cycles=[]
 if not branches:
  remaining=set(range(len(boundary)))
  while remaining:
   first=min(remaining);now=first;ids=[]
   while now in remaining:remaining.remove(now);ids.append(now);now=outgoing[boundary[now]['incidences'][0]['end']][0]
   assert now==first;pts=[boundary[i]['incidences'][0]['start']for i in ids];cycles.append(dict(atoms=ids,points=pts,exactSignedAreaM2=signed_area(pts)))
 result=dict(completePieces=len(polygons),allAtomicEdges=[dict(endpoints=k,incidences=v)for k,v in sorted(atoms.items())],allBoundaryAtoms=boundary,allInvalidIncidences=invalid,allPositiveOverlaps=bad,allBranchPoints=branches,allDirectedCycles=cycles,projectedTopologyQualified=not bad and not invalid and not branches and bool(cycles)and all(c['exactSignedAreaM2']!=0 for c in cycles))
 return result,accounting
