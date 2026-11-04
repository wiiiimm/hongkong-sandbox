"""Test the orthogonal partition of the frozen whole native-parent proposal."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from finite_terrain_two_way_partition_v1_20261028 import partition
from coordinated_native_boundary_v1_20261023 import seam_segments,seam_comparison_report
BATCH='government-xl-fuying181489-horizontal-whole-parent-partition-v1-20261029'
PRIOR='government-xl-fuying181489-whole-parent-partition-diagnostic-v1-20261029';BASE=ROOT/'docs/astra-city/government-import'
def main():
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();_,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),BASE/PRIOR/'result.json']
    def take(p):
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    previous=take(BASE/PRIOR/'summary.json');p=ROOT/previous['privateWholeParentProposal']['path'];master=np.asarray(take(p)['triangles'],dtype='<f8');parent=take(ROOT/previous['oldParent']['path']);root=take(ROOT/'3d-viewer/city/data/terrain.json')
    g=parent['meta']['georef'];extent=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(parent['w']-1)*g['aE'],816500-g['bN']-(parent['h']-1)*g['aN']]
    doc.mkdir();local.mkdir(parents=True);rows=[]
    for line in range(parent['coarseCells'][1]+1,parent['coarseCells'][3]):
        z=816500-root['meta']['georef']['bN']-line*root['meta']['georef']['aN']
        try:
            # Coordinate permutation is undone immediately; no rendered axis,
            # original vertex, winding or source model is changed.
            parts,proof=partition(master[:,:,[2,1,0]],z);members={name:d['triangles'][:,:,[2,1,0]]for name,d in parts.items()}
            curves={n:seam_segments(t,2,z,extent[0],extent[2])for n,t in members.items()};seam=seam_comparison_report(curves['west'],curves['east'],extent[0],extent[2]);counts={n:len(t)for n,t in members.items()}
            row=dict(rootRow=line,splitZ=z,memberFaces=counts,aggregateFaces=sum(counts.values()),allMemberBudgetsPassed=all(n<=25000 for n in counts.values()),completeSeam=seam,completePartitionConservation=proof)
            for name,t in members.items():
                path=local/(str(line)+'-'+name+'.json.gz');save(path,dict(triangles=t.tolist(),parentFaceIndices=parts[name]['parentFaceIndices']));refs.append(path)
            print(dict(row=line,faces=counts,seam=seam['passed']),flush=True)
        except Exception as e:row=dict(rootRow=line,splitZ=z,passed=False,errorType=type(e).__name__,reason=str(e))
        rows.append(row)
    result=dict(uids=previous['uids'],sourceSHA256ByUid=previous['sourceSHA256ByUid'],oldParent=previous['oldParent'],completeTargetObligations=previous['completeTargetObligations'],aggregateUnpartitionedFaces=len(master),rows=rows,sourceGeometryChanges=0,terrainValidatorPassed=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Alternative horizontal partition of the same frozen whole-parent proposal only. Every parent-face/vertex conservation, aggregate cost, per-member count and complete finite seam result retained. No geometry/colour/water/current-neighbour/renderer/quality acceptance or validator adapter.')
    save(doc/'summary.json',result);refs.extend([HERE/'finite_terrain_two_way_partition_v1_20261028.py',HERE/'coordinated_native_boundary_v1_20261023.py']);module('fuying_horizontal_partition_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-orthogonal-whole-parent-partition-and-complete-finite-seam-diagnostic',refs,result)
if __name__=='__main__':main()
