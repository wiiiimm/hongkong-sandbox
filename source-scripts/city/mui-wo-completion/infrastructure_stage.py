"""Stage existing Mui Wo source infrastructure through the shared exact glTF baker.
No new downloads or invented supports; walking faces require separate review.
"""
import gzip,hashlib,json,pathlib,sys,zipfile
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/mui-wo-completion'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry
from bake_model_geometry import bake

def main():
 assets=HERE/'infrastructure-assets';models=[];sources=[];inventory=[]
 config=json.loads((HERE/'infrastructure-config.json').read_text()) if (HERE/'infrastructure-config.json').exists() else None
 proxies=json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']
 for folder in sorted((HERE.parent/'mui-wo-models/sources').iterdir()):
  archive=folder/(folder.name+'.zip');download=json.loads((folder/'download.json').read_text());assert hashlib.sha256(archive.read_bytes()).hexdigest()==download['sha256']
  with zipfile.ZipFile(archive) as z:
   for name in z.namelist():
    if not name.startswith('INFRASTRUCTURE/') or not name.endswith('.gltf'):continue
    d=json.loads(z.read(name));parent=pathlib.PurePosixPath(name).parent;pos,count=model_geometry(d,lambda uri:z.read(str(parent/uri)));hashes={}
    for entry in [name]+[str(parent/b['uri']) for b in d['buffers']]:
     rel=pathlib.PurePosixPath(entry);assert not rel.is_absolute() and '..' not in rel.parts
     target=assets/folder.name/entry;target.parent.mkdir(parents=True,exist_ok=True);raw=z.read(entry);target.write_bytes(raw);hashes[entry]=hashlib.sha256(raw).hexdigest()
    mid=pathlib.PurePosixPath(name).stem;spec={'id':mid,'url':folder.name+'/'+name,'sourceEntry':name,'sourceHashes':hashes,'worldBounds':[pos.min(axis=0).tolist(),pos.max(axis=0).tolist()],'officialMatches':[]};geometry=bake(spec,assets)
    tri=np.asarray(geometry['position']).reshape(-1,3,3);cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);norm=np.linalg.norm(cross,axis=1);up=np.where((norm>1e-8)&(cross[:,1]/np.maximum(norm,1e-30)>.95))[0]
    projection=unary_union([Polygon(t[:,[0,2]]) for t in tri if Polygon(t[:,[0,2]]).area>1e-8]);near=[]
    for proxy in proxies:
     line=LineString(proxy['path'])
     if not line.intersects(projection.buffer(2)):continue
     near.append({'id':proxy['id'],'source':proxy['source'],'name':proxy.get('name'),'tags':proxy.get('tags'),'insideSourceProjectionFraction':line.intersection(projection).length/line.length,'inside2mToleranceFraction':line.intersection(projection.buffer(2)).length/line.length})
    rows=[{'index':int(i),'centre':tri[i].mean(axis=0).tolist(),'bounds':[tri[i].min(axis=0).tolist(),tri[i].max(axis=0).tolist()],'projectedArea':abs(cross[i,1])/2} for i in up]
    models.append({'id':'landsd-infrastructure/'+mid,'name':'Mui Wo source infrastructure '+mid,'sheet':folder.name,'sourceUrl':download['source'],'sourceRevision':download['revisionDate'],'modelGeometry':geometry,'worldBounds':geometry['worldBounds'],'walkable':False,'walkTriangleIndices':[],'suppresses':[],'elevationBasis':'Original source glTF hierarchy in HKPD; no height, plan or support adjustments.','accessNote':'Source infrastructure mesh staged; public walking surface selection and approach checks pending.'})
    if config:
     reviewed=config['models'][mid];assert reviewed['reviewedSourceGltfSha256']==hashes[name];models[-1].update(reviewed);models[-1]['accessNote']='Selected original public floor faces have source and continuous-navigation evidence; width and approach profiles are separately labelled estimates.' if models[-1]['walkable'] else 'Source mesh retained for visual and collision geometry. No public walking floor is enabled for this component.'
     if mid in {'I178501443703063C0','I178581445403063C0'}:models[-1]['accessNote']+=' The May 2026 sheet contains overlapping old/new Wang Tong components; current Highways information states that remaining project works continue. Only the upper western pedestrian floor is enabled; the lower component and cycle floor are not walking surfaces.'
    inventory.append({'id':mid,'sheet':folder.name,'worldBounds':geometry['worldBounds'],'triangles':count,'sourceGltfSha256':hashes[name],'upwardFaces':rows,'nearbyBridgeProxies':near});sources.append({'sheet':folder.name,'sourceUrl':download['source'],'sourceRevision':download['revisionDate'],'cacheSha256':download['sha256'],'sourceHashes':hashes})
 out={'schemaVersion':1,'kind':'official-infrastructure','region':'mui-wo','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','models':models,'sources':sources,'counts':{'models':len(models),'triangles':sum(m['modelGeometry']['triangles'] for m in models),'walkableModels':sum(m['walkable'] for m in models)},'limits':['Uses only exact source infrastructure already retained during HKS-167.','Visual mesh staging does not establish public deck access or safe route approach transitions.']}
 (HERE/'infrastructure-models.json.gz').write_bytes(gzip.compress(json.dumps(out,ensure_ascii=False,separators=(',',':')).encode(),mtime=0));(DOC/'infrastructure-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(out['counts']))
if __name__=='__main__':main()
