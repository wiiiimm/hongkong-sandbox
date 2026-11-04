"""Complete original roof openings vs unchanged reached original host facets.
Fixed existing ±.1 m whole-edge association; no exact intersection, root, bridge,
architectural identity, role waiver, current renderer or installation credit.
"""
from pathlib import Path
from collections import defaultdict
import numpy as np,json
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_segment_surface_contact_band_20261009 import verify_contact_segment
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-parkview-block6-bounded-original-clear-cap-probe-v1-20261011';GRAPH=B/'government-xl-parkview-block6-complete-original-support-paths-v1-20261011';ROUTE=B/'government-xl-parkview-block6-bounded-eligible-native-route-v2-20261011';BATCH='government-xl-parkview-block6-four-original-roof-opening-mounts-v1-20261011';DOC=B/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def opening(t,faces):
 inc=defaultdict(list)
 for i in faces:
  xyz=list(map(tuple,t[i]))
  for a,b in zip(xyz,xyz[1:]+xyz[:1]):inc[tuple(sorted((a,b)))].append((i,a,b))
 outside=[]
 for edge,rows in inc.items():
  assert len(rows)<=2
  if len(rows)==1:outside.append(rows[0])
  else:assert rows[0][1:]==rows[1][1:][::-1]
 assert len(outside)==4;out={a:(i,b)for i,a,b in outside};assert len(out)==4;start=min(out);a=start;loop=[]
 for _ in range(4):
  i,b=out[a];loop.append((i,a,b));a=b
 assert a==start and len({a for _,a,b in loop})==4
 return loop

def main():
 assert not DOC.exists();r=read(OLD/'diagnostic.json.gz');p=ROOT/r['evidenceRefs'][2]['path'];t=decode_original_world_triangles(p.read_bytes());g=read(GRAPH/'diagnostic.json.gz');route=read(ROUTE/'diagnostic.json.gz');assert route['boundedOriginalPathProved'];cs=g['completeSourceEdgeBodyFaces'];unresolved=g['unreachedBodies'];assert unresolved==[78,79,80,83];reached=set(range(85))-set(unresolved);hostfaces=sorted(f for i in reached for f in cs[i]);assert len(hostfaces)==10953;rows=[]
 for i in unresolved:
  fs=cs[i];loop=opening(t,fs);low=t[fs,:,1].min();allatbottom=all(a[1]==b[1]==low for _,a,b in loop);edges=[]
  for sourceface,a,b in loop:
   proof=verify_contact_segment(np.asarray([a,b]),t[hostfaces]);edges.append(dict(originalDetailFace=sourceface,originalBoundaryEdge=[list(a),list(b)],completeReachableOriginalHostScopeFaceIDs=hostfaces,subsetIndexToCompleteOriginalHostFaceIDs=hostfaces,proof=proof))
  row=dict(originalBody=i,completeOriginalFaces=fs,completeOriginalFaceCount=len(fs),completeOriginalLowerOpening=loop,allFourOpeningEdgesAtExactBodyMinimumHeight=allatbottom,completeOriginalOpeningMounts=edges,completeOriginalLowerOpeningWithinExistingFixedBand=allatbottom and all(x['proof']['verifiedCompleteOriginalEdgeContactBand']for x in edges),exactOriginalIntersectionRemainsAbsent=True,closedSolidCertified=False,architecturalRoleIdentity='unresolved',structuralRootCredit=False,structuralBridgeCredit=False,roleApproval=False);rows.append(row);print(json.dumps(dict(body=i,lowerOpening=allatbottom,allEdgesWithinBand=row['completeOriginalLowerOpeningWithinExistingFixedBand'],edges=[x['proof']['verifiedCompleteOriginalEdgeContactBand']for x in edges])),flush=True)
 refs=[ref(q)for q in [Path(__file__),p,OLD/'result.json',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',ROUTE/'result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_segment_surface_contact_band_20261009.py']]
 save(DOC/'diagnostic.json.gz',dict(uids=r['uids'],completeOriginalSourceFaces=11041,completeOriginalWorldSHA256=digest(t.tobytes()),completeOriginalHostScopeFaces=len(hostfaces),completeOriginalHostScopeFaceIDs=hostfaces,hostReachabilityIsConditionalOriginalVisualAssemblyOnly=True,rows=rows,allFourOriginalLowerOpeningsMeetExistingFixedBand=all(x['completeOriginalLowerOpeningWithinExistingFixedBand']for x in rows),rawNoExactContactsChanged=False,sourceOnly=True,currentAcceptance=False,sourceGeometryChanges=0,installationApproved=False,architecturalRoleApproved=False,newlyInstalled=0,evidenceRefs=refs))
if __name__=='__main__':main()
