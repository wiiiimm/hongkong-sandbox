"""Unchanged complete 72-face Hoi Shing source part and actual original TIN.

Nine real upward-clearance failures remain failures. Default source node/material
provides no basement/road/ramp semantics; no such function is inferred here.
Every complete original component face and every intersecting full TIN facet is
preserved in the diagnostic. Figures are contextual views, never acceptance.
"""
from pathlib import Path
import gzip,json,struct,importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-hoi-shing-72-face-upward-part-context-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-hoi-shing-complete-original-edge-contact-graph-v1';RECOVERY=BASE/'xl-terrain-recovery-20261011-hoi-shing-underlying-podium-original-recovery-v1';TIN=BASE/'xl-terrain-recovery-20261011-hoi-shing-two-original-authentic-tin-finite-v1';UP=BASE/'xl-terrain-recovery-20261011-hoi-shing-podium-authentic-tin-upward-refinement-v1';UID='landsd/318830:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists();refs=[ref(Path(__file__))]
    for folder in(GRAPH,RECOVERY,TIN,UP):
        r=read(folder/'result.json')
        with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
        refs.extend(ref(folder/n)for n in('result.json','diagnostic.json.gz')if(folder/n).is_file())
    row=next(r for r in read(RECOVERY/'selection.json.gz')['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];world=decode_original_world_triangles(raw);assert world.shape==(5533,3,3)
    graph=read(GRAPH/'diagnostic.json.gz');part=graph['components'][103];assert part['actorUID']==UID;ids=[int(i-13841)for i in part['globalOriginalFaces']];assert len(ids)==72;failed=[3261,3262,3263,3264,3265,3266,3267,3272,3273];assert set(failed)<=set(ids)
    groundpath=HERE/'local'/TIN.name/'complete-authentic-source-tin-ground.json.gz';g=read(groundpath);ground=np.asarray(g['completeSelectedFacets'],float).reshape(-1,3,3);assert len(ground)==11554 and digest(ground.tobytes())==g['completeSelectedFacetSHA256']
    selected=world[ids];low=selected.min((0,1));high=selected.max((0,1));padded=np.array([low-np.array([2,0,2]),high+np.array([2,0,2])]);lo=ground.min(1);hi=ground.max(1);hits=np.where(np.all(hi[:,[0,2]]>=padded[0,[0,2]],axis=1)&np.all(lo[:,[0,2]]<=padded[1,[0,2]],axis=1))[0].tolist();context=ground[hits]
    blob=gzip.decompress(raw);length=struct.unpack_from('<I',blob,12)[0];doc=json.loads(blob[20:20+length]);metadata=dict(defaultScene=doc.get('scene',0),scenes=doc['scenes'],completeNodes=doc['nodes'],completeMeshes=doc['meshes'],completeMaterials=doc.get('materials',[]),nodeMaterialMetadataSuppliesNoBelowGradeFunction=True)
    fig=plt.figure(figsize=(18,9),dpi=100);center=(low+high)/2
    for k,(include_ground,angle)in enumerate(((False,(25,-65)),(True,(32,-65)),(True,(24,120)))):
        ax=fig.add_subplot(1,3,k+1,projection='3d');shown=(selected-center)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(shown,facecolors='#839fab',edgecolors='#355262',alpha=.82,linewidths=.45));ax.add_collection3d(Poly3DCollection((world[failed]-center)[:,:,[0,2,1]],facecolors='#d3762e',edgecolors='#783b16',alpha=1,linewidths=.8))
        if include_ground:ax.add_collection3d(Poly3DCollection((context-center)[:,:,[0,2,1]],facecolors='#adbaa4',edgecolors='#4d6748',alpha=.28,linewidths=.3))
        viewlo=low-np.array([1,1,1]);viewhi=high+np.array([1,1,1]);s=(np.array([viewlo,viewhi])-center)[:,[0,2,1]];ax.set_xlim(s[0,0],s[1,0]);ax.set_ylim(s[0,1],s[1,1]);ax.set_zlim(s[0,2],s[1,2]);ax.set_box_aspect(s[1]-s[0]);ax.view_init(*angle);ax.set_title('All original 72 faces; nine failing upward faces in orange'+('\nAuthenticated full original terrain facets in green'if include_ground else'\nNo semantic function or acceptance inferred'),fontsize=9);ax.set_xlabel('Original X (m)');ax.set_ylabel('Original Z (m)');ax.set_zlabel('Original Y (m)')
    fig.tight_layout();DOC.mkdir(parents=True);png=DOC/'original-72-face-upward-part-with-authentic-tin-1800x900.png';fig.savefig(png);plt.close(fig)
    normals=np.cross(selected[:,1]-selected[:,0],selected[:,2]-selected[:,0]);refs.extend(ref(p)for p in(asset,png,groundpath,RECOVERY/'selection.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py'))
    out=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalFaces=5533,complete72FacePartIds=ids,complete72OriginalTriangles=selected.tolist(),complete72OriginalNormals=normals.tolist(),complete72OriginalAreasM2=(np.linalg.norm(normals,axis=1)/2).tolist(),completePartEdgeCensus=census(world,ids),completePartBounds=[low.tolist(),high.tolist()],completeNineRealFailingUpwardFaces=failed,rawNineExactPairedFailures=ref(UP/'diagnostic.json.gz'),completeActualOriginalPartContacts=[p for p in graph['oneExactPositiveWitnessPerContactingBodyPair']if 103 in p['components']],completeOriginalSourceHierarchyAndMaterialMetadata=metadata,wholeOriginalTINFacetsInVisualContext=hits,contextOnlyTINSelectionDoesNotReplaceComplete11554NumericScope=True,sourceOnly=True,originalTerrainAloneDoesNotResolveNineFailures=True,preciseHoldReason='Nine authored upward facets in complete72-face ancillary source part intersect authenticated originalTIN by about0.58–0.90m. No source metadata authorises below-grade upward roofs, and no exact terrain/provider defect is yet established.',noFreshCurrentReacceptance=True,noInventedFunction=True,terrainProposalCreated=False,sourceGeometryChanges=0,structuralRootCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
    s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-original-hoi-shing72-part-nine-real-upward-terrain-hold-context-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],preciseHoldReason=out['preciseHoldReason'],completePartFaces=72,realUpwardFailingFaces=failed,sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
