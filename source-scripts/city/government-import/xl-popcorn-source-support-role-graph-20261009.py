"""Complete exact original station component contact graph, no model edits or support waiver."""
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
DOC=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-support-roles-20261009';PRIOR=ROOT/'docs/astra-city/government-import/government-xl-popcorn-original-pair-interface-20261009';inp=read(PRIOR/'exact-original-contact-inputs.json.gz');src=next(r for r in inp['rows'] if r['uid']=='landsd/295539:0');tri=np.array(src['position']).reshape(-1,3,3);parts=read(PRIOR/'complete-station-source-shells-and-mall-attachments.json.gz')['components'];bounds=[(tri[p['originalSourceFaces']].min(axis=1),tri[p['originalSourceFaces']].max(axis=1)) for p in parts];cache={};edges=[]
for i,a in enumerate(parts):
 for j,b in enumerate(parts):
  if i>=j:continue
  blo,bhi=bounds[j];w=None;tests=0
  for fi in a['originalSourceFaces']:
   t=tri[fi];hits=np.flatnonzero(np.all(bhi>=t.min(axis=0),axis=1)&np.all(blo<=t.max(axis=0),axis=1))
   if not len(hits):continue
   if fi not in cache:cache[fi]=rational_face(t)
   for ix in hits:
    fj=b['originalSourceFaces'][int(ix)];tests+=1
    if fj not in cache:cache[fj]=rational_face(tri[fj])
    pts=intersection_points(cache[fi],cache[fj])
    if pts:w={'sourceFaceA':fi,'sourceFaceB':fj,'exactIntersectionPoints':[[str(v) for v in p] for p in sorted(pts)]};break
   if w:break
  edges.append({'componentA':i,'componentB':j,'exactSurfaceContact':bool(w),'contactWitness':w,'exactTrianglePairsTested':tests})
  if w:print({'pair':[i,j],'attached':True,'exactPairs':tests},flush=True)
connected={i for i,p in enumerate(parts) if p['exactOriginalMallAttachment']};changed=True
while changed:
 previous=set(connected)
 for e in edges:
  if e['exactSurfaceContact'] and ({e['componentA'],e['componentB']} & connected):connected.update([e['componentA'],e['componentB']])
 changed=previous!=connected
out={'uid':src['uid'],'sourceSHA256':src['sourceSHA256'],'sourceWorldTriangleSHA256':src['worldTriangleSHA256'],'allOriginalComponentEdges':edges,'allOriginalComponents':parts,'exactAttachmentPathToOriginalMallComponents':sorted(connected),'originalComponentsWithoutExactAttachmentPath':[i for i in range(len(parts)) if i not in connected],'sourceGeometryChanges':0,'physicalSupportAccepted':False,'installationApproved':False,'qualification':'Exact rational source-only surface contacts establish geometric graph paths only. They do not certify canopy/roof/facade load-bearing roles, override unsupported rims or replace whole-original terrain, runtime and neighbour gates.'};save(DOC/'complete-original-station-attachment-graph.json.gz',out);print({k:out[k] for k in ['exactAttachmentPathToOriginalMallComponents','originalComponentsWithoutExactAttachmentPath']},flush=True)
