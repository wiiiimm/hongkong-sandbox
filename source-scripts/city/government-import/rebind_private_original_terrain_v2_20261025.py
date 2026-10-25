"""Replay unchanged terrain with its exact authenticated historical source selection. Companion originals grant no terrain target or acceptance expansion."""
import argparse,shutil
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','previous','capture','previous-capture']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert all(n.startswith('government-xl-')and'/'not in n for n in vars(a).values())
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert not out.exists()and not local.exists()
    old,op=authenticate(base/a.previous);_,cp=authenticate(base/a.capture)
    origin_name=getattr(a,'previous_capture');_,origin_pins=authenticate(base/origin_name)
    assert old['status']=='private-terrain-validator-passed'and old['sourceGeometryChanges']==0
    refs=[Path(__file__),base/a.previous/'result.json',base/a.capture/'result.json',base/origin_name/'result.json']
    def take(path,pins):
        assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(base/a.capture/'selection.json.gz',cp);current_sources={r['uid']:r['sourceSHA256']for r in selection['rows']}
    origin_path=base/origin_name/'selection.json.gz';assert op[str(origin_path.relative_to(ROOT))]==origin_pins[str(origin_path.relative_to(ROOT))]
    origin=take(origin_path,origin_pins);oldrows={r['uid']:r for r in origin['rows']}
    targets=set(old['uids']);assert targets and targets<=set(current_sources)and targets<=set(oldrows)
    sources={u:current_sources[u]for u in targets}
    assert sources=={u:oldrows[u]['sourceSHA256']for u in targets}
    if 'sourceSHA256ByUid'in old:assert sources==old['sourceSHA256ByUid']
    for row in selection['rows']:
        if row['uid']in targets:assert row['source']['building']==oldrows[row['uid']]['source']['building']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    for row in selection['rows']:
        path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==current_sources[row['uid']];refs.append(path)
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(f for f in read(tile)['buildings']if f['uid']==row['uid'])==row['source']['building'];refs.append(tile)
    parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(parentpath,op)
    oldpath=ROOT/old['candidate']['path'];patch=take(oldpath,op);assert digest(oldpath.read_bytes())==old['candidate']['sha256']
    assert patch['meta']['parentSha256']==digest(parentpath.read_bytes())
    replacements=old.get('replacedNativeTerrain',[]);retained=set();urls={r['url']for r in read(manifest)['terrainPatches']}
    for replacement in replacements:
        assert replacement['url']in urls
        path=ROOT/'3d-viewer'/replacement['url'];assert digest(path.read_bytes())==replacement['sha256'];refs.append(path)
        prior=read(path);assert prior['meta']['targetUids']==replacement['targetUids']and prior['coarseCells']==replacement['coarseCells']
        assert prior['meta']['parentTerrain']==patch['meta']['parentTerrain']and prior['meta']['parentSha256']==patch['meta']['parentSha256']
        x,z,xx,zz=prior['coarseCells'];a0,b0,c0,d0=patch['coarseCells'];assert a0<=x<xx<=c0 and b0<=z<zz<=d0
        retained.update(prior['meta']['targetUids'])
    assert set(patch['meta']['targetUids'])==set(sources)|retained
    validator=module('rebound_original_terrain_validator',HERE/'resolve_pass_indexed_parent_clipping_v2.py')
    validator.validate_patch(patch,parent)
    out.mkdir();local.mkdir();candidate=local/'candidate-terrain.json';shutil.copyfile(oldpath,candidate)
    assert digest(candidate.read_bytes())==old['candidate']['sha256'];refs.extend([candidate,HERE/'resolve_pass_indexed_parent_clipping_v2.py'])
    bounds=validator.extent(patch['coarseCells'],parent)
    save(out/'scope.json',dict(uids=sorted(sources),bounds=bounds,coarseCells=patch['coarseCells'],currentManifestSHA256=selection['manifestSHA256'],sourceSHA256ByUid=sources,installationApproved=False))
    result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,candidate=dict(path=str(candidate.relative_to(ROOT)),sha256=digest(candidate.read_bytes())),status='private-terrain-validator-passed',terrainTriangles=len(patch['nativeMesh']['index'])//3,replacedNativeTerrain=replacements,retainedNativeTerrainTargets=sorted(retained),currentManifestSHA256=selection['manifestSHA256'],historicalCandidateSHA256=old['candidate']['sha256'],candidateBytesUnchanged=True,additionalExplicitCompanionUids=sorted(set(current_sources)-targets),priorSourceSelection=origin_name,sourceGeometryChanges=0,sourcePoseChanges=0,identityAccepted=False,physicalAcceptance=False,installationApproved=False,qualification='Current parent, exact source bytes/forms and every explicit retained native replacement identity are rechecked; the existing terrain validator is replayed without changing any candidate bytes or limits. Historical current-scene, coverage, source-role, neighbour, support and browser acceptance are NOT transferred. All require fresh scope/replay or exact authenticated stream rebinding.')
    save(out/'summary.json',result)
    module('rebound_original_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unchanged-private-original-terrain-current-input-validation',refs,result)
if __name__=='__main__':main()
