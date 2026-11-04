"""Refine only the over-budget quadrant; preserve the exact frozen surface."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from finite_terrain_two_way_partition_v1_20261028 import partition
from coordinated_native_boundary_v1_20261023 import seam_segments,seam_comparison_report
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-five-parent-members-diagnostic-v1-20261029';PRIOR='government-xl-fuying181489-edit-only-four-parent-members-v2-20261029'
def main():
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();_,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),BASE/PRIOR/'result.json']
    def take(p):
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    prior=take(BASE/PRIOR/'summary.json');assert prior['allFiniteSeamsPassed']and not prior['allMemberBudgetsPassed'];assert [m['member']for m in prior['members']if not m['runtimeBudgetPassed']]==['west-low-z']
    rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=take(rootpath);g=root['meta']['georef'];column=484;x=g['bE']+column*g['aE']-834500;nodes={};members=[];proof=None;allids=set();doc.mkdir();local.mkdir(parents=True)
    for member in prior['members']:
        data=take(ROOT/member['source']['path']);tri=np.asarray(data['triangles']);allids.update(data['parentFaceIndices'])
        if member['member']=='west-low-z':
            parts,proof=partition(tri,x)
            for side,part in parts.items():
                name='west-'+side+'-low-z';bounds=list(member['bounds']);cells=list(member['coarseCells'])
                if side=='west':bounds[2]=x;cells[2]=column
                else:bounds[0]=x;cells[0]=column
                values=part['triangles'];ids=[data['parentFaceIndices'][i]for i in part['parentFaceIndices']];path=local/(name+'.json.gz');save(path,dict(triangles=values.tolist(),parentFaceIndices=ids));refs.append(path);nodes[name]=values;members.append(dict(member=name,bounds=bounds,coarseCells=cells,faces=len(values),runtimeBudgetPassed=len(values)<=25000,source=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))))
        else:nodes[member['member']]=tri;members.append(member)
    seams=[]
    for i,a in enumerate(members):
        for b in members[i+1:]:
            rectA=shapely.box(*a['bounds']);rectB=shapely.box(*b['bounds']);assert rectA.intersection(rectB).area==0
            shared=rectA.boundary.intersection(rectB.boundary)
            if shared.geom_type=='Point'or shared.is_empty:continue
            assert shared.geom_type=='LineString';coords=np.asarray(shared.coords);axis=0 if np.all(coords[:,0]==coords[0,0])else 2;other=1 if axis==0 else 0;c=float(coords[0,0 if axis==0 else 1]);start,end=float(coords[:,other].min()),float(coords[:,other].max());curves=[seam_segments(nodes[m['member']],axis,c,start,end)for m in [a,b]];seams.append(dict(members=[a['member'],b['member']],axis=axis,coordinate=c,start=start,end=end,proof=seam_comparison_report(*curves,start,end)))
    represented={i for m in members for i in read(ROOT/m['source']['path'])['parentFaceIndices']};assert represented==allids==set(range(prior['aggregateUnpartitionedFaces']))
    union=shapely.union_all([shapely.box(*m['bounds'])for m in members]);old=take(ROOT/prior['oldParent']['path']);pg=old['meta']['georef'];extent=[pg['bE']-834500,816500-pg['bN'],pg['bE']-834500+(old['w']-1)*pg['aE'],816500-pg['bN']-(old['h']-1)*pg['aN']];assert union.equals(shapely.box(*extent))
    result=dict(uids=prior['uids'],sourceSHA256ByUid=prior['sourceSHA256ByUid'],oldParent=prior['oldParent'],completeTargetObligations=prior['completeTargetObligations'],oldParentFaces=prior['oldParentFaces'],aggregateUnpartitionedFaces=prior['aggregateUnpartitionedFaces'],aggregatePartitionedFaces=sum(m['faces']for m in members),members=members,newSubpartitionConservation=proof,seams=seams,allMemberBudgetsPassed=all(m['runtimeBudgetPassed']for m in members),allFiniteSeamsPassed=all(s['proof']['passed']for s in seams),completeOldExtentCoveredExactly=True,allParentFacesRepresented=True,sourceGeometryChanges=0,sourcePoseChanges=0,terrainValidatorPassed=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Five disjoint root-cell-aligned nodes cover exactly the full old-parent extent; all prior target obligations preserved. One over-budget quadrant is partitioned with full face/vertex/plane conservation; three other quadrant arrays remain unchanged. Every complete finite adjacency seam, aggregate cost and per-node budget reported. No outer boundary, colour/water/grid, effective replacement contract, retained-five-target regression, actual-renderer/device or installation acceptance follows this diagnostic.')
    save(doc/'summary.json',result);refs.extend([HERE/'finite_terrain_two_way_partition_v1_20261028.py',HERE/'coordinated_native_boundary_v1_20261023.py']);module('fuying_five_nodes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-five-root-aligned-parent-members-conservation-and-complete-adjacency-seams',refs,result);print(dict(budgets=result['allMemberBudgetsPassed'],seams=result['allFiniteSeamsPassed'],faces=[m['faces']for m in members],aggregate=result['aggregatePartitionedFaces']))
if __name__=='__main__':main()
