"""Trace exact prepack interfaces into actual packed edges; diagnostic only.

The declared-boundary seam negative remains immutable. This locates whether
its cause is a real packed gap or evaluation on the unrounded source line.
"""
import importlib.util,json
from fractions import Fraction as F
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from native_parent_child_flat_composition_20261010 import faces
from actual_native_parent_transition_v3_20261010 import nondegenerate
from exact_original_polygon_triangle_partition_20261010 import on_segment
from exact_finite_upper_surface_cells_20261011 import area as exact_projected_area
from exact_native_upper_surface_pair_seam_v3_20261010 import verify_pair
BASE=ROOT/'docs/astra-city/government-import';PROPOSAL=BASE/'government-xl-vancor-basic-parent-core-apron-terrain-proposal-v4-20261011';FAILED=BASE/'government-xl-vancor-basic-parent-core-apron-internal-seams-diagnostic-v1-20261011'
BATCH='government-xl-vancor-basic-parent-core-apron-packed-interfaces-diagnostic-v3-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipts=[read(p/'result.json')for p in [PROPOSAL,FAILED]]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,r in zip([PROPOSAL,FAILED],receipts):assert ref(p/'diagnostic.json.gz')in r['evidenceRefs']
 d=read(PROPOSAL/'diagnostic.json.gz');proof=d['proof'];path=ROOT/d['changedTerrainProposal']['path'];assert ref(path)==d['changedTerrainProposal']and ref(path)in receipts[0]['evidenceRefs'];full=faces(read(path));n=proof['completeOriginalCandidateFaces'];assert n==2859 and len(full)==proof['finalTerrainFacets']<=100000 and len(full)-n==proof['completeAddedTerrainFaces']
 core=shapely.from_geojson(proof['actualProtectedCoreGeoJSON']);assert proof['declaredBlendWidthM']==.008 and proof['declaredZeroAlphaCollarWidthM']==.002
 boundaries={}
 for name,g in [('core-to-blend',core),('blend-to-zero-collar',core.buffer(.008,join_style='mitre'))]:
  boundaries[name]=[(ri,ei,tuple(F(float(v))for v in a),tuple(F(float(v))for v in b))for ri,ring in enumerate([g.exterior,*g.interiors])for ei,(a,b)in enumerate(zip(list(ring.coords),list(ring.coords)[1:]))]
 assigned={'core':[],'apron':[],'zero-collar':[]};interfaces=[];all_ids=[];boundary_only=[]
 for record in proof['completeOriginalParentFacetDispositions']:
  for fragment in record['completeFiniteClipDispositions']:
   output=fragment['output']
   if not isinstance(output,dict):assert output==[];continue
   if not output:
    assert fragment['exactZeroProjectedBoundaryOnly']
    exact_boundary=[tuple(F(x)for x in p)for p in fragment['exactFiniteClipVertices']]
    assert exact_projected_area(exact_boundary)==0
    boundary_only.append(dict(originalParentFace=record['originalParentFace'],region=fragment['region'],exactBoundaryVertices=fragment['exactFiniteClipVertices'],heightOrSupportCredit=False));continue
   v=output['completePrepackVertices'];exact=[tuple(F(x)for x in p['exactParentClipVertex'])for p in v];packed=[p['packedFloat32Vertex']for p in v]
   fans=output['completeVertexFanIndices'];ids=output['newCandidateFaceIds'];assert len(fans)==len(ids)
   assert all(len(f)==3 and all(0<=i<len(v)for i in f)and nondegenerate([exact[i]for i in f])for f in fans)
   for fid,fan in zip(ids,fans):
    assert np.array_equal(full[fid],np.asarray([packed[i]for i in fan],dtype=float)),'Packed face differs from immutable constructor vertex inventory';assigned[fragment['region']].append(fid);all_ids.append(fid)
    for name,lines in boundaries.items():
     eligible={'core','apron'}if name=='core-to-blend'else{'apron','zero-collar'}
     if fragment['region']not in eligible:continue
     for i,j in zip(fan,fan[1:]+fan[:1]):
      p,q=(exact[i][0],exact[i][2]),(exact[j][0],exact[j][2])
      for ri,ei,a,b in lines:
       if on_segment(a,b,p)and on_segment(a,b,q):interfaces.append(dict(boundary=name,region=fragment['region'],originalParentFace=record['originalParentFace'],packedCandidateFace=fid,ring=ri,declaredEdge=ei,exactPrepackEdge=[[str(x)for x in exact[k]]for k in [i,j]],actualPackedEdge=[packed[i],packed[j]],prepackProjectedPoint=p==q))
 assert len(all_ids)==len(set(all_ids))and sorted(all_ids)==list(range(n,len(full)))
 side={r:np.concatenate([full[:n],full[ids]])for r,ids in assigned.items()}
 for row in interfaces:
  left,right=('core','apron')if row['boundary']=='core-to-blend'else('apron','zero-collar');row['completeActualPackedUpperSeam']=verify_pair(np.asarray(row['actualPackedEdge']),side[left],side[right])
 out=dict(proposal=ref(PROPOSAL/'diagnostic.json.gz'),preservedDeclaredBoundaryFailure=ref(FAILED/'diagnostic.json.gz'),candidate=ref(path),completeAddedFacetsReconstructedExactlyFromFrozenVertexInventory=True,completeRegionFaceIds=assigned,completeExactZeroProjectedBoundaryOnlyRecords=boundary_only,completePackedInterfaceEdges=interfaces,allPackedInterfaceUpperSeamsWithinUnchanged2mm=bool(interfaces)and all(r['completeActualPackedUpperSeam']['passedCompleteFiniteUpperSeam']for r in interfaces),strictBandM=.002,sourceGeometryChanges=0,currentAcceptance=False,installationApproved=False,qualification='Every original parent fragment/fan is independently reconstructed into the exact frozen packed face. The explicit complete centre-fan index stream is verified without assuming an old fan topology. Both sides of every exact prepack boundary edge are checked on its ACTUAL packed segment, with the literal original candidate prefix retained. The prior unrounded-line negative is preserved. This is a cause diagnostic, not complete area-domain or physical acceptance; collapsed/point edges are retained without structural credit.')
 save(DOC/'diagnostic.json.gz',out)
 refs=[Path(__file__),path,*[p/'result.json'for p in [PROPOSAL,FAILED]],*[p/'diagnostic.json.gz'for p in [PROPOSAL,FAILED]],HERE/'actual_native_parent_transition_v3_20261010.py',HERE/'exact_finite_upper_surface_cells_20261011.py',HERE/'native_parent_child_flat_composition_20261010.py',HERE/'exact_original_polygon_triangle_partition_20261010.py',HERE/'exact_native_upper_surface_pair_seam_v3_20261010.py']
 spec=importlib.util.spec_from_file_location('vancor_packed_interface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'changed-terrain-upper-cells-branch-local-actual-packed-internal-interface-cause-diagnostic-v3',refs,dict(uids=['landsd/147956:0','landsd/253697:0'],allPackedInterfaceUpperSeamsWithinUnchanged2mm=out['allPackedInterfaceUpperSeamsWithinUnchanged2mm'],currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(interfaces=len(interfaces),packedSeamsPassed=out['allPackedInterfaceUpperSeamsWithinUnchanged2mm'],currentAcceptance=False)))
if __name__=='__main__':main()
