"""Expose complete originals behind four preserved source-fit errors; no admission."""
import subprocess
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-after-sha-tin-four-source-fit-context-v1-20261029'
CAP='government-xl-remaining-178-v3-current-scene-v1-20261023-chunk-01-runtime'
UIDS=['landsd/75642:0','landsd/75643:0','landsd/43101:0','landsd/99482:0']

def main():
    out=BASE/BATCH;assert not out.exists();_,pins=authenticate(BASE/CAP)
    path=BASE/CAP/'selection.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))]
    refs=[Path(__file__),BASE/CAP/'result.json',path,HERE/'exact_packed_world_geometry_20261009.py']
    rows=[r for r in read(path)['rows']if r['uid']in UIDS];assert len(rows)==4
    manifest=ROOT/'3d-viewer/city/data/manifest.json';before=digest(manifest.read_bytes());refs.append(manifest)
    errors=read(BASE/CAP/'metrics.json');assert digest((BASE/CAP/'metrics.json').read_bytes())==pins[str((BASE/CAP/'metrics.json').relative_to(ROOT))];refs.append(BASE/CAP/'metrics.json')
    loader=module('four_source_fit_current_forms',HERE/'xl-final-script-pass.py');refs.append(HERE/'xl-final-script-pass.py');models=[];metrics=[]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in rows:
            uid=row['uid'];form=row['source']['building'];tile=ROOT/'3d-viewer'/row['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==form;refs.append(tile)
            old=next(r for r in errors['rows']if r['uid']==uid);assert old['error']=='Official model does not fit its matched footprint'
            asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
            frozen=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone();assert frozen and frozen[0]==row['native']['resultSha']
            model=next(m for m in frozen[1]['models']if m['modelId']==row['modelId']);assert model['asset']['sha256']==row['sourceSHA256']
            tri=decode_original_world_triangles(asset.read_bytes());entry=row['candidate']['entry'];assert len(tri)==entry['triangles']
            lo,hi=tri.min((0,1)),tri.max((0,1));assert np.max(np.abs(np.asarray(entry['worldBounds'])-[lo,hi]))<=.002
            nearby=loader.load_forms([lo[0]-20,lo[2]-20,hi[0]+20,hi[2]+20]);refs.extend(ROOT/'3d-viewer'/tile for _,_,tile in nearby);assert any(b['uid']==uid for b,_,_ in nearby)
            target=shapely.Polygon(form['rings'][0],form['rings'][1:]);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));vertices=tri[:,:,[0,2]].reshape(-1,2)
            metrics.append(dict(uid=uid,modelId=row['modelId'],buildingCSUID=form['buildingCSUID'],sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(tri),currentForm=form,sourceWorldBounds=[lo.tolist(),hi.tolist()],targetAreaM2=target.area,sourceProjectedAreaM2=projection.area,targetCoveredBySource=target.intersection(projection).area/target.area,sourceExcessAreaM2=projection.difference(target).area,maximumSourceVertexDistanceFromTargetM=float(shapely.distance(shapely.points(vertices),target).max()),vertexMetricIsNotContinuousMaximumProof=True,nearbyForms=len(nearby),rawRuntimeGuardErrorRetained=old['error'],sourceGeometryChanges=0))
            models.append(dict(uid=uid,label=form.get('name')or form.get('zh')or uid,assetPath=row['candidate']['path'],sourceSHA256=row['sourceSHA256'],worldBounds=entry['worldBounds'],triangles=entry['triangles'],forms=[b for b,_,_ in nearby],viewDirection=[.7,.8,1]))
    tool=HERE/'xl_remaining_three_source_views_v2_20261019.mjs';refs.append(tool);refs=list(dict.fromkeys(refs));hashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
    save(out/'input.json',dict(models=models,inputHashes=hashes,diagnosticOnly=True,publication=False))
    with(out/'render.log').open('w')as log:subprocess.run(['node',str(tool),'--inputs',str((out/'input.json').relative_to(ROOT)),'--out',str(out.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    report=read(out/'render.json');assert len(report['views'])==4 and not report['errors']
    for view in report['views']:
        image=ROOT/view['image']['path'];assert digest(image.read_bytes())==view['image']['sha256'];refs.append(image)
    for name,sha in report['inputHashes'].items():assert digest((ROOT/name).read_bytes())==sha;refs.append(ROOT/name)
    assert digest(manifest.read_bytes())==before
    result=dict(uids=UIDS,rows=metrics,currentManifestSHA256=before,views=4,rawSourceFitErrorsAreProductionGuards=True,sourceCorruptionEstablished=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,identityAccepted=False,installationApproved=False,publication=False,newlyInstalled=0,qualification='Four exact current source units decode and render in native pose with all faces retained. The prior runtime errors are genuine footprint-fit guard rejections, not software crashes or proven corrupt sources. Complete original/context views and raw projection differences support source identity/boundary investigation only. No guard weakened, footprint scope installed, current model replaced or source geometry edited.')
    save(out/'summary.json',result)
    module('four_source_fit_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-exact-source-fit-context-and-native-pose-views',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
