"""Stage one official model tile as portable glTF assets and a city-ready manifest.
No geometry or building material is changed. Only the terrain photo dependency
is removed from a separate derived glTF; the original remains in the archive.
"""
import gzip,hashlib,json,pathlib,sys,zipfile
import numpy as np
from shapely.geometry import MultiPoint
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
from compare_official import official_shape


def matrix(node):
    if 'matrix' in node:return np.array(node['matrix']).reshape(4,4,order='F')
    assert not any(k in node for k in ('translation','rotation','scale')),'Unexpected TRS: validate explicitly before using'
    return np.eye(4)


def model_geometry(data,read_buffer):
    arrays=[];triangles=0
    def visit(index,parent):
        nonlocal triangles
        node=data['nodes'][index];world=parent@matrix(node)
        if 'mesh' in node:
            for primitive in data['meshes'][node['mesh']]['primitives']:
                assert primitive.get('mode',4)==4,'Unexpected non-triangle source primitive'
                accessor=data['accessors'][primitive['attributes']['POSITION']];view=data['bufferViews'][accessor['bufferView']]
                assert accessor['componentType']==5126 and accessor['type']=='VEC3' and 'sparse' not in accessor
                raw=read_buffer(data['buffers'][view['buffer']]['uri']);offset=view.get('byteOffset',0)+accessor.get('byteOffset',0)
                local=np.ndarray((accessor['count'],3),dtype='<f4',buffer=raw,offset=offset,strides=(view.get('byteStride',12),4)).astype(float)
                transformed=np.c_[local,np.ones(len(local))]@world.T
                arrays.append(transformed[:,:3]);triangles+=(data['accessors'][primitive['indices']]['count'] if 'indices' in primitive else accessor['count'])//3
        for child in node.get('children',[]):visit(child,world)
    for root in data['scenes'][data.get('scene',0)]['nodes']:visit(root,np.eye(4))
    positions=np.concatenate(arrays);positions[:,0]-=834500;positions[:,2]+=816500
    return positions,triangles


