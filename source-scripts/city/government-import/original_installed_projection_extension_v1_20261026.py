"""Measure whether unchanged installed originals cover a saved companion gap."""
from pathlib import Path
import argparse
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_companion_projection_coverage_v1_20261026 import above_height_projection


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ['batch','coverage','native-context']:p.add_argument('--'+k,required=True)
    p.add_argument('--native',action='append',required=True);a=p.parse_args()
    base=ROOT/'docs/astra-city/government-import';out=base/a.batch;assert not out.exists() and a.batch.startswith('government-xl-') and '/' not in a.batch
    refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_companion_projection_coverage_v1_20261026.py'];pins={}
    def take(name,file):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        path=base/name/file;assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    coverage=take(a.coverage,'summary.json');diagnostic=take(a.coverage,'projection-diagnostic.json.gz')
    target=shapely.from_geojson(diagnostic['target']);combined=shapely.from_geojson(diagnostic['combinedOriginalProjection']);high=shapely.from_geojson(diagnostic['combinedAtOrAboveRecordedTop'])
    missing=target.difference(combined);assert abs(missing.area-coverage['remainingUncoveredTargetAreaM2'])<1e-9
    context=take(a.native_context,'native-input.json.gz');by={r['uid']:r for r in context['rows']}
    assert len(a.native)==len(set(a.native)) and set(a.native)<=by.keys()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==coverage['currentManifestSHA256'];refs.append(manifest)
    all_current={}
    for url in read(manifest)['officialModelCatalogues']:
        cat=ROOT/'3d-viewer'/url
        for entry in read(cat)['models']:
            if entry['uid'] in a.native:all_current[entry['uid']]=(entry,cat)
    assert set(all_current)==set(a.native);rows=[];polygons=[combined];uppers=[high]
    for uid in a.native:
        row=by[uid];entry,cat=all_current[uid];assert entry==row['entry'];asset=cat.parent/entry['asset'];assert asset==ROOT/row['path'] and digest(asset.read_bytes())==entry['sha256'];refs.extend([cat,asset])
        tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==entry['triangles']
        shape=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));upper=above_height_projection(tri,coverage['recordedTargetTopHKPD']);polygons.append(shape);uppers.append(upper)
        rows.append(dict(uid=uid,sha256=entry['sha256'],originalFaces=len(tri),missingTargetAreaCoveredM2=shape.intersection(missing).area,missingTargetAreaCoveredAtOrAboveRecordedTopM2=upper.intersection(missing).area))
    extended=shapely.union_all(polygons);extended_high=shapely.union_all(uppers)
    result=dict(uids=coverage['uids'],includedInstalledUids=a.native,currentManifestSHA256=coverage['currentManifestSHA256'],previousUncoveredTargetAreaM2=missing.area,remainingUncoveredTargetAreaM2=target.difference(extended).area,combinedCoverageFraction=extended.intersection(target).area/target.area,remainingGapAreaCoveredAtOrAboveRecordedTopM2=extended_high.intersection(missing).area,rows=rows,sourceGeometryChanges=0,existingNativeEntriesChanged=False,existingModelsReapproved=False,identityApproved=False,installationApproved=False,permanentRejection=False,qualification='Diagnostic Float64 projection only, using exact unchanged current installed entries and original bytes. Does not establish ownership, height/terrain/support compatibility or permission to remove baseline regions. Existing models receive no new acceptance.')
    save(out/'summary.json',result);save(out/'remaining-target-gap.json.gz',dict(geometry=shapely.to_geojson(target.difference(extended))))
    module('installed_projection_extension_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'unchanged-installed-original-target-gap-projection-context',refs,result)
    print(result,flush=True)


if __name__=='__main__':main()
