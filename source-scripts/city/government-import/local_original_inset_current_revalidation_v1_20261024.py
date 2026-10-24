"""Revalidate an unchanged local inset against freshly captured actual parent terrain.

Target metadata remains exactly unchanged. No current source/neighbour, role or
publication acceptance transfers from the historical private experiment.
"""
import argparse,copy,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','patch','runtime']:p.add_argument('--'+k,required=True)
    a=p.parse_args();base=ROOT/'docs/astra-city/government-import';out=base/a.batch;local=HERE/'local'/a.batch
    assert a.batch.startswith('government-xl-')and'/'not in a.batch and not out.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    receipt,_=authenticate(base/a.patch);assert receipt['status']=='private-terrain-validator-passed'and not receipt['candidate'].get('replaces')
    oldpath=ROOT/receipt['candidate']['path'];old=take(a.patch,oldpath);scope=take(a.patch,base/a.patch/'scope.json');assert set(old['meta']['targetUids'])==set(receipt['uids'])==set(scope['uids'])
    selected=take(a.runtime,base/a.runtime/'selection.json.gz');sources={r['uid']:r for r in selected['rows']};assert set(receipt['uids'])<=sources.keys()
    root=ROOT/'3d-viewer/city/data/terrain.json';assert digest(root.read_bytes())==pins[a.patch][str(root.relative_to(ROOT))];refs.append(root)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
    for uid in receipt['uids']:
        r=sources[uid];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
    sourceScope=take(a.patch,base/a.patch/'original-face-scope.json');assert sources[sourceScope['uid']]['sourceSHA256']==sourceScope['sourceSHA256']
    oldparent=take(a.patch,HERE/'local'/a.patch/'parent.json');assert oldparent['domain']==scope['bounds']
    tool=HERE/'selected_original_parent_capture_v2.mjs';assert digest(tool.read_bytes())==pins[a.patch][str(tool.relative_to(ROOT))];refs.append(tool)
    save(out/'scope.json',scope);local.mkdir(parents=True)
    with(out/'parent-capture.log').open('w')as log:subprocess.run(['node',str(tool),str((out/'scope.json').relative_to(ROOT)),str((local/'parent.json').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    current=read(local/'parent.json');assert current['domain']==oldparent['domain'];before,after=np.asarray(oldparent['triangles']),np.asarray(current['triangles']);assert before.shape==after.shape and np.array_equal(before,after),'Actual rendered parent changed: construct and validate a fresh inset instead'
    refs.append(local/'parent.json')
    for key,sha in current['inputHashes'].items():assert digest((ROOT/key).read_bytes())==sha;refs.append(ROOT/key)
    patch=copy.deepcopy(old);patch['nativeMesh'].pop('sourceOverlap',None)
    proof=module('local_inset_current_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');proof.DOC=out;proof.overlap_proof(patch,[oldpath,local/'parent.json',Path(__file__)])
    builder=module('local_inset_current_validator',HERE/'resolve_pass_indexed_parent_clipping_v2.py');builder.validate_patch(patch,read(root))
    assert patch['nativeMesh']['position']==old['nativeMesh']['position']and patch['nativeMesh']['index']==old['nativeMesh']['index']and patch['coarseCells']==old['coarseCells']and patch['meta']['targetUids']==old['meta']['targetUids']
    assert digest(manifest.read_bytes())==selected['manifestSHA256'];path=local/'candidate-terrain.json';save(path,patch)
    result=dict(uids=receipt['uids'],status='private-terrain-validator-passed',candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())),sourceSHA256ByUid={u:sources[u]['sourceSHA256']for u in receipt['uids']},currentManifestSHA256=selected['manifestSHA256'],actualCurrentParentIdentical=True,parentGeometrySHA256=digest(after.tobytes()),sourceTerrainGeometryUnchanged=True,targetSetUnchanged=True,terrainTriangles=len(patch['nativeMesh']['index'])//3,historicalApprovalTransferred=False,sourceGeometryChanges=0,installationApproved=False,qualification='Historical exact private mesh/target set revalidated against unchanged root bytes and an actually freshly captured identical complete rendered parent. Ordinary overlap and final native validation rerun without limits changed. Source, current native/basic neighbours, seams, role, identity and browser/publication acceptance remain separate.')
    save(out/'summary.json',result);refs.extend([path,HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE/'resolve_pass_indexed_parent_clipping_v2.py']);module('local_inset_revalidation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unchanged-local-original-inset-current-parent-revalidation',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
