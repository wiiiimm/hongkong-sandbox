"""DRAFT exact complete494 original terrain overlap attribution, no consolidation."""
from pathlib import Path
from collections import Counter
import numpy as np,json
from run import ROOT,HERE,read,save,digest,connect
from exact_resumable_projected_inventory_v1_20261011 import decoded,encoded
from exact_compute_transition_mesh_v1_20261011 import faces
from exact_original_terrain_overlap_plane_classification_v1_20261011 import classify
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-mongkok-stadium240332-original494-overlap-plane-attribution-v1-20261011';DOC=B/NAME;PRIOR=B/'government-xl-mongkok-stadium240332-actual-native-union-authentic-core-inventory-v2-20261011';SOURCE=HERE/'local'/PRIOR.name/'actual-union-authentic-whole-source-facets.json.gz';METHOD=B/'government-xl-mongkok-stadium240332-adjacent-authentic-tin-method-v1-20261011/METHOD.md'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 d=decoded(read(PRIOR/'diagnostic.json.gz'));s=read(SOURCE);a=np.asarray(s['completeSelectedOriginalFacets'],dtype='<f8');assert a.shape==(14554,3,3)and np.isfinite(a).all()and digest(a.tobytes())==s['completeSelectedOriginalSHA256'];f=faces(a);rows=[];overlaps=d['completeSourceCoreAtomicTopology']['allPositiveOverlaps'];assert len(overlaps)==494
 for i,o in enumerate(overlaps):
  j,k=o['pieces'];c=classify(f[j],f[k]);assert c['exactPositiveProjectedAreaM2']==o['exactPositiveOverlapM2'];rows.append(dict(overlapIndex=i,selectedPieces=[j,k],originalSheetFacetIds=[s['completeSelectedOriginalSheetFacetIds'][j],s['completeSelectedOriginalSheetFacetIds'][k]],**c))
 counts=dict(completePositiveOverlapPairs=len(rows),exactDuplicateUnorderedVertices=sum(x['exactDuplicateUnordered3DVertices']for x in rows),exactCoplanarPairs=sum(x['exactClosedOverlapPlanesIdentical']for x in rows),distinctPlanePairs=sum(not x['exactClosedOverlapPlanesIdentical']for x in rows),distinctPlaneCrossingPairs=sum(x['distinctPlaneHeightsCrossWithinOverlap']for x in rows));refs=[ref(p)for p in[Path(__file__),METHOD,SOURCE,PRIOR/'result.json',PRIOR/'diagnostic.json.gz',HERE/'exact_original_terrain_overlap_plane_classification_v1_20261011.py',HERE/'test_exact_original_terrain_overlap_plane_classification_v1_20261011.py',HERE/'exact_compute_transition_mesh_v1_20261011.py',HERE/'exact_source_core_ten_metre_transition_domain_v1_20261011.py',HERE/'exact_original_projection_coverage_v2_20261010.py']]+s['sourceFiles'];assert all(ref(ROOT/e['path'])==e for e in refs);save(DOC/'diagnostic.json.gz',encoded(dict(uids=['landsd/240332:0','landsd/240527:0'],sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=False,allOriginalFacetsPreserved=True,sourceGeometryChanges=0,liveTerrainChanges=0,completeSelectedSourceFaces=len(f),all494ExactOriginalOverlapPlaneAttributions=rows,summary=counts,raw50FringeCoverageAnd6Invalid4BranchFailuresPreserved=True,consolidationPerformed=False,evidenceRefs=refs,qualification='Exact affine plane attribution only, all494 original source overlap pairs retained. Same-plane/duplicate conclusions are bounded to complete exact closed overlap, do not authorize arbitrary facet deletion or claim full source-height function/support/current/native acceptance. A subsequent coplanar exact union consolidation must prove identical entire closed rendered surface/full coverage/topology/F32 and preserve source provenance. Distinctplanes need source-backed interpretation; adjacent-sheet retrieval does not automatically discharge these independent source obligations.')));print(json.dumps(counts),flush=True)
if __name__=='__main__':main()
