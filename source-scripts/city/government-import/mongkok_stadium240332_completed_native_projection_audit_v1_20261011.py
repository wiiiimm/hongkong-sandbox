"""DRAFT complete native-only audit of preserved interrupted-v3 checkpoints."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_compute_transition_mesh_v1_20261011 import faces,project
from exact_resumable_projected_inventory_v1_20261011 import Checkpoints,overlaps,encoded
from exact_original_projection_coverage_v2_20261010 import signed_area
NAME='government-xl-mongkok-stadium240332-completed-native-projection-audit-v1-20261011';B=ROOT/'docs/astra-city/government-import';DOC=B/NAME;OLDLOCAL=HERE/'local/government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v3-20261011';PRE=B/'government-xl-mongkok-stadium240332-ten-metre-clipped-transition-candidate-v1-20261011';ARCHIVE=HERE/'local/government-xl-mongkok-stadium240332-actual-current-byte-archives-v1-20261011/manifest-actual-d152dca4.json';PIN='d152dca423d23b3bdb21a06786dd01980a5ab86b8bab75646d2ee6cd0a387c43'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
class CachedOnly(Checkpoints):
 def map(self,label,items,compute):
  assert label=='positive-overlap-pairs'and len(items)==919570
  assert all((self.folder/label/f'{start:09d}-{min(start+self.chunk_size,len(items)):09d}.json.gz').is_file()for start in range(0,len(items),self.chunk_size))
  def forbidden(part):raise AssertionError('Native audit cannot recompute a missing chunk')
  return super().map(label,items,forbidden)
def main():
 assert not DOC.exists();r=read(PRE/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs=[]
 for e in r['evidenceRefs']:
  if e==dict(path='3d-viewer/city/data/manifest.json',sha256=PIN):assert ref(ARCHIVE)['sha256']==PIN;refs.append(ref(ARCHIVE))
  else:assert ref(ROOT/e['path'])==e;refs.append(e)
 entry=next(e for e in read(ARCHIVE)['terrainPatches']if e['url']=='city/data/government-native-240527-0.json');p=ROOT/'3d-viewer'/entry['url'];assert ref(p)['sha256']==entry['sha256'];patch=read(p);assert patch['meta']['targetUids']==['landsd/240527:0']and patch['coarseCells']==[510,388,514,390];raw=patch['nativeMesh'];position=np.asarray(raw['position'],dtype='<f4').reshape(-1,3);index=np.asarray(raw['index'],dtype='<u4').reshape(-1,3)
 for i,f in enumerate(index):
  a,b,c=position[f].astype('<f8');y=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])
  if y<0:index[i,1],index[i,2]=index[i,2],index[i,1]
 mesh=read(PRE/'complete-current-ground.json.gz')['completeGlobalActualMeshes'][175];assert len(index)==16297 and digest(position.tobytes())==mesh['actualPositionAttributeSHA256']and digest(index.tobytes())==mesh['actualIndexAttributeSHA256'];native=position[index].astype('<f8');af=faces(native);zeros=[i for i,f in enumerate(af)if not signed_area([(q[0],q[2])for q in f])];assert not zeros;polys=[project(f)for f in af];bindings=[ref(ARCHIVE),ref(p),ref(HERE/'mongkok_stadium240332_merged_protected_patch_authentic_core_inventory_v3_20261011.py')]+[ref(HERE/n)for n in ['exact_resumable_projected_inventory_v1_20261011.py','exact_compute_transition_mesh_v1_20261011.py','exact_source_core_ten_metre_transition_domain_v1_20261011.py','exact_original_projection_coverage_v2_20261010.py','exact_atomic_terrain_domain_boundary_ring_v1_20261011.py','run.py']]
 def check():assert all(ref(ROOT/e['path'])==e for e in bindings)
 assert(OLDLOCAL/'native-projection-checkpoints/contract.json.gz').is_file();cp=CachedOnly(OLDLOCAL/'native-projection-checkpoints',polys,bindings,check);bad,counters=overlaps(polys,cp);assert len(bad)==771 and counters['completeClosedBucketCandidatePairs']==919570;summed=sum(signed_area(p)for p in polys);lo=native.min((0,1));hi=native.max((0,1));assert [lo[0],lo[2],hi[0],hi[2]]==[1232.5,-4307.5,1512.5,-4167.5];check();refs.extend(bindings);refs.extend(ref(q)for q in OLDLOCAL.rglob('*.json*')if q.is_file()and not q.name.endswith('.tmp'));refs.extend(ref(q)for q in [Path(__file__),HERE/'test_exact_resumable_projected_inventory_v1_20261011.py',HERE/'local/government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v1-20261011/supervised-interrupted-attempt.json',HERE/'local/government-xl-mongkok-stadium240332-merged-protected-patch-authentic-core-inventory-v2-20261011/supervised-interrupted-attempt.json',PRE/'result.json',PRE/'diagnostic.json.gz',PRE/'complete-current-ground.json.gz',B/'government-xl-mongkok-stadium240332-completed-native-projection-audit-method-v1-20261011/METHOD.md']);assert all(ref(ROOT/e['path'])==e for e in refs)
 save(DOC/'diagnostic.json.gz',encoded(dict(uid='landsd/240332:0',protectedUID='landsd/240527:0',sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=False,sourceGeometryChanges=0,liveTerrainChanges=0,historicalCapturedBaselineOnly=True,completeNativeFacets=16297,zeroProjectedNativeFacetIds=zeros,nativeWorldSHA256=digest(native.tobytes()),nativePositionSHA256=digest(position.tobytes()),nativeIndexSHA256=digest(index.tobytes()),completeNativePairAccounting=counters,allExactPositiveNativeProjectedOverlaps=bad,completeNativeProjectedAreaSumM2=summed,actualNativeContainingXZBounds=[lo[0],lo[2],hi[0],hi[2]],nativePerfectRectangleFootprintQualified=False,sourceCoverageOrTopologyCompleted=False,partialSourceChunksAreAuditOnly=True,protected240527RegressionsDischarged=False,historicalManifestBinding=dict(originalPath='3d-viewer/city/data/manifest.json',historicalSHA256=PIN,actualArchive=ref(ARCHIVE)),evidenceRefs=list({(e['path'],e['sha256']):e for e in refs}.values()),qualification='Complete native-only919570-pair preserved checkpoint audit,771 exact positive native overlaps. Original fullsource coverage/topology was not completed/persisted; partialsource chunks have no qualification credit. Existing oldnative overlap negatives remain unwaived, no native/source/current/root/candidate acceptance. Actual finite union may be covered by a later genuine originalsource core with fullactor regressions.')))
if __name__=='__main__':main()
