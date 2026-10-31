"""Bind exact nested replacement and reuse the identical complete changed rectangle."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from disjoint_nested_append_contract_v1_20261029 import verify_append
from nested_coordinated_parent_contract_v1_20261027 import targets
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-academy69025-nested-binding-scope-v1-20261029'
PATCH='government-xl-academy69025-nested-parent-composition-v2-20261029';SCOPE='government-xl-academy69025-stored-return-current-evidence-v1-20261029-69025-0-scope'
def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={};receipts={}
    def take(n,p):
        if n not in pins:receipts[n],pins[n]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    patch=take(PATCH,BASE/PATCH/'summary.json');assert patch['status']=='private-terrain-validator-passed'
    new=take(PATCH,ROOT/patch['candidate']['path']);old=verify_append(new);row=patch['replacedNativeTerrain'][0];priorpath=ROOT/'3d-viewer'/row['url'];assert digest(priorpath.read_bytes())==row['sha256']and read(priorpath)==old;refs.append(priorpath)
    assert set(row['retainedUids'])==set(old['meta']['targetUids'])==targets(old)
    scope=take(SCOPE,BASE/SCOPE/'scope.json');assert scope['regionalParentExtent']==patch['nestedBounds']
    assert scope['terrainContacts']and {r['url']for r in scope['terrainContacts']}=={row['url']}
    source=new['patches'][-1];g=source['meta']['georef'];bounds=[g['bE']-834500,816500-g['bN'],g['bE']-834500+(source['w']-1)*g['aE'],816500-g['bN']-(source['h']-1)*g['aN']];assert bounds==scope['regionalParentExtent']
    positions=np.asarray(source['nativeMesh']['position']).reshape(-1,3)
    for values in [positions,positions.astype('<f4').astype('<f8')]:
        assert values[:,0].min()>=bounds[0]and values[:,0].max()<=bounds[2]and values[:,2].min()>=bounds[1]and values[:,2].max()<=bounds[3]
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pins[SCOPE][str(manifest.relative_to(ROOT))];refs.append(manifest)
    forms=take(SCOPE,BASE/SCOPE/'form-obligations.json.gz');natives=take(SCOPE,BASE/SCOPE/'native-obligations.json.gz');assert len(forms)==scope['intersectingForms']==4 and {r['uid']for r in natives}==set(scope['touchingNativeUids'])
    for f in forms:
        tile=ROOT/'3d-viewer/city/data/tiles'/(f['tile']+'.json');assert digest(tile.read_bytes())==pins[SCOPE][str(tile.relative_to(ROOT))]and next(b for b in read(tile)['buildings']if b['uid']==f['uid'])==f;refs.append(tile)
    retention=dict(allOldGridValuesAndChildBodiesExact=True,retainedChildren=len(old['patches']),closedChangedRegion=bounds,noExistingTerrainChildOverlapped=True,scopeReusedOnlyForIdenticalChangedRegion=True,oldSourceScope=dict(path=str((BASE/SCOPE/'scope.json').relative_to(ROOT)),sha256=digest((BASE/SCOPE/'scope.json').read_bytes())),sourceGeometryChanges=0)
    save(out/'retention.json',retention);save(out/'scope.json',{**scope,'exactRetainedParentComposition':retention});save(out/'form-obligations.json.gz',forms);save(out/'native-obligations.json.gz',natives)
    candidate={**patch['candidate'],'replaces':{k:row[k]for k in ['url','sha256','retainedUids']}}
    result=dict(uids=patch['uids'],sourceSHA256ByUid=patch['sourceSHA256ByUid'],status='private-terrain-validator-passed',candidate=candidate,retention=retention,replacedNativeTerrain=patch['replacedNativeTerrain'],installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Complete immutable prior scope re-bound only after proving the new child changes the identical closed140mrectangle and every old grid/child body survives exactly. One explicit pinned regional parent replacement. All four current forms, two touching installed originals and every retained parent target remain mandatory regression obligations. No model/physical/source/visual approval.')
    save(out/'summary.json',result);refs.extend([HERE/'disjoint_nested_append_contract_v1_20261029.py',HERE/'nested_coordinated_parent_contract_v1_20261027.py'])
    module('academy_nested_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-retained-parent-replacement-binding-and-complete-local-changed-scope',refs,result)
if __name__=='__main__':main()
