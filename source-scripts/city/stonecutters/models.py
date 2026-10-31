"""Assemble original deck + two original tower meshes without modifying geometry."""
import importlib.util,hashlib,json,pathlib,sys
import numpy as np
from shapely.geometry import MultiPoint,Polygon,LineString
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/stonecutters'
spec=importlib.util.spec_from_file_location('ting_kau_sources',HERE.parent/'ting-kau/models.py');shared=importlib.util.module_from_spec(spec);spec.loader.exec_module(shared)
original=shared.original;bake=shared.bake
DECK='I296272022407063C0'
TOWERS=[('B298652107401063C0','10-NE-15B','landsd/75319:0','Tsing Yi tower'),('B306502042501063C0','11-NW-11C','landsd/75938:0','Stonecutters Island tower')]

def build():
    wanted={r[2] for r in TOWERS};buildings={}
    for tile in json.loads((ROOT/'3d-viewer/city/data/manifest.json').read_text())['tiles']:
        x0,z0,x1,z1=tile['bounds']
        if x1<-5000 or x0>-3500 or z1<-4900 or z0>-3600:continue
        for b in json.loads((ROOT/'3d-viewer'/tile['url']).read_text())['buildings']:
            if b['uid'] in wanted:buildings[b['uid']]=b
    assert set(buildings)==wanted
    assets=HERE/'assets';sources=[];models=[];proofs=[]
    configs=[(DECK,'11-NW-11C',None,'original deck and supports','sources')]+[(mid,sheet,uid,name,'towers/sources') for mid,sheet,uid,name in TOWERS]
    for mid,sheet,uid,name,folder in configs:
        p,t,spec,meta=original(HERE/folder/sheet,mid,assets)
        matches=[]
        if uid:
            b=buildings[uid];assert b['buildingCSUID'].startswith(mid[1:11]);poly=Polygon(b['rings'][0],b['rings'][1:]);hull=MultiPoint(p[:,[0,2]]).convex_hull
            overlap=poly.intersection(hull).area/min(poly.area,hull.area);assert overlap>.75
            match={'uid':uid,'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'sourceBaseHeightHKPD':b['baseHeightHKPD'],'sourceTopHeightHKPD':b['topHeightHKPD'],'identityModel':mid,'identityWorldBounds':spec['worldBounds'],'identitySourceUrl':meta['source'],'identityHashes':spec['sourceHashes'],'overlapOfSmallerFootprint':overlap,'sourceModelTopMinusBuildingTopMetres':float(p[:,1].max()-b['topHeightHKPD']),'policy':'Exact GeoRefNo/CSUID prefix and overlapping original geometry. Keep footprint source values; suppress only its extrusion after this valid original tower loads. Mesh upper extent differs from building metadata/design tower height; no model scaling or elevation correction is applied.'}
            matches=[match];proofs.append(match)
        spec['officialMatches']=matches;g=bake(spec,assets);assert g['triangles']==t
        m={'id':'landsd-infrastructure/'+mid,'name':'Stonecutters Bridge · '+name,'zh':'昂船洲大橋','sheet':sheet,'sourceUrl':meta['source'],'sourceRevision':meta['revisionDate'],'modelGeometry':g,'worldBounds':g['worldBounds'],'walkable':False,'walkTriangleIndices':[],'suppresses':[],'suppressesBuildingUids':[uid] if uid else [],'buildingMatches':matches,'elevationBasis':'Original source hierarchy transformed to Hong Kong Principal Datum city coordinates. Mesh vertices are unchanged; maximum model elevation is distinct from a building-record roof level.','accessNote':'Motorway bridge; no public pedestrian access is inferred.'}
        models.append(m);sources.append({'modelId':mid,'sourceUrl':meta['source'],'sourceRevision':meta['revisionDate'],'cacheKind':meta['cacheKind'],'cacheSha256':meta['sha256'],'sourceHashes':spec['sourceHashes']})
        if not uid:deck_hull=MultiPoint(p[:,[0,2]]).convex_hull
    coverage=[];clips=[]
    for b in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']:
        if b.get('name')!='Stonecutters Bridge':continue
        line=LineString(b['path']);keep=line.difference(deck_hull.buffer(1.5));ratio=1-keep.length/line.length
        coverage.append({'id':b['id'],'originalLengthMetres':line.length,'sourceHullCoverageWith1_5mTolerance':ratio,'source':b['source']})
        if keep.length<.001:models[0]['suppresses'].append(b['id'])
        elif ratio>0:
            parts=list(keep.geoms) if hasattr(keep,'geoms') else [keep]
            clips.append({'id':b['id'],'source':b['source'],'keepPaths':[[list(q) for q in part.coords] for part in parts if part.length>1e-6],'originalLengthMetres':line.length,'retainedLengthMetres':keep.length,'replacedLengthMetres':line.length-keep.length,'policy':'Only the source bridge hull plus an explicit 1.5 m map tolerance replaces mapped geometry; unmatched original approach tails remain.'})
    a,b=[np.mean(np.array(m['worldBounds'])[:,[0,2]],axis=0) for m in models[1:]]
    out={'schemaVersion':1,'kind':'official-infrastructure','region':'stonecutters','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','coordinatePolicy':'Original hierarchy then city translation [-834500,0,816500], without model rescaling or height adjustment.','models':models,'sources':sources,'proxyClips':clips,'counts':{'models':len(models),'sourceTriangles':sum(m['modelGeometry']['triangles'] for m in models),'publicWalkModels':0,'matchedBuildingExtrusions':len(proofs),'genericBridgeProxiesReplaced':len(models[0]['suppresses']),'partiallyReplacedProxies':len(clips)},'limits':['Deck and towers are separate original government models.','Source tower upper extents differ from the recorded/design top of298 m; all source values are retained.','Cable availability is audited separately; any added cables must be labelled illustrative.','No public walking, traffic simulation or surveyed bathymetry is inferred.']}
    (HERE/'bridges-stonecutters.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
    report={'counts':out['counts'],'sourceComponents':[{'id':m['id'],'worldBounds':m['worldBounds'],'triangles':m['modelGeometry']['triangles']} for m in models],'towerMatches':proofs,'towerHorizontalSeparationMetres':float(np.linalg.norm(b-a)),'proxyCoverage':coverage,'proxyClips':clips,'bridgePacketSha256':hashlib.sha256((HERE/'bridges-stonecutters.json').read_bytes()).hexdigest(),'published':False}
    (DOC/'model-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report['counts']));return out
if __name__=='__main__':build()
