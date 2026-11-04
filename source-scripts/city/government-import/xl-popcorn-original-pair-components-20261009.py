"""Complete original station shells and exact direct attachment to original mall."""
import collections,numpy as np,json
from run import ROOT,HERE,read,save,digest
from original_shell_diagnostic_20261009 import shell_context
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009';inp=read(DOC/'exact-original-contact-inputs.json.gz');src=next(x for x in inp['rows'] if x['uid']=='landsd/295539:0');mall=next(x for x in inp['rows'] if x['uid']=='landsd/295538:0');tri=np.array(src['position']).reshape(-1,3,3);body=np.array(mall['position']).reshape(-1,3,3);parents=np.arange(len(tri));edges={}
def root(i):
 while parents[i]!=i:parents[i]=parents[parents[i]];i=int(parents[i])
 return i
for i,t in enumerate(tri):
 for k in range(3):
  key=tuple(sorted((tuple(t[k]),tuple(t[(k+1)%3]))))
  if key in edges:parents[root(i)]=root(edges[key])
  else:edges[key]=i
groups=collections.defaultdict(list)
for i in range(len(tri)):groups[root(i)].append(i)
lo=body.min(axis=1);hi=body.max(axis=1);cache={};rows=[]
for ci,ids in enumerate(groups.values()):
 ctri=tri[ids];context=shell_context(ctri,[0]);proof=None;tests=0
 for fi in ids:
  face=tri[fi];hits=np.flatnonzero(np.all(hi>=face.min(axis=0),axis=1)&np.all(lo<=face.max(axis=0),axis=1));rf=rational_face(face)
  for j in hits:
   j=int(j);tests+=1
   if j not in cache:cache[j]=rational_face(body[j])
   pts=intersection_points(rf,cache[j])
   if pts:proof={'stationSourceFace':fi,'mallSourceFace':j,'exactIntersectionPoints':[[str(v) for v in p] for p in sorted(pts)]};break
  if proof:break
 row={**context,'component':ci,'originalSourceFaces':ids,'exactOriginalMallAttachment':bool(proof),'attachmentWitness':proof,'exactTrianglePairsTested':tests};rows.append(row);print({k:row[k] for k in ['component','triangles','closedConsistentlyOriented','bounds','exactOriginalMallAttachment','exactTrianglePairsTested']},flush=True)
save(DOC/'complete-station-source-shells-and-mall-attachments.json.gz',{'uid':src['uid'],'sourceSHA256':src['sourceSHA256'],'sourceWorldTriangleSHA256':src['worldTriangleSHA256'],'supportSHA256':mall['sourceSHA256'],'supportWorldTriangleSHA256':mall['worldTriangleSHA256'],'sourceTriangles':len(tri),'completeFaceAccounting':sum(len(x['originalSourceFaces']) for x in rows)==len(tri),'components':rows,'installationApproved':False,'identityAccepted':False,'supportAccepted':False,'modelGeometryChanges':0,'qualification':'Exact surface attachment and open/closed topology evidence only. Does not replace all source terrain/contact/runtime gates or infer roof/canopy structural support from intersection alone.'})
