"""Nominate complete current nearby actors for original model-only installation."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','runtime','attributes','inventory']:p.add_argument('--'+k,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selected=take(a.runtime,base/a.runtime/'selection.json.gz');attributes={r['uid']:r for r in take(a.attributes,base/a.attributes/'attributes.json.gz')['rows']};inventory=take(a.inventory,base/a.inventory/'complete-bounds.json.gz')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256']==pins[a.inventory][str(manifest.relative_to(ROOT))];refs.append(manifest)
    final=module('model_only_current_scope',HERE/'xl-final-script-pass.py');rows=[];formrefs={}
    for source in selected['rows']:
        uid=source['uid'];attr=attributes[uid];assert attr['sourceSHA256']==source['sourceSHA256']
        positions=[np.asarray(attr[k],float).reshape(-1,3)for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']]
        from exact_packed_world_geometry_20261009 import decode_original_world_triangles
        asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);positions.append(decode_original_world_triangles(asset.read_bytes()).reshape(-1,3))
        combined=np.concatenate(positions);assert np.isfinite(combined).all();lo,hi=combined.min(0),combined.max(0);touching=[]
        for native in inventory['rows']:
            values=np.asarray(native['completeFourWorldBounds'],float).reshape(-1,3);nlo,nhi=values.min(0),values.max(0)
            if native['uid']!=uid and np.all(hi+.5>=nlo)and np.all(nhi+.5>=lo):touching.append(dict(uid=native['uid'],sourceSHA256=native['sourceSHA256'],completeFourWorldBounds=native['completeFourWorldBounds']))
        region=[lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2];forms=[]
        for f,poly,tile in final.load_forms(region):
            path=ROOT/'3d-viewer'/tile;key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==inventory['currentFormTileHashes'][key];formrefs[key]=inventory['currentFormTileHashes'][key];refs.append(path)
            forms.append(dict(building=f,tile=tile,tileSHA256=inventory['currentFormTileHashes'][key]))
        save(out/(uid.split('/')[1]+'-forms.json.gz'),forms)
        rows.append(dict(uid=uid,sourceSHA256=source['sourceSHA256'],completeSourceFourWorldBounds=[lo.tolist(),hi.tolist()],currentFormsWithinTwoMetreRegion=len(forms),nearbyNativeActors=touching,currentNativeActorsChecked=len(inventory['rows']),sourceModelOnly=True,terrainEdits=False))
    assert digest(manifest.read_bytes())==selected['manifestSHA256']
    result=dict(uids=[r['uid']for r in rows],rows=rows,currentManifestSHA256=selected['manifestSHA256'],currentFormTileHashes=formrefs,sourceGeometryChanges=0,terrainEdits=False,installationApproved=False,publication=False,status='model-only-current-collision-scope',qualification='All four source coordinate representations bound every current native actor through conservative closed3Dboxes with.5m margin; exact current forms within2m horizontally are nominated. No source/foreign collision or dependency approval. Terrain unchanged; no terrain patch invented to use an unrelated installer.')
    save(out/'summary.json',result);refs.extend(HERE/n for n in ['xl-final-script-pass.py','exact_packed_world_geometry_20261009.py']);module('model_only_scope_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-current-original-model-only-collision-scope',list(dict.fromkeys(refs)),result);print([dict(uid=r['uid'],forms=r['currentFormsWithinTwoMetreRegion'],nativeCandidates=len(r['nearbyNativeActors']))for r in rows],flush=True)

if __name__=='__main__':main()
