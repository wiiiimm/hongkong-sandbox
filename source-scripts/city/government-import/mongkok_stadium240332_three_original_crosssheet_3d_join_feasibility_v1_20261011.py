"""DRAFT exact nomination ONLY for three proven source boundary intervals."""
from pathlib import Path
import numpy as np,json
from run import ROOT,HERE,read,save,digest,connect
from exact_resumable_projected_inventory_v1_20261011 import decoded,encoded
from exact_compute_transition_mesh_v1_20261011 import faces,height
from exact_shared_3d_segment_intervals_v1_20261011 import overlap,covered
from exact_original_boundary_vertical_join_feasibility_v1_20261011 import nominate
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-mongkok-stadium240332-three-original-crosssheet-3d-join-feasibility-v1-20261011';DOC=B/NAME;METHOD=B/(NAME+'-method')/'METHOD.md';FRINGE=B/'government-xl-mongkok-stadium240332-adjacent15c-complete-fringe-coverage-crosssheet-seams-v1-20261011';GRAPH=B/'government-xl-mongkok-stadium240332-original14d-whole3d494-component-context-v1-20261011';OLD=B/'government-xl-mongkok-stadium240332-actual-native-union-authentic-core-inventory-v2-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(folder):
 r=read(folder/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 return r
def boundary(a,b,face):
 parts=[]
 for u,v in zip(face,face[1:]+face[:1]):
  q=overlap(a,b,u,v)
  if q is not None:parts.append(q)
 assert covered(parts),'Proposed source join interval must be entire positive actual original triangle boundary'
 return parts
def main():
 assert not DOC.exists();receipts=[verify(p)for p in[FRINGE,GRAPH,OLD]];d=decoded(read(FRINGE/'diagnostic.json.gz'));oldfile=HERE/'local'/OLD.name/'actual-union-authentic-whole-source-facets.json.gz';newfile=HERE/'local'/FRINGE.name/'complete-original15c-sheet-world.json.gz';o=read(oldfile);n=read(newfile);a=np.asarray(o['completeSelectedOriginalFacets'],dtype='<f8');z=np.asarray(n['allWholeOriginalSheetFacets'],dtype='<f8');assert a.shape==(14554,3,3)and z.shape==(48930,3,3)and digest(a.tobytes())==o['completeSelectedOriginalSHA256']and digest(z.tobytes())==n['completeOriginalSheetWorldSHA256']==d['original15cSheetWorldSHA256'];mapping={j:i for i,j in enumerate(o['completeSelectedOriginalSheetFacetIds'])};rows=[];intervals=d['allPositiveCrossSheetBoundaryInterfaceHeightProofs'];assert len(intervals)==3
 for i,r in enumerate(intervals):
  old=faces(a[mapping[r['original14dFacetId']]:mapping[r['original14dFacetId']]+1])[0];new=faces(z[r['original15cFacetId']:r['original15cFacetId']+1])[0];p,q=r['allExactProjectedInterfaceEndpoints'];oldends=[(v[0],height(old,v),v[1])for v in[p,q]];newends=[(v[0],height(new,v),v[1])for v in[p,q]];assert [n[1]-o[1]for n,o in zip(newends,oldends)]==r['allExactEndpointHeightDifferencesM'];old_parts=boundary(*oldends,old);new_parts=boundary(*newends,new);proposal=nominate(*oldends,*newends);rows.append(dict(originalBoundaryProof=r,completeOldOriginalBoundaryIntervals=old_parts,completeNewOriginalBoundaryIntervals=new_parts,**proposal))
 refs=[ref(p)for p in[Path(__file__),METHOD,oldfile,newfile,HERE/'exact_original_boundary_vertical_join_feasibility_v1_20261011.py',HERE/'test_exact_original_boundary_vertical_join_feasibility_v1_20261011.py',HERE/'exact_shared_3d_segment_intervals_v1_20261011.py',HERE/'test_exact_shared_3d_segment_intervals_v1_20261011.py',HERE/'exact_compute_transition_mesh_v1_20261011.py']]+[ref(folder/n)for folder in[FRINGE,GRAPH,OLD]for n in['result.json','diagnostic.json.gz']]+o['sourceFiles']+n['sourceFiles'];assert all(ref(ROOT/e['path'])==e for e in refs);assert all(verify(folder)==r for folder,r in zip([FRINGE,GRAPH,OLD],receipts));save(DOC/'diagnostic.json.gz',encoded(dict(uids=['landsd/240332:0','landsd/240527:0'],sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=False,meshFilesCreated=False,originalSourcePositionChanges=0,liveTerrainChanges=0,allThreeExactSourceBoundaryJoinNominations=rows,evidenceRefs=refs,qualification='Only three proven positive finite original source boundary intervals. Every generated nominee retains both independently exact original3D boundary curves, splitting any sign change exactly. Zero-area nominees get no area credit. Not a complete merged boundary or terrain candidate: original91proper crossings/494distinctplanes/6incidence/4branch failures and three rational gaps remain. Original facet winding/source-piece internal/F32 seams, all other source boundary intervals, actual complete actor finite/vertical-ground/water/runtime guards unresolved. No 2.5D predicate relabelling, source-snap/deletion, manufactured architectural intent or installed credit.')));print(json.dumps(dict(intervals=3,positiveGeneratedNominees=sum(len(r['allPositiveGeneratedJoinFaces'])for r in rows),currentAcceptance=False)))
if __name__=='__main__':main()
