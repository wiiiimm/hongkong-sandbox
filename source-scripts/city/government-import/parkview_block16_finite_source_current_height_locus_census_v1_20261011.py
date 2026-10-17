"""DRAFT source-only finite exact overlay/equal-height context, no candidate."""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest
from native_patch_resolution import _faces
from exact_finite_source_current_height_locus_v1_20261011 import locus
from exact_source_planar_domain_recovery_seams_v1_20261011 import projected
from exact_original_projection_coverage_v2_20261010 import signed_area
B=ROOT/'docs/astra-city/government-import';AUTH=B/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3';OLD=B/'government-xl-parkview-block16-two-parent-facet-source-planar-proposal-v1-20261011';DOC=B/'government-xl-parkview-block16-finite-source-current-height-locus-census-v1-20261011';INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def strings(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:strings(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [strings(v)for v in x]
 return x

def main():
 assert not DOC.exists();oldproof=read(OLD/'diagnostic.json.gz');assert oldproof['localTerrainProposalWritten']is False
 refs=[ref(p)for p in [Path(__file__),INSTALLED,OLD/'diagnostic.json.gz',OLD/'result.json',AUTH/'diagnostic.json.gz',AUTH/'result.json',HERE/'pending-context.py',HERE/'native_patch_resolution.py',HERE/'exact_finite_source_current_height_locus_v1_20261011.py',HERE/'test_exact_finite_source_current_height_locus_v1_20261011.py',HERE/'exact_source_planar_domain_recovery_seams_v1_20261011.py',HERE/'exact_original_projection_coverage_v2_20261010.py']];current=_faces(read(INSTALLED));assert len(current)==94794 and ref(INSTALLED)['sha256']=='12816eebe4f6600fd13a41a897bfd9c044e2a7ac5edf0dde0d7d76647642f1d6'
 spec=importlib.util.spec_from_file_location('block16_primary_tin_context',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);parts=[]
 for sheet in ['11-SE-21B','11-SE-16D']:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;receiptpath=folder/'original/download.json';receipt=read(receiptpath);directory=folder/'directory/result.json';assert receipt['directorySHA256']==read(directory)['directorySHA256'];refs.extend([ref(receiptpath),ref(directory)]);gltfs=[]
  for ent in receipt['entries']:
   if ent['name'].startswith('TERRAIN')and ent['name'].endswith(('.gltf','.bin')):
    p=folder/'terrain'/ent['name'];assert digest(p.read_bytes())==ent['sha256'];refs.append(ref(p))
    if p.suffix=='.gltf':gltfs.append(p)
  assert gltfs;parts.extend(context.triangles(p)for p in sorted(gltfs))
 terrain=np.concatenate(parts);auth=next(r for r in read(AUTH/'diagnostic.json.gz')['rows']if r['uid']=='landsd/254491:0');assert len(terrain)==auth['authenticWholeSourceTerrainTriangles']==394774 and digest(terrain.tobytes())==auth['authenticWholeSourceTerrainSHA256'];assert digest(terrain.tobytes())=='740580e8f1bd38cddc48b956f5ca161de7fcebac2852d887d02ad60c1178cff5'
 sid=oldproof['completeSourceCandidateOriginalTINIds'];rid=oldproof['completeRetainedCandidateInstalledFacetIds'];assert len(sid)==150 and len(rid)==191 and len(set(sid))==150 and len(set(rid))==191
 domains=current[[94641,94645]];lo,hi=domains[:,:,[0,2]].min((0,1)),domains[:,:,[0,2]].max((0,1))
 def candidates(faces):
  xz=faces[:,:,[0,2]];return np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1)).tolist()
 assert candidates(terrain)==sid
 assert [i for i in candidates(current)if i not in [94641,94645]]==rid
 rows=[];pairCount=0;counts=Counter();sxz=terrain[sid][:,:,[0,2]];cxz=current[rid][:,:,[0,2]];clo,chi=cxz.min(1),cxz.max(1)
 for si,fid in enumerate(sid):
  ids=np.flatnonzero(np.all(chi>=sxz[si].min(0),axis=1)&np.all(clo<=sxz[si].max(0),axis=1)).tolist()
  for ri in ids:
   pairCount+=1;assert pairCount<=28650,'Complete bounded pair inventory; never truncate';nid=rid[ri];proof=locus(terrain[fid],current[nid]);counts[proof['classification']]+=1
   if proof['classification']=='equal-plane-finite-overlay':
    # Finite full-area containment, not a boundary/point coincidence. Context
    # only; topology, original winding, attribution and support remain separate.
    proof['entireCurrentFacetContainedInThisFiniteOriginalSourcePlane']=proof['exactAreaM2']==abs(signed_area(projected(current[nid])))
   rows.append(dict(originalTINFacet=fid,currentNativeFacet=nid,originalFacetSHA256=digest(terrain[fid].tobytes()),currentFacetSHA256=digest(current[nid].tobytes()),proof=strings(proof)))
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,nativeReacceptance=False,terrainProposalWritten=False,sourceGeometryChanges=0,terrainChanges=0,completeOriginalTINWorldSHA256=digest(terrain.tobytes()),completeSourceCandidateOriginalTINIds=sid,completeRetainedCandidateInstalledFacetIds=rid,completeSourceCurrentProjectedAABBPairs=pairCount,counts=dict(counts),rows=rows,evidenceRefs=refs,qualification='Exact finite overlay/equal-height context only. Full finite coplanar containment is recorded separately from segment/point equality. No complete domain/frontier, outside-side, internal/F32 incidence/overlap/winding, primary provenance beyond recorded pair, structural support, qualified cap/root, retention discharge or affected17/native/foreign obligation credit. No candidate. Source reconstructs original doubles; arithmetic projection is not an actual F32 seam proof. Fixed exact installed terrain bytes are independently fenced; no live currentmanifest claim. All prior raw failures preserved.'))
 print(json.dumps(dict(completeSourceCurrentProjectedAABBPairs=pairCount,counts=dict(counts),terrainProposalWritten=False,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
