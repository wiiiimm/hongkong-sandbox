"""Measure four coherent root-aligned domains of the same private terrain surface."""
from pathlib import Path
import argparse
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from finite_terrain_two_way_partition_v1_20261028 import partition
from coordinated_native_boundary_v1_20261023 import seam_segments,seam_comparison_report
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-four-parent-members-diagnostic-v1-20261029';PRIOR='government-xl-fuying181489-whole-parent-partition-diagnostic-v1-20261029'
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['batch','prior']:parser.add_argument('--'+name,required=True)
    parser.add_argument('--row',type=int,required=True);parser.add_argument('--column',type=int,required=True);args=parser.parse_args()
    global BATCH,PRIOR
    BATCH,PRIOR=args.batch,args.prior
    assert BATCH.startswith('government-xl-fuying181489-')and '/'not in BATCH
    assert PRIOR.startswith('government-xl-fuying181489-')and '/'not in PRIOR
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();_,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),BASE/PRIOR/'result.json']
    def take(p):
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    before=take(BASE/PRIOR/'summary.json');master=np.asarray(take(ROOT/before['privateWholeParentProposal']['path'])['triangles'],dtype='<f8');parent=take(ROOT/before['oldParent']['path']);root=take(ROOT/'3d-viewer/city/data/terrain.json');g=root['meta']['georef'];column,row=args.column,args.row;x=g['bE']+column*g['aE']-834500;z=816500-g['bN']-row*g['aN'];cells=parent['coarseCells'];assert cells[0]<column<cells[2]and cells[1]<row<cells[3]
    pg=parent['meta']['georef'];extent=[pg['bE']-834500,816500-pg['bN'],pg['bE']-834500+(parent['w']-1)*pg['aE'],816500-pg['bN']-(parent['h']-1)*pg['aN']]
    doc.mkdir();local.mkdir(parents=True);halves,xproof=partition(master,x);nodes={};members=[];proofs=dict(firstAxis=xproof)
    for side,data in halves.items():
        parts,zproof=partition(data['triangles'][:,:,[2,1,0]],z);proofs[side]=zproof
        for half,part in parts.items():
            name=side+('-low-z'if half=='west'else'-high-z');tri=part['triangles'][:,:,[2,1,0]];parentids=[data['parentFaceIndices'][i]for i in part['parentFaceIndices']];bounds=[extent[0]if side=='west'else x,extent[1]if half=='west'else z,x if side=='west'else extent[2],z if half=='west'else extent[3]];coarse=[cells[0]if side=='west'else column,cells[1]if half=='west'else row,column if side=='west'else cells[2],row if half=='west'else cells[3]]
            path=local/(name+'.json.gz');save(path,dict(triangles=tri.tolist(),parentFaceIndices=parentids));refs.append(path);nodes[name]=tri;members.append(dict(member=name,bounds=bounds,coarseCells=coarse,faces=len(tri),runtimeBudgetPassed=len(tri)<=25000,source=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))))
    seams=[]
    for a,b,axis,c,start,end in [('west-low-z','east-low-z',0,x,extent[1],z),('west-high-z','east-high-z',0,x,z,extent[3]),('west-low-z','west-high-z',2,z,extent[0],x),('east-low-z','east-high-z',2,z,x,extent[2])]:
        curves=[seam_segments(nodes[n],axis,c,start,end)for n in [a,b]];seams.append(dict(members=[a,b],axis=axis,coordinate=c,start=start,end=end,proof=seam_comparison_report(*curves,start,end)))
    represented={i for m in members for i in read(ROOT/m['source']['path'])['parentFaceIndices']};assert represented==set(range(len(master)))
    result=dict(uids=before['uids'],sourceSHA256ByUid=before['sourceSHA256ByUid'],oldParent=before['oldParent'],completeTargetObligations=before['completeTargetObligations'],oldParentFaces=before['oldParentFaces'],aggregateUnpartitionedFaces=len(master),aggregatePartitionedFaces=sum(m['faces']for m in members),members=members,partitionConservation=proofs,seams=seams,allMemberBudgetsPassed=all(m['runtimeBudgetPassed']for m in members),allFiniteSeamsPassed=all(s['proof']['passed']for s in seams),sourceGeometryChanges=0,terrainValidatorPassed=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Four root-aligned rectangular nodes conserve the frozen whole-parent private surface. No parent face or original vertex omitted by either complete partition. Every finite shared edge and aggregate cost reported. This is not budget, effective-boundary, surface/colour/water, neighbour, source-role, device-performance or installation approval. The full old-parent replacement and all six target obligations remain mandatory; no nested native override or overlapping root patch.')
    save(doc/'summary.json',result);refs.extend([HERE/'finite_terrain_two_way_partition_v1_20261028.py',HERE/'coordinated_native_boundary_v1_20261023.py']);module('fuying_four_nodes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-four-root-aligned-parent-members-full-conservation-and-finite-seams',refs,result);print(dict(allMemberBudgetsPassed=result['allMemberBudgetsPassed'],allFiniteSeamsPassed=result['allFiniteSeamsPassed'],faces=[m['faces']for m in members],aggregate=result['aggregatePartitionedFaces']))
if __name__=='__main__':main()
