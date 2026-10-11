"""Complete parent/child count and actual-parent seam negatives, no acceptance."""
import importlib.util,numpy as np
from run import ROOT,HERE,read,save,digest
from native_parent_child_flat_composition_20261010 import compose,bounds,faces
from rendered_patch_sampler import RenderedPatchSampler
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-flat-parent-child-census-20261010'
PARENT=ROOT/'3d-viewer/city/data/government-native-163705-0.json'
CHILD=HERE/'local/government-xl-tung-sing-two-nested-original-physical-v3-20261010/government-native-53800-0.json'
def main():
 assert not DOC.exists();parent=read(PARENT);child=read(CHILD);candidate,census=compose(parent,child);save(DOC/'complete-parent-face-census.json.gz',census)
 s=importlib.util.spec_from_file_location('flat_parent_drawn_sampler',HERE/'xl-second-pass.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);grand=read(ROOT/'3d-viewer/city/data/terrain.json');sampler=RenderedPatchSampler(parent,m.resolution.terrain.fine.DemSampler(grand,rendered=True),m.resolution.terrain.fine.DemSampler(parent,rendered=True));cb=bounds(child);vertices=np.unique(faces(child).reshape(-1,3),axis=0);edge=vertices[(vertices[:,0]==cb[0])|(vertices[:,0]==cb[2])|(vertices[:,2]==cb[1])|(vertices[:,2]==cb[3])];records=[{'actualChildRuntimeVertex':v.tolist(),'actualNativeParentHeightHKPD':sampler.ground(v[0],v[2]),'gapM':float(v[1]-sampler.ground(v[0],v[2]))} for v in edge]
 save(DOC/'seam-vertex-counterexamples.json.gz',{'rows':records,'completeUniqueBoundaryVertices':len(edge),'maximumActualNativeParentVertexGapM':max(abs(r['gapM']) for r in records),'fullFiniteSeamAccepted':False,'outsideEquivalenceAccepted':False,'inputHashes':{str(PARENT.relative_to(ROOT)):digest(PARENT.read_bytes()),str(CHILD.relative_to(ROOT)):digest(CHILD.read_bytes())},'qualification':'Actual native parent Float32 triangle sampler, not grid fallback. Vertex evidence can disprove a seam; even a positive vertex check cannot approve whole finite boundary segments.'})
 print({'fullCombinedFaces':census['fullCombinedFaces'],'within100k':census['withinUnchangedRuntimeBudget'],'retainedVerticalFaces':len(census['allRetainedVerticalOriginalFaceIds']),'seamVertices':len(edge),'actualNativeParentMaxVertexGapM':max(abs(r['gapM']) for r in records),'accepted':False},flush=True)
if __name__=='__main__':main()
