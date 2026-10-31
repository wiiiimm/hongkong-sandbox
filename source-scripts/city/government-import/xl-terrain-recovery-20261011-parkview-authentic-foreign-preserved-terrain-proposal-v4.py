"""Explicit terrain-only causal repair of eighteen disjoint ordinary forms.

Reuses the verified authentic v3 proposal; retains actual old rendered terrain
under full outward dyadic rectangles covering each existing original/F32 form
footprint. All owned complete POSITION/literal/two explicit matrix-F32 bounds
are strictly disjoint. Full source/runtime/native/foreign checks remain mandatory.
"""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-parkview-authentic-foreign-preserved-terrain-proposal-v4';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'xl-terrain-recovery-20261011-parkview-authentic-current-retained-terrain-proposal-v3'
PHYSICAL=BASE/'government-xl-terrain-recovery-parkview-block11-authentic-retained-current-physical-v1-20261011'
ACTUAL=BASE/'xl-terrain-recovery-20261011-parkview-owned-actual-render-capture-v1'
PARENT='city/data/government-native-255439-0.json';UID='landsd/255647:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def receipt(folder):
 r=read(folder/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 return r

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);receipts=[receipt(f)for f in [PRIOR,PHYSICAL,ACTUAL]]
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);current=read(manifest);catrefs=[ref(ROOT/'3d-viewer'/u)for u in current['officialModelCatalogues']]
 selected=read(PHYSICAL/'selection.json.gz');assert selected['manifestSHA256']==start['sha256'];row=selected['rows'][0];assert row['uid']==UID
 native=read(PHYSICAL/'native-neighbour-checks.json');assert len(native['rows'])==4 and all(r['passed']for r in native['rows'])
 actor=read(ACTUAL/'actual-render-geometry.json.gz')['row'];assert actor['uid']==UID and actor['sourceSHA256']==row['sourceSHA256']
 boxes=[packed_world_bounds((ROOT/row['candidate']['path']).read_bytes())['originalWholeSourceBounds']]+[actor[k]for k in ['completeLiteralWorldBounds','completeExplicitLeftAssociatedFloat32ModelMatrixWorldBounds','completeExplicitBalancedFloat32ModelMatrixWorldBounds']]
 lo=np.min(np.asarray(boxes)[:,0],axis=0);hi=np.max(np.asarray(boxes)[:,1],axis=0);owned_region=box(lo[0],lo[2],hi[0],hi[2])
 forms={r['building']['uid']:r['building']for r in read(PHYSICAL/'neighbour-inputs.json.gz')['rows']};checks=read(PHYSICAL/'neighbour-checks.json')['rows'];foreign=[];regions=[]
 for r in checks:
  if not r['reasons']or r['existingNative']:continue
  assert r['uid']!=UID and r['reasons']==['increased-neighbour-ground-gap'];form=forms[r['uid']]
  vertices=np.asarray([p for ring in form['rings']for p in ring],float);assert vertices.ndim==2 and vertices.shape[1]==2 and np.isfinite(vertices).all()
  original_and_cast=np.concatenate([vertices,vertices.astype(np.float32).astype(float)]);low=np.floor(original_and_cast.min(axis=0)*1024)/1024;high=np.ceil(original_and_cast.max(axis=0)*1024)/1024
  assert np.all(original_and_cast>=low)and np.all(original_and_cast<=high);region=box(low[0],low[1],high[0],high[1]);assert owned_region.disjoint(region),'Complete owned source/literal/actual-F32 region overlaps foreign terrain retention'
  foreign.append(dict(uid=r['uid'],fullCurrentForm=form,completeOriginalAndFloat32FootprintBounds=[original_and_cast.min(axis=0).tolist(),original_and_cast.max(axis=0).tolist()],outwardDyadicRectangleBounds=[*low,*high],dyadicStepM=1/1024,exactCompleteOwnedBoundsDisjoint=True,minimumSeparationM=owned_region.distance(region),rawBeforeAfterFinding=r));regions.append(region)
 assert len(foreign)==18
 prior=read(PRIOR/'terrain-candidates.json')[0];patch=read(ROOT/prior['path']);assert ref(ROOT/prior['path'])['sha256']==prior['sha256'];bounds=prior['bounds'];patches=module('parkview_foreign_retention','native_patch_resolution.py');second=module('parkview_foreign_resolution','xl-second-pass.py')
 parentpath=ROOT/'3d-viewer'/PARENT;oldpatch=read(parentpath);rootparent=ROOT/'3d-viewer/city/data/terrain.json';parent=read(rootparent)
 assert oldpatch['meta']['targetUids']==['landsd/255439:0',UID]and patch['meta']['targetUids']==oldpatch['meta']['targetUids']
 assert prior['replaces']['url']==PARENT and prior['replaces']['sha256']==ref(parentpath)['sha256']
 from rendered_patch_sampler import RenderedPatchSampler
 sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True);old_sampler=RenderedPatchSampler(oldpatch,sampler,second.resolution.terrain.fine.DemSampler(oldpatch,rendered=True))
 protected=shapely.union_all(regions);assert owned_region.disjoint(protected)
 retention=patches.preserve_parent_under_projection(patch,bounds,protected,old_sampler,edge_sampler=sampler)
 fill=patches.fill_parent_only_holes(patch,parent,bounds,owned_region,sampler);snap=patches.snap_boundary_to_parent(patch,bounds,sampler)
 path=LOCAL/(patch['id']+'.json');save(path,patch);sourcefiles=read(PRIOR/'terrain.json')['sourceFiles']
 for r in sourcefiles:assert ref(ROOT/r['path'])==r
 if patches.projected_context(patch,bounds)[3]>1e-8:
  patches.approve_original_overlap(patch,path,DOC/'native-overlap.json',sourcefiles);patches.finalize_overlap_evidence(patch,DOC/'native-overlap.json')
 second.resolution.validate_patch(patch,parent);save(path,patch);candidate={**prior,'path':str(path.relative_to(ROOT)),'sha256':ref(path)['sha256'],'triangles':len(patch['nativeMesh']['index'])//3}
 save(DOC/'terrain-candidates.json',[candidate]);save(DOC/'terrain.json',dict(patch=candidate,priorImmutableProposal=ref(PRIOR/'terrain-candidates.json'),sourceFiles=sourcefiles,retainedInstalledNativeUIDs=['landsd/255439:0'],preservedOrdinaryForms=foreign,completeOwnedOriginalLiteralActualF32Bounds=[lo.tolist(),hi.tolist()],additionalParentPreservation=retention,parentHoleFill=fill,finalBoundarySnap=snap,sourceBuildingGeometryChanges=0,terrainProposalGeometryChanged=True,allCurrentSourceRuntimeForeignNativeChecksRequired=True,nativeReacceptance=False,publication=False))
 assert reservations.heartbeat(lease)['ok']and ref(manifest)==start
 refs=[ref(p)for p in [Path(__file__),manifest,rootparent,parentpath,ROOT/prior['path'],ROOT/row['candidate']['path'],PHYSICAL/'selection.json.gz',PHYSICAL/'neighbour-checks.json',PHYSICAL/'neighbour-inputs.json.gz',PHYSICAL/'native-neighbour-checks.json',ACTUAL/'actual-render-geometry.json.gz',DOC/'terrain-candidates.json',DOC/'terrain.json',path,HERE/'native_patch_resolution.py',HERE/'xl-second-pass.py',HERE/'rendered_patch_sampler.py',HERE/'exact_packed_world_bounds_v3_20261010.py']]+catrefs+sourcefiles
 for f,r in zip([PRIOR,PHYSICAL,ACTUAL],receipts):refs.extend([ref(f/'result.json'),*r['evidenceRefs']])
 refs=list({r['path']:r for r in refs}.values())
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=[UID,'landsd/254491:0','landsd/255439:0'],currentManifest=start,terrainCandidate=candidate,full18OrdinaryRetentionProof=foreign,sourceGeometryChanges=0,terrainProposalGeometryChanged=True,fullCurrentPhysicalRequired=True,nativeReacceptance=False,fullAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',result)
 module('parkview_foreign_proposal_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'explicit-current-parent-eighteen-whole-disjoint-ordinary-footprints-dyadic-terrain-preservation-v4',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=result['uids'],ordinaryForeignFormsPreserved=18,terrainProposalGeometryChanged=True,sourceGeometryChanges=0,fullCurrentPhysicalRequired=True,nativeReacceptance=False,newlyInstalled=0));print(dict(terrainCandidateValidated=True,triangles=candidate['triangles'],ordinaryForeignFormsPreserved=18,fullCurrentPhysicalRequired=True),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();uids={r['building']['uid']for r in read(PHYSICAL/'neighbour-inputs.json.gz')['rows']};claim=reservations.claim('parkview-foreign-preserved-terrain-'+str(uuid.uuid4()),['building:'+u for u in sorted(uids)]+['terrain-surface:'+PARENT],batch=BATCH,ttl=3600);assert claim['ok'];save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
