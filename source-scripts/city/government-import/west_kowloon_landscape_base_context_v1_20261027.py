"""Bind buried auxiliary surfaces to exact source topology and primary photographs."""
from pathlib import Path
from fractions import Fraction
import json
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_negative_face_component_context_v2_20261027 import component_context


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-west-kowloon-north-landscape-base-context-v1-20261027';out=base/batch;assert not out.exists()
    refs=[Path(__file__),HERE/'original_negative_face_component_context_v2_20261027.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(base/name)[1];refs.append(base/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    uid='landsd/182397:0';runtime='government-xl-after-dragon-next-five-ground-v1-20261026'
    source=next(r for r in take(runtime,base/runtime/'selection.json.gz')['rows']if r['uid']==uid)
    warnings=take('government-xl-west-kowloon-north-original-tin-failing-facets-v1-20261027',base/'government-xl-west-kowloon-north-original-tin-failing-facets-v1-20261027/summary.json')
    columns=take('government-xl-west-kowloon-north-original-tin-full-columns-v1-20261027',base/'government-xl-west-kowloon-north-original-tin-full-columns-v1-20261027/summary.json')
    views=take('government-xl-west-kowloon-north-original-tin-warning-views-v1-20261027',base/'government-xl-west-kowloon-north-original-tin-warning-views-v1-20261027/summary.json')
    tile=ROOT/'3d-viewer'/source['source']['tile'];assert digest(tile.read_bytes())==source['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==uid)==source['source']['building'];refs.append(tile)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256']==warnings['sourceSHA256']==columns['sourceSHA256'];refs.append(asset)
    tri=decode_original_world_triangles(asset.read_bytes());assert digest(tri.astype('<f8').tobytes())==warnings['sourceWorldSHA256']==columns['sourceWorldSHA256']
    ids=[r['sourceFace']for r in warnings['rows']];assert ids==columns['explicitScopedSourceFaces']==views['sourceFaces']
    ring=np.asarray(source['source']['building']['rings'][0]);core_lo,core_hi=ring.min(0),ring.max(0)
    rows=[]
    for record in columns['rows']:
        i=record['sourceFace'];t=tri[i];lo,hi=t[:,[0,2]].min(0),t[:,[0,2]].max(0);gaps=np.maximum(core_lo-hi,lo-core_hi)
        assert np.any(gaps>0),'Warning overlaps core footprint bounds'
        assert record['completeProjectionCovered'] and Fraction(record['exactMaximumGapM'])<0
        rows.append(dict(sourceFace=i,strictCoreFootprintSeparatingAxisGapsM=gaps.tolist(),exactMaximumSourceMinusOriginalTerrainM=record['exactMaximumGapM'],entireFacetStrictlyBelowEveryOverlappingOriginalTerrainFacet=True))
    remaining=set(ids);components=[]
    while remaining:
        representative=min(remaining);context=component_context(tri,representative);members=set(context['componentFaceIds']);covered=sorted(remaining&members);remaining-=members
        components.append(dict(representative=context,warningFacesInComponent=covered))
    photo_root=HERE/'local/government-xl-west-kowloon-north-primary-photos-v1-20261027';retrieval=photo_root/'retrieval.json';photos=read(retrieval);refs.append(retrieval)
    for r in photos:
        if 'path' in r:
            p=ROOT/r['path'];assert digest(p.read_bytes())==r['sha256'];refs.append(p)
    assert len([r for r in photos if 'path'in r])==3
    inspected=[]
    for r in views['exports']:
        p=ROOT/r['path'];assert digest(p.read_bytes())==r['sha256'];refs.append(p);inspected.append(r)
    bibliography=[dict(url='https://www.archsd.gov.hk/en/exhibition/5798_Construction_of_West_Kowloon_Government_Offices.html',observation='ArchSD project description identifies the two towers and1.5-storey basement; its labelled North Tower lobby/ground photographs show the entrance, planted beds and flagpoles. The description alone does not assign a role to any mesh facet.'),dict(url='https://fpf.ccidahk.gov.hk/en/location/detail.php?id=1948',observation='Government location library describes the interconnecting landscaped public/vehicular space. Its fourth photograph shows raised planting beside the paved path. No precise survey heights are inferred.')]
    result=dict(uids=[uid],sourceSHA256=source['sourceSHA256'],sourceWorldSHA256=warnings['sourceWorldSHA256'],originalTerrainSHA256=warnings['originalTerrainSHA256'],allWarningFacetsStrictlyOutsideCoreFootprint=True,allWarningFacetsCompletelyMaskedByOriginalTerrain=True,warningRows=rows,exactSharedEdgeComponentContext=components,primaryPhotoRetrieval=photos,primarySources=bibliography,rootActuallyViewedPhotos=[r for r in photos if 'path'in r],rootActuallyViewedOriginalTINExports=inspected,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,landscapeBaseInterpretationProposed=True,sourceRoleAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Source-specific landscape-base interpretation proposed for35 entirely masked auxiliary facets outside the tower core. Exact full-facet original-TIN bounds and shared-edge source components preserved. Primary photographs and all3 original-TIN plots actually viewed by ROOT. This context is not source-role/physical acceptance and does not lower terrain or erase upward-face failures. Source4-point foundation records and current-renderer obligations remain unchanged.')
    result=json.loads(json.dumps(result,allow_nan=False));save(out/'summary.json',result)
    module('west_kowloon_landscape_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-outside-core-masked-original-landscape-base-context',refs,result)
    print(dict(maskedAuxiliaryFaces=len(rows),exactWholeSourceComponents=len(components),sourceRoleAccepted=False),flush=True)

if __name__=='__main__':main()
