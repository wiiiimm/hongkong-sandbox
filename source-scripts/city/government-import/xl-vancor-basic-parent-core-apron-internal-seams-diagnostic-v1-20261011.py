"""Independent complete internal packed upper-branch seams; no acceptance."""
import importlib.util,json
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from native_parent_child_flat_composition_20261010 import faces
from exact_native_upper_surface_pair_seam_v3_20261010 import verify_pair
BASE=ROOT/'docs/astra-city/government-import'
PROPOSAL=BASE/'government-xl-vancor-basic-parent-core-apron-terrain-proposal-v2-20261011'
BATCH='government-xl-vancor-basic-parent-core-apron-internal-seams-diagnostic-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(PROPOSAL/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 diagnostic=read(PROPOSAL/'diagnostic.json.gz');assert ref(PROPOSAL/'diagnostic.json.gz')in receipt['evidenceRefs']
 path=ROOT/diagnostic['changedTerrainProposal']['path'];assert ref(path)==diagnostic['changedTerrainProposal']and ref(path)in receipt['evidenceRefs']
 full=faces(read(path));proof=diagnostic['proof'];n=proof['completeOriginalCandidateFaces'];assert n==2859 and len(full)==proof['finalTerrainFacets']==3449
 assigned={'core':[],'apron':[],'zero-collar':[]}
 for record in proof['completeOriginalParentFacetDispositions']:
  for fragment in record['completeFiniteClipDispositions']:
   ids=fragment['output']['newCandidateFaceIds'] if isinstance(fragment['output'],dict)else []
   assigned[fragment['region']].extend(ids)
 all_ids=sum(assigned.values(),[]);assert len(all_ids)==len(set(all_ids))and sorted(all_ids)==list(range(n,len(full)))
 core=shapely.from_geojson(proof['actualProtectedCoreGeoJSON']);blend_outer=core.buffer(proof['declaredBlendWidthM'],join_style='mitre');assert proof['declaredBlendWidthM']==.008 and proof['declaredZeroAlphaCollarWidthM']==.002
 rows=[]
 for name,geometry,left,right in [('core-to-blend',core,'core','apron'),('blend-to-zero-collar',blend_outer,'apron','zero-collar')]:
  # Baseline is the unchanged literal prefix on BOTH sides. Every appended
  # region facet is independently assigned once, including zero projections.
  a=np.concatenate([full[:n],full[assigned[left]]]);b=np.concatenate([full[:n],full[assigned[right]]])
  for ring_id,ring in enumerate([geometry.exterior,*geometry.interiors]):
   coords=list(ring.coords)
   for edge_id,(p,q)in enumerate(zip(coords,coords[1:])):
    rows.append(dict(boundary=name,ring=ring_id,edge=edge_id,leftRegion=left,rightRegion=right,completeFiniteUpperSeam=verify_pair(np.asarray([[p[0],0,p[1]],[q[0],0,q[1]]]),a,b)))
 out=dict(proposal=ref(PROPOSAL/'diagnostic.json.gz'),candidate=ref(path),completeTerrainFaces=len(full),completeRegionFaceIds=assigned,allAddedFacesAssignedExactlyOnce=True,completeInternalBoundaryEdges=rows,allInternalUpperSeamsWithinUnchanged2mm=all(r['completeFiniteUpperSeam']['passedCompleteFiniteUpperSeam']for r in rows),strictBandM=.002,sourceGeometryChanges=0,currentAcceptance=False,installationApproved=False,qualification='Exact finite upper branch comparisons at every exterior and interior edge of the declared unrounded internal boundaries. This is a separate diagnostic, not full 2D domain/current physical acceptance. Raw packed gaps are retained.')
 save(DOC/'diagnostic.json.gz',out)
 refs=[Path(__file__),PROPOSAL/'result.json',PROPOSAL/'diagnostic.json.gz',path,HERE/'exact_native_upper_surface_pair_seam_v3_20261010.py',HERE/'native_parent_child_flat_composition_20261010.py']
 spec=importlib.util.spec_from_file_location('vancor_internal_seams_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'changed-terrain-complete-internal-upper-seams-diagnostic-v1',refs,dict(uids=['landsd/147956:0','landsd/253697:0'],allInternalUpperSeamsWithinUnchanged2mm=out['allInternalUpperSeamsWithinUnchanged2mm'],currentAcceptance=False,newlyInstalled=0))
 print(json.dumps(dict(edges=len(rows),internalSeamsPassed=out['allInternalUpperSeamsWithinUnchanged2mm'],currentAcceptance=False)))
if __name__=='__main__':main()
