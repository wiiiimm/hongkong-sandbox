"""Candidate-only literal original parent restoration for two disjoint basic forms."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from native_parent_child_flat_composition_20261010 import faces
from whole_source_disjoint_literal_parent_facets_20261010 import propose
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-literal-disjoint-parent-candidate-20261010'
PHYS=DOC.parent/'government-xl-tung-sing-two-flat-original-physical-v4-20261010'
SOURCES=DOC.parent/'government-xl-source-neighbour-recovery-leads-20261010/selection.json.gz'
DIAG=DOC.parent/'government-xl-tung-sing-three-basic-source-intersections-20261010/diagnostic.json.gz'
def main():
 assert not DOC.exists();parentpath=ROOT/'3d-viewer/city/data/government-native-163705-0.json';parent=read(parentpath);assert digest(parentpath.read_bytes())=='b713f279439f89c3bf50b21623c41e18cb0859eca85ca2854851d8cf429b1e57';candidate_row=read(PHYS/'terrain-candidates.json')[0];path=ROOT/candidate_row['path'];assert digest(path.read_bytes())==candidate_row['sha256'];candidate=read(path);selection=read(PHYS/'selection.json.gz')['rows'];commercial=next(r for r in read(SOURCES)['rows'] if r['uid']=='landsd/254604:0');selection.append(commercial);models={};inputs=[Path(__file__),parentpath,path,PHYS/'terrain-candidates.json',PHYS/'selection.json.gz',SOURCES,DIAG,HERE/'whole_source_disjoint_literal_parent_facets_20261010.py',HERE/'test_whole_source_disjoint_literal_parent_facets_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']
 for r in selection:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];models[r['uid']]=decode_original_world_triangles(raw);inputs.append(p)
 forms=[r['completeCurrentBuilding'] for r in read(DIAG)['rows'] if r['uid'] in ['landsd/124952:0','landsd/341948:0']];out,proof=propose(candidate,parent,models,forms,digest(faces(parent).astype('<f8').tobytes()));proof['inputHashes']={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in inputs};proof['originalThreeActorRegressionUID']='landsd/254604:0';proof['originalDetachedTowerComponentsRemainHeld']=[343,344];proof['noPhysicalOrInstallationAcceptance']=True
 # Changed mesh invalidates the previous overlap receipt; preserve it as raw provenance, not current credit.
 old=out['nativeMesh'].pop('sourceOverlap',None);proof['previousCandidateOverlapApprovalRetainedHistorically']=old;out['nativeMesh']['source']['literalDisjointParentProposal']={'evidencePath':str((DOC/'diagnostic.json.gz').relative_to(ROOT)),'physicalAccepted':False}
 save(DOC/'candidate-native-terrain.json',out);save(DOC/'diagnostic.json.gz',proof);print({'facets':proof['finalCandidateFacets'],'literalOriginalParentFaces':[r['originalParentFace'] for r in proof['allRetainedLiteralParentFacetDispositions']],'models':proof['completeSourceFaceCounts'],'physicalAccepted':False},flush=True)
if __name__=='__main__':main()
