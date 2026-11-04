"""Stage continuous source-network candidates without inventing public connections.
Routes are source selections, not yet validated gameplay walking routes.
"""
import collections,gzip,hashlib,heapq,json,math,pathlib
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/central-completion'
# Approximate visitor points only select nearby original network nodes. No
# straight connector to these hints is added to the source geometry.
HINTS={
 'core':[('Statue Square',24.8,666.9,5),('HSBC frontage',-20,738,4),('Bank Street',35,790,6),('Chater Garden',125,758,6),('Bank of China Tower frontage',185,852,8),('City Hall frontage',180,550,4)],
 'waterfront':[('City Hall frontage',180,550,4),('IFC eastern frontage',35,300,5),('Central piers promenade',100,90,4),('Central harbourfront',480,415,4),('Tamar Park',652.6,631.9,6)],
 'soho':[('Central Market northern frontage',-430,306,4),('Pottinger Street',-490,487,15),('Hollywood Road',-654,568,34),('Shelley Street',-706.8,648.1,51),('Staunton Street',-770,690,56),('Lan Kwai Fong',-425,735,25)],
}
TYPES={1:'footway',2:'footbridge',6:'traffic island',7:'driveway crossing',11:'ramp',12:'stairs',23:'park path',30:'signalised crossing',31:'zebra crossing',32:'cautionary crossing',33:'other crossing'}
def key(p):return tuple(round(v,3) for v in p)
def world(p):return [p[0]-834500,p[2],816500-p[1]]
def length(line):return sum(math.dist(a,b) for a,b in zip(line,line[1:]))
def main(blocked_ids=(), output_name="route-candidates.json", selected_hints=None):
 blocked_ids=set(blocked_ids)
 source=HERE/'pedestrian-network.json.gz';features=json.loads(gzip.decompress(source.read_bytes()))['features'];access=json.loads((HERE/'pedestrian-access.json').read_text())['tables']
 schedules={r['AccessTimeID']:r for r in access['AccessTime']};details=collections.defaultdict(list)
 for r in access['AccessTimeDetails']:details[r['AccessTimeID']].append(r)
 def open_reference(id):
  return id is None or (schedules[id]['AccessTimeType']=='OPEN' and any(r['DayCode']=='ED' and r['FromTime']==0 and r['ToTime']==2359 for r in details[id]))
 graph=collections.defaultdict(list);nodes={};segments={};excluded=collections.Counter()
 for f in features:
  a=f['attributes'];reason=None
  if a['Location']!=1:reason='indoor'
  elif a['Enabled']!=1 or a['PositionCertainty']!=1:reason='not source-enabled/certain'
  elif a['FeatureType'] not in TYPES:reason='service lane, lift, escalator or unsupported type'
  elif a['Direction']!=0:reason='directional facility'
  elif not open_reference(a['AccessTimeID']):reason='restricted or unresolved opening time'
  if reason:excluded[reason]+=1;continue
  for part,line in enumerate(f['geometry']['paths']):
   id=str(a['PedestrianRouteID'])+':'+str(part)
   if id in blocked_ids:excluded['obstacle screen or source review boundary']+=1;continue
   start,end=key(line[0]),key(line[-1]);nodes.setdefault(start,line[0]);nodes.setdefault(end,line[-1])
   assert id not in segments
   dist=length(line);segment={'id':id,'sourceObjectId':a['OBJECTID'],'pedestrianRouteId':a['PedestrianRouteID'],'attributes':a,'nativeCentreline':line,'centrelineXYZ':[world(p) for p in line],'lengthMetres':dist,'kind':TYPES[a['FeatureType']],'source':f'https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637222018065_52265/MapServer/0/query?f=json&where=PedestrianRouteID%3D{a["PedestrianRouteID"]}&outFields=*&returnGeometry=true&outSR=2326&returnZ=true'}
   segments[id]=segment
   # Public bridges remain candidate links but incur a review penalty to favour
   # ordinary ground routes. Every used bridge is explicitly reported as a gap.
   cost=dist*(2 if a['FeatureType']==2 else 1.15 if a['FeatureType']==12 else 1)
   graph[start].append((end,cost,id,False));graph[end].append((start,cost,id,True))
 def nearest(hint):
  name,x,z,y=hint;rank=sorted(nodes,key=lambda k:math.hypot(k[0]-834500-x,816500-k[1]-z)+abs(k[2]-y)*2)
  k=rank[0];p=world(nodes[k]);assert math.hypot(p[0]-x,p[2]-z)<30,(name,p,hint)
  return k,{'title':name,'hintWorldXYZ':[x,y,z],'sourceWorldXYZ':p,'horizontalHintDistanceMetres':math.hypot(p[0]-x,p[2]-z)}
 def path(start,end):
  queue=[(0,start)];best={start:0};previous={}
  while queue:
   cost,node=heapq.heappop(queue)
   if cost!=best[node]:continue
   if node==end:break
   for dest,delta,id,reverse in graph[node]:
    total=cost+delta
    if total<best.get(dest,math.inf):best[dest]=total;previous[dest]=(node,id,reverse);heapq.heappush(queue,(total,dest))
  assert end in best,('Disconnected source nodes',start,end)
  result=[];node=end
  while node!=start:prior,id,reverse=previous[node];result.append((id,reverse));node=prior
  return result[::-1]
 routes=[]
 for name,hints in (selected_hints or HINTS).items():
  anchors=[nearest(h) for h in hints];selected=[];lines=[];gaps=[]
  for (start,_),(end,_) in zip(anchors,anchors[1:]):
   for id,reverse in path(start,end):
    s=segments[id];line=s['centrelineXYZ'][::-1] if reverse else s['centrelineXYZ'];line=[p[:] for p in line]
    if lines:assert math.dist(lines[-1],line[0])<.002,(id,lines[-1],line[0])
    lines.extend(line if not lines else line[1:]);selected.append({**s,'reverse':reverse})
    if s['kind']=='footbridge':gaps.append({'segment':id,'reason':'Source 3D pedestrian line exists; an actual source deck/collision surface must be matched and validated before walking.'})
  routes.append({'id':'central-'+name,'sectionId':{'core':'01.1','waterfront':'01.2','soho':'01.3'}[name],'status':'source-connected-runtime-unverified','anchors':[a for _,a in anchors],'sourceLengthMetres':length(lines),'sourceCentrelineXYZ':lines,'centreline':[[p[0],p[2]] for p in lines],'segments':selected,'gaps':gaps,'segmentKinds':dict(collections.Counter(s['kind'] for s in selected))})
 payload={'schemaVersion':1,'area':'Central','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceCRS':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','sourceAccuracy':{'horizontalMetres':1,'verticalMetres':2,'basis':'3DPN Data Dictionary v2.2 sections 1.3–1.4'},'heightPolicy':'Original network Z is retained for comparison. Its stated accuracy is not a surveyed bridge floor; match actual source deck geometry before surface publication.','nodeJoinPolicy':'Native XYZ endpoints rounded to 0.001 m solely for network identity; original segment vertices retained. Joined endpoint mismatch must remain below 0.002 m. No cross-level or straight-line invented links.','selectionPolicy':'Source-enabled, certain outdoor bidirectional segments. Excludes service lanes, lifts, moving stairs and restricted/unresolved schedules. Explicit every-day 00:00–23:59 opening entries accepted as full-day references; null schedules remain null.','excludedSourceSegments':dict(excluded),'routes':routes,'limits':['Continuous source topology is not a continuous navigation pass.','Bridge, stair and terrain placement still need actual surfaces and actor-clearance checks.','Source opening-time attributes are references, not live closure information.']}
 DOC.mkdir(exist_ok=True);(DOC/output_name).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps([{'route':r['id'],'metres':r['sourceLengthMetres'],'segments':len(r['segments']),'kinds':r['segmentKinds'],'gaps':len(r['gaps'])} for r in routes],indent=2))
 return payload
if __name__=='__main__':main()
