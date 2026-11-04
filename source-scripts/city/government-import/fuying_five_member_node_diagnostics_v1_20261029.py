"""Bind five private terrain nodes to exact old grids and report surface guards."""
from pathlib import Path
import copy
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from constant_colour_terrain_consolidation_v1 import colours
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-five-member-node-diagnostics-v1-20261029';PRIOR='government-xl-fuying181489-five-parent-members-diagnostic-v1-20261029'
def main():
    doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();_,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),BASE/PRIOR/'result.json']
    def take(p):
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    proposal=take(BASE/PRIOR/'summary.json');assert proposal['allMemberBudgetsPassed']and proposal['allFiniteSeamsPassed']and proposal['allParentFacesRepresented']and proposal['completeOldExtentCoveredExactly']
    parentpath=ROOT/proposal['oldParent']['path'];parent=take(parentpath);assert digest(parentpath.read_bytes())==proposal['oldParent']['sha256'];pg=parent['meta']['georef'];step=parent['cell'];assert step==pg['aE']==5;rows=[];doc.mkdir();local.mkdir(parents=True)
    for member in proposal['members']:
        tri=np.asarray(take(ROOT/member['source']['path'])['triangles'],dtype='<f4').astype('<f8');node=copy.deepcopy(parent);x0,z0,x1,z1=member['bounds'];c0=(x0+834500-pg['bE'])/step;r0=(z0-816500+pg['bN'])/step;c1=(x1+834500-pg['bE'])/step;r1=(z1-816500+pg['bN'])/step;assert all(v==int(v)for v in [c0,r0,c1,r1]);c0,r0,c1,r1=map(int,[c0,r0,c1,r1]);assert 0<=c0<c1<parent['w']and 0<=r0<r1<parent['h']
        for key,value in parent.items():
            if isinstance(value,list)and len(value)==parent['w']*parent['h']:node[key]=[value[r*parent['w']+c]for r in range(r0,r1+1)for c in range(c0,c1+1)]
        node['id']=BATCH+'-'+member['member'];node['w']=c1-c0+1;node['h']=r1-r0+1;node['coarseCells']=member['coarseCells'];node['meta']['georef'].update(bE=x0+834500,bN=816500-z0,W=node['w'],H=node['h']);node['meta']['targetUids']=proposal['completeTargetObligations'];node['nativeMesh']['position']=tri.reshape(-1).tolist();node['nativeMesh']['index']=list(range(tri.size//3));node['nativeMesh'].pop('sourceOverlap',None)
        for key in ['coordinatedBoundary','numericalCoverageGap','numericalProjectionOverlap']:node['nativeMesh']['source'].pop(key,None)
        node['nativeMesh']['source']['privateWholeParentReplacement']=dict(oldParent=proposal['oldParent'],member=member['member'],sourceSHA256ByUid=proposal['sourceSHA256ByUid'],qualification='Unapproved derived terrain; exact full-parent replacement required, no standalone or nested insertion.')
        vertex_colours_exact=np.array_equal(colours(tri,node),colours(tri,parent));assert vertex_colours_exact
        for key in ['elev','renderedElev','vegetation']:
            if key in parent:assert node[key]==[parent[key][r*parent['w']+c]for r in range(r0,r1+1)for c in range(c0,c1+1)]
        polygons=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;union=shapely.union_all(polygons[valid]);domain=shapely.box(*member['bounds']);gap=float(union.symmetric_difference(domain).area);excess=float(shapely.area(polygons[valid]).sum()-union.area);tolerance=max(.001,domain.area*1e-7)
        path=local/(member['member']+'-unbound.json');save(path,node);refs.append(path);rows.append(dict(member=member['member'],candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),coarseCells=member['coarseCells'],terrainTriangles=len(tri),gridExactCrop=True,originalWaterMaskExactCrop=True,vertexColourLookupExact=True,coverageGapM2=gap,projectedExcessM2=excess,ordinaryAreaToleranceM2=tolerance,ordinaryCoveragePassed=gap<tolerance,ordinaryProjectedOverlapPassed=excess<tolerance,runtimeBudgetPassed=len(tri)<=25000,sourceGeometryChanges=0))
        print({k:rows[-1][k]for k in ['member','terrainTriangles','coverageGapM2','projectedExcessM2']},flush=True)
    result=dict(uids=proposal['uids'],sourceSHA256ByUid=proposal['sourceSHA256ByUid'],oldParent=proposal['oldParent'],completeTargetObligations=proposal['completeTargetObligations'],members=rows,aggregateTerrainTriangles=sum(r['terrainTriangles']for r in rows),allOrdinaryCoveragePassed=all(r['ordinaryCoveragePassed']for r in rows),allOrdinaryProjectedOverlapPassed=all(r['ordinaryProjectedOverlapPassed']for r in rows),allNodeBudgetsPassed=all(r['runtimeBudgetPassed']for r in rows),allGridWaterColourCropsExact=True,sourceGeometryChanges=0,sourcePoseChanges=0,terrainValidatorPassed=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Five unbound nodes only: current native-parent grid/elevation/vegetation/water data are exact indexed crops and current colour lookup is preserved for every represented vertex. Ordinary coverage/overlap/budget numbers reported with unchanged thresholds. Full old-parent/effective-member/outer-boundary binding, numerical surface treatment, all retained-source regression and actual renderer/device checks still required. No public terrain writes or original building edits.')
    save(doc/'summary.json',result);refs.append(HERE/'constant_colour_terrain_consolidation_v1.py');module('fuying_node_diagnostics_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-five-terrain-node-exact-grid-water-colour-and-ordinary-surface-diagnostics',refs,result)
if __name__=='__main__':main()
