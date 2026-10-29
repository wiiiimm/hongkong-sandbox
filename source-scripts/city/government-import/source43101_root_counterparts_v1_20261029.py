"""Map both unchanged provider roots onto exact current forms; no acceptance."""
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source43101_provider_roots_v1_20261029 import glb

BATCH='government-xl-source43101-root-counterparts-v1-20261029'
SELECT='government-xl-source43101-current-selection-v1-20261029'
IDENTITY='government-xl-source43101-current-identity-v1-20261029'
PROVIDER='government-xl-after-sha-tin-43101-provider-roots-v1-20261029'

def main():
    base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;assert not doc.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(SELECT,base/SELECT/'selection.json.gz');row=selection['rows'][0];assert row['uid']=='landsd/43101:0'
    identity=take(IDENTITY,base/IDENTITY/'43101:0/identity.json');assert identity['sourceSHA256']==row['sourceSHA256']and not identity['passed']
    provider=take(PROVIDER,base/PROVIDER/'summary.json');assert provider['sourceSHA256']==row['sourceSHA256']and provider['allProviderAndPackedWorldArraysEqual']
    source=HERE/'local/government-xl-held-component-recovery-20261008/government-source/8-SW-11C/decoded'/provider['originalSourceEntry'];assert digest(source.read_bytes())==provider['originalGLTFSHA256'];gltf=read(source);binarypath=source.parent/gltf['buffers'][0]['uri'];binary=binarypath.read_bytes();assert digest(binary)==provider['originalBinarySHA256'];refs.extend([source,binarypath])
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];whole=decode_original_world_triangles(asset.read_bytes());refs.append(asset)
    bounds=[float(whole[:,:,0].min()-20),float(whole[:,:,2].min()-20),float(whole[:,:,0].max()+20),float(whole[:,:,2].max()+20)]
    loader=module('root_counterpart_forms',HERE/'xl-final-script-pass.py');forms=loader.load_forms(bounds);current=[]
    for form,_,tile in forms:
        path=ROOT/'3d-viewer'/tile;refs.append(path);current.append(form)
    assert next(f for f in current if f['uid']==row['uid'])==row['source']['building'];roots=[];arrays=[]
    for root in gltf['scenes'][gltf.get('scene',0)]['nodes']:
        triangles=decode_original_world_triangles(glb(gltf,binary,root));arrays.append(triangles);projection=shapely.union_all(shapely.polygons(triangles[:,:,[0,2]]));overlaps=[]
        for form in current:
            polygon=shapely.Polygon(form['rings'][0],form['rings'][1:]);area=projection.intersection(polygon).area
            if area>1e-8:overlaps.append(dict(uid=form['uid'],name=form.get('name'),buildingCSUID=form.get('buildingCSUID'),sourceFormSHA256=digest(__import__('json').dumps(form,sort_keys=True,separators=(',',':')).encode()),projectedOverlapM2=area,formCoverageFraction=area/polygon.area))
        roots.append(dict(name=gltf['nodes'][root]['name'],completeOriginalFaces=len(triangles),worldBounds=[triangles.min((0,1)).tolist(),triangles.max((0,1)).tolist()],originalWorldSHA256=digest(triangles.astype('<f8').tobytes()),positiveProjectedFormOverlaps=overlaps))
    assert len(arrays)==2 and np.array_equal(np.concatenate(arrays),whole)
    delta=arrays[1]-arrays[0];translation=delta[0,0];identical=np.array_equal(delta,np.broadcast_to(translation,delta.shape))
    result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],completeFaces=len(whole),roots=roots,providerAuthoredRoots=True,completeRootsEqualCurrentPackedOriginal=True,rootsAreExactTranslatedCopies=identical,translationIfExact=translation.tolist()if identical else None,rawIdentityReasons=identity['reasons'],sourceIdentityInterpretationApproved=False,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceCorruptionEstablished=False,qualification='All provider roots and faces retained. Exact copy/translation and current projected overlaps are measured, not interpreted as corruption or duplicate identity. Current component/root identity and Dock1A interfaces remain unresolved. Do not delete a root, translate the source, suppress neighbours, or grant publication from this diagnostic.')
    save(doc/'summary.json',result);save(doc/'current-forms.json',dict(rows=current))
    module('root_counterpart_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-provider-root-current-counterpart-measurements-no-acceptance',list(dict.fromkeys(refs)),result)
    print(dict(exactTranslatedCopies=identical,roots=roots),flush=True)

if __name__=='__main__':main()
