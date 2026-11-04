"""Compose a private whole-parent terrain proposal and measure bounded partitions.

Retains the current outer boundary and all retained target obligations. This is
not a validator adapter or installation approval; aggregate geometry is reported.
"""
from pathlib import Path
import uuid
from collections import Counter
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_assembly_context_plot_v3_20261023 import clipped_faces
from finite_terrain_two_way_partition_v1_20261028 import partition
from coordinated_native_boundary_v1_20261023 import seam_segments,seam_comparison_report

BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-edit-only-parent-partition-diagnostic-v2-20261029'
PRIOR='government-xl-fuying181489-actual-native-parent-inset-v2-20261029';PARENT='3d-viewer/city/data/government-native-fu-wong-original-v1-20261023.json'

def main():
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists()
    receipt,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),BASE/PRIOR/'result.json']
    def take(path):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    failed=take(BASE/PRIOR/'summary.json');child=take(BASE/PRIOR/'unapproved-terrain.json')
    assert failed['reason']=='Native terrain boundary does not join parent heights' and failed['privateNestedChildOnly']
    parentpath=ROOT/PARENT;parent=take(parentpath);targets=sorted(set(parent['meta']['targetUids'])|{'landsd/181489:0'})
    resources=['building:'+u for u in targets]+['terrain:city/data/terrain.json','terrain:'+PARENT.removeprefix('3d-viewer/')]
    claim=reservations.claim('fuying-whole-parent-diagnostic-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
    try:
        doc.mkdir();local.mkdir(parents=True)
        def faces(node):
            m=node['nativeMesh'];return np.asarray(m['position'],dtype='<f4').astype('<f8').reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)]
        def bounds(node):
            g=node['meta']['georef'];x=g['bE']-834500;z=816500-g['bN'];return [x,z,x+(node['w']-1)*g['aE'],z-(node['h']-1)*g['aN']]
        old,new=faces(parent),faces(child);x0,z0,x1,z1=bounds(child);extent=bounds(parent)
        assert extent[0]<x0<x1<extent[2]and extent[1]<z0<z1<extent[3]
        assert child['meta']['parentSha256']==digest(parentpath.read_bytes())
        from ronsdale_local_inset_v2_20261022 import plane,lift
        envelope=take(BASE/PRIOR/'core-envelope-proof.json')
        edit=shapely.from_wkt(envelope['envelopeWKT']).buffer(1,join_style='mitre').buffer(3,join_style='mitre')
        assert shapely.box(*extent).covers(edit) and edit.distance(shapely.box(*extent).boundary)>0
        pieces=[];old_ids=[];whole_ids=[];max_drift=0.;new_pieces=[];retained_zero=0;child_zero=0
        def derived(region,face):
            nonlocal max_drift
            if region.is_empty or region.area==0:return []
            coefficient=plane(face);parts=lift(region,coefficient)
            for part in parts:
                runtime=part.astype('<f4').astype('<f8');height=runtime[:,[0,2]]@coefficient[:2]+coefficient[2]
                max_drift=max(max_drift,float(abs(runtime[:,1]-height).max()))
            return parts
        for i,f in enumerate(old):
            polygon=shapely.MultiPoint(f[:,[0,2]]).convex_hull
            if polygon.area==0 or not polygon.intersects(edit):
                pieces.append(f);old_ids.append(i);whole_ids.append(i)
                retained_zero+=int(polygon.area==0);continue
            for part in derived(polygon.difference(edit),f):pieces.append(part);old_ids.append(i)
        old_zero={f.astype('<f8').tobytes()for f in old if shapely.MultiPoint(f[:,[0,2]]).convex_hull.area==0}
        for f in new:
            polygon=shapely.MultiPoint(f[:,[0,2]]).convex_hull
            if polygon.area==0:
                if polygon.intersects(edit)and f.astype('<f8').tobytes()not in old_zero:new_pieces.append(f);child_zero+=1
                continue
            new_pieces.extend(derived(polygon.intersection(edit),f))
        assert max_drift<.01, 'Derived clipping changes source terrain plane height beyond existing1cm guard'
        remainder=np.asarray(pieces,dtype='<f4').astype('<f8');combined=np.concatenate([remainder,np.asarray(new_pieces,dtype='<f4').astype('<f8')])
        save(doc/'edit-only-composition.json',dict(editWKT=edit.wkt,retainedWholeOldFaces=len(whole_ids),retainedOriginalZeroXZFaces=retained_zero,additionalChildZeroXZFaces=child_zero,maximumDerivedPlaneHeightDriftM=max_drift,newInsideEditFaces=len(new_pieces),sourceGeometryChanges=0))
        refs.append(doc/'edit-only-composition.json')
        # Every original outer-boundary triangle is retained byte-for-byte.
        boundary_ids=np.flatnonzero(np.any((old[:,:,0]==extent[0])|(old[:,:,0]==extent[2])|(old[:,:,2]==extent[1])|(old[:,:,2]==extent[3]),axis=1))
        assert set(boundary_ids)<=set(whole_ids)
        original_boundary=Counter(old[boundary_ids].reshape(len(boundary_ids),-1).tobytes()[i*72:(i+1)*72]for i in range(len(boundary_ids)))
        output_faces=Counter(f.astype('<f8').tobytes()for f in combined)
        assert all(output_faces[k]>=v for k,v in original_boundary.items())
        meshpath=local/'whole-parent-triangles.json.gz';save(meshpath,dict(triangles=combined.tolist(),retainedParentFaceIds=old_ids,privateChildFaces=len(new)));refs.append(meshpath)
        rootpath=ROOT/'3d-viewer/city/data/terrain.json';root=take(rootpath);g=root['meta']['georef'];cells=parent['coarseCells'];candidates=[]
        for column in range(cells[0]+1,cells[2]):
            x=g['bE']+column*g['aE']-834500
            try:
                divided,conservation=partition(combined,x)
                counts={name:len(data['triangles'])for name,data in divided.items()}
                seams={name:seam_segments(data['triangles'],0,x,extent[1],extent[3])for name,data in divided.items()}
                seam=seam_comparison_report(seams['west'],seams['east'],extent[1],extent[3])
                row=dict(column=column,splitX=x,memberFaces=counts,aggregateFaces=sum(counts.values()),allMemberBudgetsPassed=all(n<=25000 for n in counts.values()),completePartitionConservation=conservation,completeSeam=seam)
                for name,data in divided.items():
                    path=local/(str(column)+'-'+name+'.json.gz');save(path,dict(triangles=data['triangles'].tolist(),parentFaceIndices=data['parentFaceIndices']));refs.append(path)
                print(dict(column=column,faces=counts,seamPassed=seam['passed']),flush=True)
            except Exception as error:row=dict(column=column,splitX=x,passed=False,errorType=type(error).__name__,reason=str(error))
            candidates.append(row)
            assert reservations.owns(lease)
        result=dict(uids=['landsd/181489:0'],sourceSHA256ByUid=failed['sourceSHA256ByUid'],retainedTargetUids=parent['meta']['targetUids'],completeTargetObligations=targets,oldParent=dict(path=PARENT,sha256=digest(parentpath.read_bytes())),oldParentFaces=len(old),privateInsetFaces=len(new_pieces),retainedOutsideFaces=len(remainder),aggregateUnpartitionedFaces=len(combined),retainedWholeOuterBoundaryFaces=len(boundary_ids),partitionCandidates=candidates,privateWholeParentProposal=dict(path=str(meshpath.relative_to(ROOT)),sha256=digest(meshpath.read_bytes())),sourceGeometryChanges=0,sourcePoseChanges=0,terrainValidatorPassed=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Private whole-parent composition/partition diagnostic only. All original parent outer-boundary facets retained exactly; every prior target remains an explicit obligation. Aggregate face cost and every per-node budget/seam are reported, never hidden by partitioning. Only the actual convex source edit and3m return are replaced; irrelevant rectangle boundary fragments are not substituted. Clipped derived terrain must still pass global coverage/overlap, finite before/after conservation, color/water/parent-grid obligations, effective member binding, retained-five-source regression and actual desktop/mobile runtime tests before any acceptance. No original government building source edits or public writes.')
        save(doc/'summary.json',result);refs.extend([HERE/'original_assembly_context_plot_v3_20261023.py',HERE/'finite_terrain_two_way_partition_v1_20261028.py',HERE/'coordinated_native_boundary_v1_20261023.py'])
        module('fuying_parent_partition_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-whole-native-parent-replacement-partition-and-aggregate-cost-diagnostic',refs,result)
    finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
