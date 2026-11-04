"""Run existing finite Float32 coverage/overlap proofs on every private node."""
from pathlib import Path
import copy,traceback
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from float32_coverage import approve_roundoff
from native_patch_resolution import projected_context
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-five-node-roundoff-v1-20261029';PRIOR='government-xl-fuying181489-five-member-node-diagnostics-v1-20261029'
def main():
    out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()and not local.exists();_,pins=authenticate(BASE/PRIOR);refs=[Path(__file__),BASE/PRIOR/'result.json']
    def take(p):
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    proposal=take(BASE/PRIOR/'summary.json');assert proposal['allNodeBudgetsPassed']and proposal['allGridWaterColourCropsExact'];out.mkdir();local.mkdir(parents=True);rows=[]
    for member in proposal['members']:
        path=ROOT/member['candidate']['path'];node=copy.deepcopy(take(path));mesh=copy.deepcopy(node['nativeMesh']);record=dict(member=member['member'],coveragePassed=False,overlapPassed=False,status='private-numerical-surface-investigation')
        try:
            g=node['meta']['georef'];x=g['bE']-834500;z=816500-g['bN'];bounds=[x,z,x+(node['w']-1)*g['aE'],z-(node['h']-1)*g['aN']];_,polygons,_,_=projected_context(node,bounds)
            if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:save(out/(member['member']+'-coverage.json'),approve_roundoff(node,bounds))
            record['coveragePassed']=True
            overlap=module('fuying_numerical_overlap_'+member['member'].replace('-','_'),HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out/member['member'];overlap.DOC.mkdir();overlap.overlap_proof(node,[path,Path(__file__)]);record['overlapPassed']=True
            assert node['nativeMesh']['position']==mesh['position']and node['nativeMesh']['index']==mesh['index'];dest=local/(member['member']+'-unbound.json');save(dest,node);refs.append(dest);record.update(status='private-roundoff-qualified-pending-effective-boundary-and-full-scene-checks',candidate=dict(path=str(dest.relative_to(ROOT)),sha256=digest(dest.read_bytes())),coarseCells=node['coarseCells'],terrainTriangles=len(mesh['index'])//3)
        except Exception as error:
            record.update(errorType=type(error).__name__,reason=str(error));save(out/(member['member']+'-failure.json'),dict(record,traceback=traceback.format_exc()))
        rows.append(record);print(record,flush=True)
    result=dict(uids=proposal['uids'],sourceSHA256ByUid=proposal['sourceSHA256ByUid'],oldParent=proposal['oldParent'],completeTargetObligations=proposal['completeTargetObligations'],members=rows,allNumericalCoverageAndOverlapPassed=all(r['coveragePassed']and r['overlapPassed']for r in rows),sourceGeometryChanges=0,sourcePoseChanges=0,terrainCoordinatesChanged=False,terrainValidatorPassed=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Existing unchanged finite Float32 coverage/overlap proof kernels applied to each complete source-bound private node. Terrain positions/indices remain exact. This grants no effective five-member boundary contract, full parent replacement, current retained-source/foreign/rendered-ground or device/publication acceptance.')
    save(out/'summary.json',result);refs.extend([HERE/'float32_coverage.py',HERE/'native_patch_resolution.py',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py']);module('fuying_five_roundoff_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-private-nodes-existing-finite-coverage-overlap-proofs',refs,result)
if __name__=='__main__':main()
