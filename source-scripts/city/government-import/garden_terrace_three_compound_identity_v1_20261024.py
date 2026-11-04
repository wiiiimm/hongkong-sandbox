"""Exact three-source Garden Terrace footprint identity; physical gates stay separate."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-next-repairs-garden-terrace2-';BATCH=P+'three-compound-identity-v1-20261024'
SOURCES={'landsd/109491:0':'d6f60c07b429bd89b7c45b09f3a3077960ecbd96898c833684a564d1a4fb9f2e','landsd/162285:0':'331e11c7d4e5834397430c9b10d10e753f550e080f398c75d8b390741ebc1cbd','landsd/21894:0':'ea3b2a1531c7cce1f1d3915bc3014bc5eab2f0cef807fe3f581bf9f1320f4e5f'}

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(name,path):
        if name not in pins:pins[name]=authenticate(BASE/name)[1];refs.append(BASE/name/'result.json')
        assert digest(path.read_bytes())==pins[name][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    runtime=P+'three-current-runtime-v1-20261024';selection=take(runtime,BASE/runtime/'selection.json.gz');assert{r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    scopeName=P+'three-current-model-scope-v1-20261024';scope=take(scopeName,BASE/scopeName/'summary.json');assert scope['currentManifestSHA256']==selection['manifestSHA256'];forms={}
    for r in scope['rows']:
        for item in take(scopeName,BASE/scopeName/(r['uid'].split('/')[1]+'-forms.json.gz')):forms[item['building']['uid']]=item['building']
    polygons={u:shapely.Polygon(forms[u]['rings'][0],forms[u]['rings'][1:])for u in SOURCES};assert all(p.is_valid and p.area>0 for p in polygons.values());assembly=shapely.union_all(list(polygons.values()));foreign=shapely.union_all([shapely.Polygon(f['rings'][0],f['rings'][1:])for u,f in forms.items()if u not in SOURCES]);rows=[]
    pairName=P+'three-original-pair-context-v1-20261024';pairs=take(pairName,BASE/pairName/'summary.json');assert pairs['sourceSHA256ByUid']==SOURCES and pairs['completeUnorderedPairs']==3 and len(pairs['rows'])==12 and all(not r['strictBoundsSeparated']and r['positiveSurfaceContacts']>0 for r in pairs['rows'])
    for number in ['109491','21894']:
        name=P+number+'-original-podium-paths-v1-20261024';paths=take(name,BASE/name/'summary.json');assert paths['allUnresolvedHaveFinitePaths']and len(paths['rows'])==4 and all(r['verifiedPaths']==r['targets']and not r['remaining']for r in paths['rows'])
    for row in selection['rows']:
        uid=row['uid'];name=P+'three-current-identity-v1-20261024';path=BASE/name/(uid.split('/')[1]+'/identity.json');raw=take(name,path)
        assert raw['sourceSHA256']==SOURCES[uid]and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']and raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']==row['modelId']
        if uid=='landsd/109491:0':assert set(raw['reasons'])=={'fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent'}
        else:assert raw['passed']and not raw['reasons']
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));own=polygons[uid];coverage=projection.intersection(own).area/own.area;extent=float(shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),assembly).max());unrelated=projection.difference(assembly).intersection(foreign).area
        assert coverage>=.95 and extent<=10 and unrelated<=1
        rows.append(dict(uid=uid,sourceSHA256=SOURCES[uid],completeOriginalFaces=len(tri),ownTargetCoverage=coverage,completeOriginalExtentFromVerifiedAssemblyM=extent,unrelatedExcessOutsideAssemblyM2=unrelated,rawIdentityPath=str(path.relative_to(ROOT)),rawReasonsRetained=raw['reasons'],identityAccepted=True,proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']}))
    result=dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,requiredUnchangedAssembly=SOURCES,rows=rows,identityAccepted=True,sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,qualification='Exact named original Blocks2/3 and source-owned common podium only; all three hashes must remain together. Unique current GeoRef/type/CSUID/ObjectID routes, root graphs and complete coordinate cells stay required. Original-coordinate own footprint coverage95percent, extent10m and unrelated overlap1m2 limits are unchanged. Only Block2 individual maximum-extent reasons are qualified by its authored lower extension inside the verified connected three-source assembly; raw negatives stay archived. No support, actual-ground, native neighbour, browser, publication or optimisation approval is inferred.')
    save(out/'identity.json',result);refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('garden_compound_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-three-original-garden-terrace-compound-footprint-identity',refs,result)

if __name__=='__main__':main()
