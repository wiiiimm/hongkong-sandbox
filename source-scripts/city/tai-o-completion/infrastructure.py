"""Retain and bake existing official Tai O infrastructure; no source geometry edits."""
import argparse, gzip, hashlib, json, pathlib, subprocess, sys, zipfile
import numpy as np
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
ROOT=pathlib.Path(__file__).resolve().parents[3]
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry
from bake_model_geometry import bake

def build(publish=False):
    assets=HERE/'infrastructure-assets';models=[];sources=[]
    config=json.loads((HERE/'infrastructure-config.json').read_text())
    bridges={b['id']:b for b in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']}
    for sheet in ['9-SW-23A','9-SW-23B']:
        folder=ROOT/'source-scripts/city/tai-o-models/sources'/sheet
        archive=folder/(sheet+'.zip');download=json.loads((folder/'download.json').read_text())
        assert hashlib.sha256(archive.read_bytes()).hexdigest()==download['sha256']
        sources.append({'sheet':sheet,'sourceUrl':download['source'],'revision':download['revisionDate'],'cacheSha256':download['sha256'],'cacheKind':download.get('cacheKind'),'entries':[]})
        with zipfile.ZipFile(archive) as z:
            for name in sorted(n for n in z.namelist() if n.startswith('INFRASTRUCTURE/') and n.endswith('.gltf')):
                raw=z.read(name);data=json.loads(raw);parent=pathlib.PurePosixPath(name).parent
                positions,triangles=model_geometry(data,lambda uri:z.read(str(parent/uri)))
                hashes={}
                for entry in [name]+[str(parent/b['uri']) for b in data['buffers']]:
                    rel=pathlib.PurePosixPath(entry);assert not rel.is_absolute() and '..' not in rel.parts
                    target=assets/sheet/entry;target.parent.mkdir(parents=True,exist_ok=True)
                    content=z.read(entry);target.write_bytes(content);hashes[entry]=hashlib.sha256(content).hexdigest()
                spec={'id':pathlib.PurePosixPath(name).stem,'url':sheet+'/'+name,'sourceEntry':name,'worldBounds':[positions.min(axis=0).tolist(),positions.max(axis=0).tolist()],'sourceHashes':hashes,'officialMatches':[]}
                geometry=bake(spec,assets)
                meta=config['models'][spec['id']].copy()
                assert hashes[name]==meta['reviewedSourceGltfSha256'],'Source changed: re-review floor indices before rebuilding'
                indices=[i for a,b in meta.pop('walkTriangleRangesInclusive') for i in range(a,b+1)]
                alltri=np.array(geometry['position']).reshape(-1,3,3);floors=alltri[indices]
                cross=np.cross(floors[:,1]-floors[:,0],floors[:,2]-floors[:,0]);norm=np.linalg.norm(cross,axis=1)
                assert np.all(cross[:,1]/norm>.6),'Selected face is not upward-facing floor'
                floor=unary_union([Polygon(t[:,[0,2]]) for t in floors]);assert floor.is_valid
                projected=unary_union([Polygon(t[:,[0,2]]) for t in alltri if Polygon(t[:,[0,2]]).area>1e-8])
                duplicates=[]
                for bid in meta['suppresses']:
                    proxy=bridges[bid];line=LineString(proxy['path']);ratio=line.intersection(projected).length/line.length
                    buffered=line.intersection(projected.buffer(1.5)).length/line.length
                    assert ratio>=.85 and buffered>.99999,'Candidate proxy is insufficiently aligned with source'
                    duplicates.append({'id':bid,'source':proxy['source'],'pathInsideExactModelFraction':ratio,'pathInsideModelWith1_5mMapToleranceFraction':buffered,'policy':'Suppress this generic bridge only after valid source mesh has loaded. Keep original record for identity; source height/width/approaches supersede generic estimates. 1.5m is an explicit map-alignment tolerance, not a shifted source model.'})
                walk={'triangleIndices':indices,'estimatedElevation':False,'elevationBasis':'Selected original LandsD glTF deck top triangles in HKPD; no layer-to-height conversion or terrain lifting.','worldBounds':[floors.min(axis=(0,1)).tolist(),floors.max(axis=(0,1)).tolist()],'projectedArea':floor.area,'connectedComponents':len(floor.geoms) if hasattr(floor,'geoms') else 1,'triangleCount':len(indices),'extractionNote':meta.pop('floorSelectionNote')}
                if meta.get('routeProxyId'):
                    line=LineString(bridges[meta['routeProxyId']]['path']);samples=[line.interpolate(float(d)) for d in np.linspace(0,line.length,int(np.ceil(line.length/.25))+1)]
                    walk['routeAudit']={'proxyId':meta['routeProxyId'],'samples':len(samples),'sampleStepMaxMetres':.25,'centreSamplesOnDeck':sum(floor.covers(p) for p in samples),'minimumCentreToBoundaryMetres':min(p.distance(floor.boundary) for p in samples),'walkingRadiusTestMetres':.55,'discSamplesOnDeck':sum(floor.covers(p.buffer(.55)) for p in samples),'note':'Guidance diagnostic, not approval to override building or deck-edge collision.'}
                models.append({'id':'landsd-infrastructure/'+spec['id'],'sheet':sheet,'sourceUrl':download['source'],'sourceRevision':download['revisionDate'],'modelGeometry':geometry,'worldBounds':geometry['worldBounds'],**meta,'walkTriangleIndices':indices,'walkSurface':walk,'duplicateSuppression':duplicates})
                sources[-1]['entries'].append({'entry':name,'sha256':hashes[name]})
    result={'schemaVersion':1,'kind':'tai-o-official-infrastructure','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','coordinatePolicy':'Exact original glTF hierarchy, then x=E-834500, y=HKPD height, z=816500-N. No elevation, simplification or support geometry adjustments.','models':models,'sources':sources,'counts':{'models':len(models),'sourceTriangles':sum(m['modelGeometry']['triangles'] for m in models),'publicWalkModels':sum(m['walkable'] for m in models),'publicWalkTriangles':sum(len(m['walkTriangleIndices']) for m in models if m['walkable']),'genericBridgeProxiesReplaced':sum(len(m['suppresses']) for m in models)},'limits':['Five infrastructure models are the complete INFRASTRUCTURE set in the two retained non-textured sheets, not every Tai O structure.','No individual stilt-house pile heights/locations or private boardwalk access are inferred.','Yim Tin and Po Chue Tam bridge names/opening are documented, but these five source meshes do not include them; retain their current mapped source paths and estimated elevations.','Source triangles preserve the source snapshot configuration of movable bridges; no opening or tidal deformation is invented.']}
    raw=json.dumps(result,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
    (HERE/'infrastructure-models.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    if publish:
        subprocess.run(['node',str(HERE/'infrastructure-access.mjs')],cwd=ROOT,check=True,capture_output=True)
        access=json.loads((HERE/'infrastructure-access.json').read_text());public={**result,'approaches':access['records'],'canopyEstimates':access['canopyEstimates']}
        public['counts']={**result['counts'],'estimatedPublicApproaches':len(access['records']),'scopedCanopyEstimates':len(access['canopyEstimates'])}
        published=json.dumps(public,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
        output=ROOT/'3d-viewer/city/data/bridges-tai-o.json'
        temporary=output.with_suffix('.json.tmp');temporary.write_bytes(published);temporary.replace(output)
        manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=json.loads(manifest_path.read_text())
        manifest['bridgeModels']=list(dict.fromkeys([*manifest.get('bridgeModels',[]),'city/data/bridges-tai-o.json']))
        temporary=manifest_path.with_suffix('.json.tmp');temporary.write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+'\n');temporary.replace(manifest_path)
    brief={'models':len(models),'triangles':sum(m['modelGeometry']['triangles'] for m in models),'bytes':len(raw),'gzipBytes':len(gzip.compress(raw,mtime=0)),'items':[{k:v for k,v in m.items() if k!='modelGeometry'}|{'triangles':m['modelGeometry']['triangles']} for m in models]}
    (ROOT/'docs/astra-city/tai-o-completion/infrastructure-build.json').write_text(json.dumps(brief,indent=2)+'\n')
    print(json.dumps({k:v for k,v in brief.items() if k!='items'},indent=2))
    return result
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--publish',action='store_true',help='Publish verified mesh package and add manifest bridgeModels; preserve other keys')
    build(parser.parse_args().publish)
