"""Prove actual complete BASIC meshes cannot intersect the reviewed original wall."""
from pathlib import Path
import subprocess
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BATCH = 'government-xl-nam-cheong-wall-actual-basic-scope-v1-20261023'
VERTICAL = 'government-xl-nam-cheong-complete-vertical-ground-and-wall-scope-v1-20261023'
SCOPE = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-scope'
ATTR = 'government-xl-nam-cheong-fu-yun-joint-attributes-v1-20261023'
CAPTURE = 'government-xl-nam-cheong-fu-yun-after-island-current-v1-20261023-runtime'


def main():
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / BATCH
    assert not doc.exists()
    refs, pins = [Path(__file__)], {}
    for name in [VERTICAL,SCOPE,ATTR,CAPTURE]:
        _,pins[name] = authenticate(base/name)
        refs.append(base/name/'result.json')
    def take(name,path):
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    vertical=take(VERTICAL,base/VERTICAL/'summary.json')
    assert not vertical['additionalUnclassifiedFaces']
    scope=take(VERTICAL,base/VERTICAL/'literal-wall-foreign-scope.json.gz')
    wanted={r['uid'] for r in scope['basicFootprintSeparations']}
    forms={r['uid']:r for r in take(SCOPE,base/SCOPE/'form-obligations.json.gz')}
    assert len(wanted)==36 and wanted<=set(forms)
    assert all(not forms[u].get('modelGeometry') for u in wanted)
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    manifestsha=digest(manifest.read_bytes())
    assert manifestsha==vertical['currentManifestSHA256']
    refs.append(manifest)
    selection=take(CAPTURE,base/CAPTURE/'selection.json.gz')
    attrs=take(ATTR,base/ATTR/'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    byuid={r['uid']:r for r in attrs['rows']}
    selected={r['uid']:r for r in selection['rows']}
    nam=byuid['landsd/268867:0'];ix=np.asarray(nam['completeOriginalIndex']).reshape(-1,3)
    raw=(ROOT/selected['landsd/268867:0']['candidate']['path']).read_bytes()
    assert digest(raw)==nam['sourceSHA256']
    walls=dict(original=decode_original_world_triangles(raw)[11390],**{mode:np.asarray(nam[key]).reshape(-1,3)[ix][11390] for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]})
    inputpath=doc/'input.json.gz';outpath=doc/'attributes.json.gz'
    save(inputpath,dict(currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=manifestsha),evidenceRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in refs],rows=[forms[u] for u in sorted(wanted)]))
    tool=HERE/'current_basic_attributes_v1_20261023.mjs'
    with (doc/'worker.log').open('w') as log:
        subprocess.run(['node',str(tool),str(inputpath.relative_to(ROOT)),str(outpath.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    captured=read(outpath)
    assert captured['startEndAllInputsVerified'] and {r['uid'] for r in captured['rows']}==wanted
    for path,sha in captured['inputHashes'].items():
        assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    results=[]
    for mode,wall in walls.items():
        comparisons=[]
        for row in captured['rows']:
            assert row['building']==forms[row['uid']]
            for index,mesh in enumerate(row['meshes']):
                assert mesh['identityArithmeticAllThreeExactlyEqual']
                p=np.asarray(mesh['position']).reshape(-1,3);lo,hi=p.min(0),p.max(0)
                assert np.any(lo>wall.max(0)) or np.any(hi<wall.min(0)),(mode,row['uid'],index)
                comparisons.append(dict(uid=row['uid'],mesh=index,wholePositionVerticesIncludingUnused=len(p),completeFaces=len(mesh['index'])//3,wholeBounds=[lo.tolist(),hi.tolist()]))
        fu=byuid['landsd/270874:0']
        if mode=='original':
            asset=ROOT/selected[fu['uid']]['candidate']['path'];assert digest(asset.read_bytes())==fu['sourceSHA256'];refs.append(asset)
            tri=decode_original_world_triangles(asset.read_bytes())
        else:
            key={'literal':'completeLiteralWorldPosition','left':'completeExplicitLeftAssociatedFloat32WorldPosition','balanced':'completeExplicitBalancedFloat32WorldPosition'}[mode]
            tri=np.asarray(fu[key]).reshape(-1,3)[np.asarray(fu['completeOriginalIndex']).reshape(-1,3)]
        assert np.any(tri.min((0,1))>wall.max(0)) or np.any(tri.max((0,1))<wall.min(0))
        save(doc/(mode+'.json.gz'),dict(mode=mode,wall=wall.tolist(),basicMeshBounds=comparisons,proposedCompanionUID=fu['uid'],proposedCompanionSourceSHA256=fu['sourceSHA256'],proposedCompanionCompleteFaces=len(tri),proposedCompanionWorldBounds=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()]))
        results.append(dict(mode=mode,completeCurrentBasicActors=len(wanted),completeBasicMeshes=len(comparisons),proposedCompanionStrictlySeparated=True,allActualMeshBoundsStrictlySeparated=True))
    assert digest(manifest.read_bytes())==manifestsha
    summary=dict(uids=['landsd/268867:0'],sourceFace=11390,currentManifestSHA256=manifestsha,rows=results,
                 sourceRoleAccepted=False,installationApproved=False,
                 qualification='All36remaining actual productionBASIC actors and every mesh/unusedPOSITION vertex bound are strictly disjoint from wall11390 in all four source representations. The proposed unchanged FuYun original is independently disjoint too. Combined with complete6860native bounds and fullregional scope, this closes wallforeignseparation only; no fullsourcecontact, exteriorrole, support, physical, publication or installation credit.')
    save(doc/'summary.json',summary)
    refs.extend([tool,HERE/'exact_packed_world_geometry_20261009.py'])
    module('nam_actual_basic_wall_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-actual-current-basic-and-companion-wall-separation',refs,summary)


if __name__=='__main__':
    main()
