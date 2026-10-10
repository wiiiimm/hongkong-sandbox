"""Every child rectangle edge tested against complete actual parent upper facets."""
import numpy as np
from run import ROOT,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from actual_native_parent_transition_v2_20261010 import height_facet_indices
from exact_native_parent_seam_band_20261010 import verify_seam_segment
BATCH='government-xl-tung-sing-complete-interior-seams-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-tung-sing-actual-parent-interior-composition-v2-20261010/diagnostic.json.gz';CANDIDATE=INPUT.parent/'candidate-single-native-original-surface.json';PARENT=ROOT/'3d-viewer/city/data/government-native-163705-0.json'
def main():
 assert not DOC.exists();x=read(INPUT);original=faces(read(PARENT));parent=original[height_facet_indices(original)];alltri=faces(read(CANDIDATE));child=alltri[x['retainedExactlyEquivalentFacets']:];bb=x['childBounds'];segments={}
 for i,t in enumerate(child):
  for a,b in zip(t,np.roll(t,-1,axis=0)):
   if np.array_equal(a,b):continue
   if any(a[k]==b[k]==v for k,v in [(0,bb[0]),(0,bb[2]),(2,bb[1]),(2,bb[3])]):segments.setdefault(tuple(sorted((tuple(a),tuple(b)))),[]).append(i)
 rows=[]
 for i,(edge,ids) in enumerate(sorted(segments.items())):
  proof=verify_seam_segment(edge,parent);rows.append({'candidateChildFaceIds':ids,'completeSegment':edge,'proof':proof})
  if i%100==0:print({'completeSeamSegmentsChecked':i,'total':len(segments)},flush=True)
 save(DOC/'diagnostic.json.gz',{'completeOriginalParentFacets':len(original),'completeNonzeroProjectedParentFacets':len(parent),'completeCandidateChildFacets':len(child),'completeBoundarySeamSegments':len(rows),'completeClosedBoundaryProofs':rows,'allSegmentsWithinUnchanged2mmBand':bool(rows) and all(r['proof']['verifiedCompleteOriginalEdgeContactBand'] for r in rows),'sourceBuildingGeometryChanges':0,'physicalAccepted':False,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [INPUT,CANDIDATE,PARENT,__import__('pathlib').Path(__file__)]},'qualification':'Exact finite upper-parent envelope evaluated for every complete outer rectangle child edge. Fixed2mm seam band; no source snapping, structural support or physical approval. Exterior original parent facets are independently preserved in the exact finite surface certificate.'});print({'segments':len(rows),'failed':sum(not r['proof']['verifiedCompleteOriginalEdgeContactBand'] for r in rows)},flush=True)
if __name__=='__main__':main()