def main():
    archive=HERE/'official-10-SW-12C.zip';download=json.loads((HERE/'model-download.json').read_text())
    official_path=ROOT/'source-scripts/city/mui-wo-buildings/landsd-mui-wo.json.gz';official_raw=gzip.decompress(official_path.read_bytes());official=json.loads(official_raw)
    by_ref={}
    for f in official['features']:by_ref.setdefault(str(f['attributes'].get('GeoRefNo','')),[]).append((f['attributes'],official_shape(f)))
    out=HERE/'model-sample';out.mkdir(exist_ok=True)
    models=[];terrain=None;asset_bytes=0
    with zipfile.ZipFile(archive) as z:
        for name in sorted(n for n in z.namelist() if n.endswith('.gltf')):
            folder=pathlib.PurePosixPath(name).parent;original=z.read(name);data=json.loads(original)
            paths=[str(folder / buffer['uri']) for buffer in data.get('buffers',[])]
            positions,triangles=model_geometry(data,lambda uri:z.read(str(folder/uri)))
            bounds=[positions.min(axis=0).tolist(),positions.max(axis=0).tolist()]
            source_hashes={name:hashlib.sha256(original).hexdigest()}
            # Explicitly copy referenced buffers only: no arbitrary ZIP extraction.
            for path in paths:
                relative=pathlib.PurePosixPath(path)
                assert not relative.is_absolute() and '..' not in relative.parts
                dest=out/path;dest.parent.mkdir(parents=True,exist_ok=True);raw=z.read(path);dest.write_bytes(raw);asset_bytes+=len(raw);source_hashes[path]=hashlib.sha256(raw).hexdigest()
            entry={'id':pathlib.PurePosixPath(name).stem,'url':name,'worldBounds':bounds,'vertices':len(positions),'triangles':triangles,'sourceEntry':name,'sourceHashes':source_hashes,'rootTranslation':[-834500,0,816500]}
            if name.startswith('BUILDING/'):
                dest=out/name;dest.write_bytes(original);asset_bytes+=len(original)
                georef=entry['id'][1:11];hull=MultiPoint(positions[:,[0,2]]).convex_hull
                matches=[]
                for attrs,shape in by_ref.get(georef,[]):
                    overlap=hull.intersection(shape).area/max(.001,min(hull.area,shape.area));centre_distance=hull.centroid.distance(shape.centroid)
                    if overlap>=.5 and centre_distance<=10:
                        matches.append({'buildingCSUID':attrs['BuildingCSUID'],'objectId':attrs['OBJECTID'],'buildingID':attrs['BuildingID'],'geoRefNo':attrs['GeoRefNo'],'blockType':attrs['BuildingBlockType'],'overlapOfSmallerFootprint':round(overlap,5),'footprintCentroidDistanceMetres':round(centre_distance,4),'sourceBaseHeight':attrs.get('BaseHeight'),'sourceTopHeight':attrs.get('TopHeight')})
                entry.update(geoRefNo=georef,officialMatches=matches,officialBuildingCSUIDs=sorted(set(m['buildingCSUID'] for m in matches)),replacementVerified=bool(matches))
                models.append(entry)
            else:
                assert name.startswith('TERRAIN'),'Unexpected model category'
                data.pop('images',None);data.pop('textures',None);data.pop('samplers',None)
                original_materials=data.get('materials',[])
                for material in data.get('materials',[]):
                    material.get('pbrMetallicRoughness',{}).pop('baseColorTexture',None)
                    for key in ('normalTexture','occlusionTexture','emissiveTexture'):material.pop(key,None)
                derived=str(folder/(entry['id']+'-geometry.gltf'));raw=json.dumps(data,separators=(',',':')).encode();(out/derived).write_bytes(raw);asset_bytes+=len(raw)
                terrain={**entry,'url':derived,'photoOmitted':True,'omittedPhotoEntries':[str(folder/image['uri']) for image in json.loads(original).get('images',[])],'originalMaterials':json.loads(original).get('materials',[]),'derivedSha256':hashlib.sha256(raw).hexdigest()}
    manifest={'schemaVersion':1,'kind':'official-mui-wo-model-sample','datasetId':'landsd_rcd_1742809441342_98380','datasetTitle':'Lands Department 3D Visualisation Map (Non-textured models)','datasetMetadataRevision':'2026-08-28','tile':download['sheet'],'tileRevision':download['revisionDate'],'sourceDownload':download['source'],'sourceArchiveSha256':download['sha256'],'crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','axes':'Source glTF node matrices output [E,HKPD height,-N]. Add root translation [-834500,0,816500] for the city; no rotation, scale or height adjustment is added.','rootTranslation':[-834500,0,816500],'officialFootprintDatasetVersion':official['datasetVersion'],'officialFootprintSnapshotSha256':hashlib.sha256(official_raw).hexdigest(),'matchPolicy':'Exact GeoRefNo match plus source-model projected convex hull overlap >=50% of the smaller footprint and centroid difference <=10m. BuildingCSUIDs come directly from those matched official records. No name-only matching. This is a conservative replacement screen, not detailed architectural acceptance.','models':models,'terrain':terrain,'counts':{'buildingModels':len(models),'buildingModelsWithVerifiedOfficialMatch':sum(m['replacementVerified'] for m in models),'matchedOfficialBuildingCSUIDs':len(set(csuid for m in models for csuid in m['officialBuildingCSUIDs'])),'modelVertices':sum(m['vertices'] for m in models),'modelTriangles':sum(m['triangles'] for m in models),'terrainVertices':terrain['vertices'],'terrainTriangles':terrain['triangles'],'assetBytes':asset_bytes},'limits':['The source model tile and Building footprint dataset have different revision dates.','Only explicitly matched BuildingCSUIDs may suppress corresponding extrusions after a successful model load. Unmatched models need source review before production replacement.','Absolute HKPD source placement is unchanged. Existing70m/5m terrain may intersect source geometry.','The source terrain photograph is omitted from the derived glTF; building glTF, vertex colours, material facts and binary geometry are unchanged.','This is one750m×600m tile, not complete Mui Wo 3D coverage.']}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(manifest['counts'],indent=2));print('Terrain bounds',terrain['worldBounds'])
if __name__=='__main__':main()
