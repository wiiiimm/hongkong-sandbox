"""Review two exact Peninsula source associations, preserving physical obligations."""
from pathlib import Path
import re
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-peninsula-exact-source-association-review-v1-20261029'
RUNTIME='government-xl-peninsula-pair-current-v1-20261029-runtime';IDENTITY='government-xl-peninsula-pair-current-v1-20261029-identity';PRIMARY='government-xl-peninsula-primary-component-context-v1-20261029'

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(n,p):
        if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
        assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');primary=take(PRIMARY,BASE/PRIMARY/'summary.json');assert primary['currentPrimaryRecords'][0]['passed']
    official=primary['currentPrimaryRecords'][0]['features'];assert len(official)==2
    osm=primary['overlappingOSMForm'];assert osm['passed']and osm['id']=='709674357'and osm['version']=='4'and osm['tags']['building:part']=='roof'
    sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert sources==primary['sourceSHA256ByUid']
    assert sources=={'landsd/270876:0':'3a40860e5302240d814f907d2f1edabc4b3c7becab1c90d37f406d2a4ce631f2','landsd/266543:0':'4c40dd7918c6677d6fa564bb28daac019a8cd8af8d713897678ad03be27e3521'}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    reviews=[]
    for row in selection['rows']:
        uid=row['uid'];b=row['source']['building'];raw=take(IDENTITY,BASE/IDENTITY/(uid.split('/')[1])/'identity.json');ownership=raw['originalOwnership']
        assert ownership['sourceGraphVerified']and ownership['originalRootName']==row['modelId']
        assert raw['sourceSHA256']==sources[uid]and raw['freshCurrentIdentity']['exactObjectAndCSUID']
        matches=[f for f in official if f['attributes']['BuildingCSUID']==b['buildingCSUID']];assert len(matches)==1;fresh=matches[0]['attributes']
        assert fresh['Status']=='Active'and fresh['BuildingID']==b['buildingId']and fresh['BuildingBlockType']==b['structureType']=='Tower'
        assert fresh['BaseHeight']==b['baseHeightHKPD']and abs(fresh['TopHeight']-b['topHeightHKPD'])<1e-12
        csuid=b['buildingCSUID'];mid=row['modelId'];assert re.fullmatch(r'B[0-9]{10}(01|02)063C0',mid)and mid[1:11]==csuid[:10]and csuid[10]=='T'
        assert (uid,mid[11:13])in [('landsd/270876:0','02'),('landsd/266543:0','01')]
        east=800000+int(csuid[:5]);north=800000+int(csuid[5:10]);cell=shapely.box(east-834500,816500-north-1,east-834500+1,816500-north)
        target=shapely.Polygon(b['rings'][0],b['rings'][1:]);path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==sources[uid];refs.append(path);tri=decode_original_world_triangles(path.read_bytes());projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]))
        assert len(tri)==row['triangles']and digest(tri.astype('<f8').tobytes())==raw['worldTrianglesSHA256']
        assert target.covers(cell)and projection.covers(cell)
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']and [f for f in read(tile)['buildings']if f['uid']==uid]==[b];refs.append(tile)
        reviews.append(dict(uid=uid,sourceSHA256=sources[uid],modelId=mid,buildingCSUID=csuid,buildingId=b['buildingId'],pinnedViewerObjectId=b['objectId'],freshProviderObjectId=fresh['OBJECTID'],wholeOneMetreCellWKT=cell.wkt,targetCoversWholeCell=True,sourceCoversWholeCell=True,wholeSourceGraphVerified=True,sourceWorldSHA256=raw['worldTrianglesSHA256'],current2DStructureType='Tower',nativeSubtype=mid[11:13],exactSourceAssociationAccepted=True,sourceRole=('Lower original hotel body including courtyard/entrance roof'if uid=='landsd/270876:0'else'Original upper Peninsula hotel/office tower with twin rooftop pads'),rawIdentityReasonsVerbatim=raw['reasons']))
    views=[]
    for n,files in [('government-xl-peninsula-original-pair-assembly-views-v1-20261029',['complete-original-assembly.png','base-only-diagnostic.png']),('government-xl-peninsula-office-28-junction-views-v1-20261029',[f'residual-witnesses-{i}.png'for i in range(1,5)]),('government-xl-peninsula-osm-roof-contact-views-v1-20261029',['before-after-contact-context.png'])]:
        take(n,BASE/n/'summary.json')
        for filename in files:
            p=BASE/n/filename;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);views.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    result=dict(uids=list(sources),sourceSHA256ByUid=sources,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),reviewer='Codex ROOT',reviewType='exact-original-native-root-stable-CSUID-and-BuildingID-association-only',exactSourceAssociationAccepted=True,identityAcceptedForSourceAssociationOnly=True,rows=reviews,imagesActuallyViewed=views,foreignRoofRecord=osm,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='ROOT inspected complete assembly, base-only, all28 residual-junction and exact roof contact images. Both primary records bind exact stable CSUID and BuildingID; viewer and live provider OBJECTIDs are explicitly distinct reindexed values. Native subtype02 of the lower original coexists with authoritative2D Tower/T CSUID; accept this exact named source association only, without coercing2D records or changing generic type checking. Full source graph, exact bytes/pose/world hash and whole1m cell remain verified. Raw spatial/type/support negatives remain verbatim. Current OSM version4 declares the overlapping form a roof component; conditional replacement still requires exact feature, collision and full lifecycle review. This does not grant whole-source placement, physical, suppression, browser or publication approval.')
    save(out/'ROOT-IDENTITY-REVIEW.json',result);save(out/'summary.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('peninsula_source_association_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-two-exact-original-Peninsula-primary-source-association-review',refs,result)

if __name__=='__main__':main()
