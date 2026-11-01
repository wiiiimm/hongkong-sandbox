"""Private existing-renderer foundation diagnostic for two exact unsurveyed temporary forms.

No publisher eligibility, source support credit, model edits or public writes.
"""
import argparse,sys,uuid,subprocess
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from wave_multicore_estimated_bases_v4_20261017 import measure
P='government-xl-academic309823-after-carpark-';BASE=ROOT/'docs/astra-city/government-import'
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['uid','batch','scope','runtime','primary']:ap.add_argument('--'+key,required=True)
    a=ap.parse_args();assert a.uid in ['landsd/309838:0','landsd/339024:0']
    assert all(n.startswith('government-xl-') and '/'not in n for n in [a.batch,a.scope,a.runtime,a.primary])
    batch=a.batch;out=BASE/batch;assert not out.exists();pins={};refs=[Path(__file__),HERE/'wave_multicore_estimated_bases_v4_20261017.py']
    def take(name,path):
        if name not in pins:pins[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    scope=a.scope;runtime=a.runtime;primary=a.primary
    b=next(f for f in take(scope,BASE/scope/'form-obligations.json.gz')if f['uid']==a.uid)
    assert b['structureType']=='Temporary Structure'and b['baseSource']=='terrain-estimated'and b['heightSource']=='estimated'
    assert b['baseHeightHKPD']is None and b['topHeightHKPD']is None and not b.get('modelGeometry')and b.get('foundationBase')is None
    footprint=next(r['attributes']for r in take(primary,BASE/primary/'footprints.json')['features']if r['attributes']['BuildingCSUID']==b['buildingCSUID'])
    assert footprint['BuildingBlockType']=='Temporary Structure'and footprint['BaseHeight']is None and footprint['TopHeight']is None
    selection=take(runtime,BASE/runtime/'selection.json.gz');source=next(r for r in selection['rows']if r['uid']=='landsd/309823:0');g=next(r for r in take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']if r['uid']=='landsd/309823:0');assert source['sourceSHA256']==g['sourceSHA256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');assert next(f for f in read(tile)['buildings']if f['uid']==a.uid)==b;refs.append(tile)
    claim=reservations.claim('temporary-basic-foundation-'+str(uuid.uuid4()),['building:'+a.uid,'building:landsd/309823:0','terrain:city/data/terrain.json'],batch=batch,ttl=1800);assert claim['ok'],claim;lease=claim['reservation']
    try:
        ground=np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);polygon=shapely.Polygon(b['rings'][0],b['rings'][1:]);measurement=measure(ground,polygon)
        polys=shapely.polygons(ground[:,:,[0,2]]);vertical=[];conservative=[measurement['maximum']]
        for i in np.flatnonzero(shapely.area(polys)<=1e-10):
            low,high=ground[i].min(0),ground[i].max(0)
            if polygon.intersects(shapely.box(low[0],low[2],high[0],high[2]).buffer(1e-9)):vertical.append(int(i));conservative.extend(ground[i,:,1].tolist())
        base=float(measurement['minimum']);roof=b['base']+b['height'];covered=measurement['uncoveredAreaM2']<1e-8;roof_clear=roof>max(conservative)+.02
        assert base>=1.2 and base<b['base']-.02
        save(out/'input.json',dict(building=b,expectedUid=a.uid,foundationBase=base))
        save(out/'continuous-footprint-ground.json',dict(measurement=measurement,verticalOrDegenerateConservativeIds=vertical,maximumConservativeGroundHKPD=max(conservative),drawnGroundSHA256=digest(ground.tobytes())))
        tool=HERE/'temporary_basic_foundation_geometry_diagnostic_v1_20261101.mjs';refs.append(tool)
        with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(out.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        proof=read(out/'render-proof.json');assert all(proof[k]for k in ['originalBodyAndRoofPartsExactlyUnchanged','originalBodyVerticesAndWindowMasksExactlyUnchanged','allNewXZFromOriginalFootprint','collisionVolumesExactlyMatchRenderedParts','foundationOnlyBelowOriginalBase'])
        for path,sha in proof['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
        result=dict(uid=a.uid,uids=[a.uid],originalBuilding=b,foundationBase=base,fullFootprintGroundCovered=covered,wholeOriginalRoofClear=roof_clear,originalRoofHKPD=roof,maximumGroundHKPD=max(conservative),existingRendererFoundationMechanism=True,sourceGeometryChanges=0,recordedFieldsChanged=False,nativeSupportCredit=False,publisherEligible=False,physicalAcceptance=False,installationApproved=False,publication=False,renderProof=proof,qualification='Private diagnostic for wholly unsurveyed Temporary Structure. Exact existing body/roof vertices and masks remain unchanged; only the existing renderer foundation volume is added below original base. Complete actual terrain footprint and conservative vertical roof bounds measured. No native-source support credit, publisher route, architectural reconstruction or publication approval.')
        save(out/'summary.json',result);assert reservations.owns(lease)
        module('temporary_basic_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-unsurveyed-temporary-existing-foundation-private-diagnostic',list(dict.fromkeys(refs)),result)
        print(dict(uid=a.uid,covered=covered,roofClear=roof_clear,foundationBase=base,publisherEligible=False),flush=True)
    finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
