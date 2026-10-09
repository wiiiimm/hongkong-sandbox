"""Complete original downward details and exact source roof counterparts."""
import collections,json
import numpy as np
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_source_surface_contact_band_20261009 import verify_contact
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261009-118230-original-underside-counterparts-v2';DOC=BASE/BATCH
def main():
 assert not DOC.exists();g=read(BASE/'xl-terrain-recovery-20261009-118230-original-world-current-support-v1/diagnostic.json.gz');role=read(BASE/'xl-terrain-recovery-20261009-118230-current-roof-perimeter-role-v1/typed-role.json.gz');row=read(BASE/'government-xl-terrain-recovery-harbourfront-boundary-nested-physical-v3-20261009/selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();tri=decode_original_world_triangles(raw);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratio=np.divide(normal[:,1],length,out=np.zeros(len(length)),where=length>0);byface={i:k for k,c in enumerate(g['components']) for i in c['globalOriginalFaces']};rooted=set(role['resolvedOriginalComponents']);roofids=sorted(i for i,k in byface.items() if k in rooted and ratio[i]>.25);exactxy=collections.defaultdict(list)
 for i in roofids:exactxy[tuple(sorted(tuple(p) for p in tri[i][:,[0,2]]))].append(i)
 parts=[]
 for k in [330,332,444]:
  ids=g['components'][k]['globalOriginalFaces'];down=[i for i in ids if ratio[i]<-.25];faces=[]
  for i in down:
   lo=tri[i][:,[0,2]].min(axis=0);hi=tri[i][:,[0,2]].max(axis=0);near=[j for j in roofids if np.all(tri[j][:,[0,2]].max(axis=0)>=lo) and np.all(tri[j][:,[0,2]].min(axis=0)<=hi)];proof=verify_contact(tri[i],tri[near]);pieces=[dict(originalSourceFace=near[p['originalGroundFace']],originalComponent=byface[near[p['originalGroundFace']]],originalNormalYRatio=float(ratio[near[p['originalGroundFace']]]),exactGapRangeM=[p['exactMinimumGapM'],p['exactMaximumGapM']]) for p in proof['allOriginalIntersectingPlanePieces']];faces.append(dict(sourceFace=i,completeOriginalVertices=tri[i].tolist(),normalYRatio=float(ratio[i]),exactMatchingProjectedTriangleFaces=exactxy.get(tuple(sorted(tuple(p) for p in tri[i][:,[0,2]])),[]),allIntersectingRootedUpwardFacets=pieces,completeFiniteProjectionCoveredByRootedUpwardFacets=proof['exactProjectionCoverage']['exactProjectionCovered'],existingBandAccepted=proof['verifiedCompleteFacetContactBand']))
  parts.append(dict(component=k,completeOriginalFaces=ids,completeOriginalDownwardFaces=down,everyOriginalDownwardFace=faces,allDownwardProjectionCovered=all(r['completeFiniteProjectionCoveredByRootedUpwardFacets'] for r in faces),noSupportOrOcclusionCredit=True))
  print(json.dumps(dict(component=k,downwardFaces=len(down),exactXYMatching=sum(bool(r['exactMatchingProjectedTriangleFaces']) for r in faces),covered=parts[-1]['allDownwardProjectionCovered'],counterpartComponents=sorted(set(p['originalComponent'] for f in faces for p in f['allIntersectingRootedUpwardFacets'])))),flush=True)
 save(DOC/'diagnostic.json.gz',dict(sourceSHA256=digest(raw),completeOriginalWorldSHA256=digest(tri.tobytes()),independentlyRootedComponents=sorted(rooted),completeRootedUpwardFacetScope=roofids,everyInvestigatedPart=parts,sourceGeometryChanges=0,structuralRootCredit=False,fullAcceptance=False,installationApproved=False))
if __name__=='__main__':main()
