"""Bounded HKS-214 roof/terrain audit. Read cached sources; do not move geometry."""
import hashlib,importlib.util,json,pathlib,sys,time,zipfile
import numpy as np
from shapely.geometry import Polygon
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];D=R/'docs/astra-city/roof-occlusion-review'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
shared=module('roof_terrain_helpers',H.parent/'landmark-pass/taio_terrain.py')
sys.path.insert(0,str(R/'docs/astra-city/mui-wo-buildings/review'))
from bake_model_geometry import bake
TARGETS=['landsd/186982:0','landsd/226248:0']
def main():
 report=read(D.parent/'landmark-preflight/report.json');parts={p['uid']:p for p in report['parts'] if p['uid'] in TARGETS};terrain=read(R/'3d-viewer/city/data/terrain.json');manifest=read(R/'3d-viewer/city/data/manifest.json');children=[read(R/'3d-viewer'/p['url']) for p in manifest['terrainPatches']];buildings={};rows=[]
 for tile in manifest['tiles']:
  for b in read(R/'3d-viewer'/tile['url'])['buildings']:
   if b['uid'] in TARGETS:buildings[b['uid']]=b
 for uid,p in parts.items():
  candidate=p['candidate'];nativefolder=H.parent/'landmark-acquisition/batches/terrain-prerequisites/staged'/candidate['sourceTile'];nm,ns,tri,valid,usable,tree=shared.shared.terrain_index(nativefolder)
  with zipfile.ZipFile(nativefolder.parents[1]/'sources'/candidate['sourceTile']/(candidate['sourceTile']+'.zip')) as archive:
   for name,digest in ns['sourceHashes'].items():assert hashlib.sha256(archive.read(name)).hexdigest()==digest
  assert sha(nativefolder/ns['url'])==ns['derivedSha256']
  modelmanifest=R/p['acquisitionEvidence']['models'][0]['manifest'];mm=read(modelmanifest);spec=next(m for m in mm['models']if m['id']==candidate['modelId']);assert all(sha(modelmanifest.parent/name)==digest for name,digest in spec['sourceHashes'].items());geometry=bake(spec,modelmanifest.parent);vertices=np.array(geometry['position']).reshape(-1,3);b=buildings[uid];poly=Polygon(b['rings'][0],b['rings'][1:]);roof=candidate['worldBounds'][1][1]
  native,_,_=shared.shared.shared_audit.source_piece_audit(poly,roof,(usable,tree));current=shared.extrema(poly,terrain,children);point=np.array([p['cpu']['terrain']['roof'][::2]]);sample,_=shared.shared.shared_refine.source_samples(point,[{'usable':usable,'tree':tree}]);bottom=vertices[vertices[:,1]<vertices[:,1].min()+.15];heights,_=shared.shared.shared_refine.source_samples(bottom[:,[0,2]],[{'usable':usable,'tree':tree}]);clearance=bottom[:,1]-heights;top=vertices[vertices[:,1]>vertices[:,1].max()-.01];topground,_=shared.shared.shared_refine.source_samples(top[:,[0,2]],[{'usable':usable,'tree':tree}]);topclear=top[:,1]-topground
  row={'uid':uid,'name':p['name'],'sourceTile':candidate['sourceTile'],'modelBounds':candidate['worldBounds'],'dimensionsMetres':np.diff(np.array(candidate['worldBounds']),axis=0)[0].tolist(),'modelTriangles':candidate['triangles'],'modelSourceManifest':str(modelmanifest.relative_to(R)),'modelSourceManifestSha256':sha(modelmanifest),'modelSourceHashes':spec['sourceHashes'],'terrainManifest':str((nativefolder/'manifest.json').relative_to(R)),'terrainManifestSha256':sha(nativefolder/'manifest.json'),'terrainSourceHashes':ns['sourceHashes'],'terrainRevision':nm['tileRevision'],'currentRenderedTerrain':current,'nativeTIN':native,'highestRoofPoint':p['cpu']['terrain']['roof'],'nativeTINAtRoofPoint':float(sample[0]),'nativeRoofPointClearance':float(roof-sample[0]),'currentRoofPointClearance':float(roof-p['cpu']['terrain']['roofGround']),'bottomVertexNativeClearanceRange':[float(np.nanmin(clearance)),float(np.nanmax(clearance))],'highestRoofVertexNativeClearanceRange':[float(np.nanmin(topclear)),float(np.nanmax(topclear))],'sourceFootprintArea':poly.area,'buildingRecord':b,'publicationApproved':False}
  row['decision']='hold-native-terrain-intersection' if native['areaAboveHighestRoofPlusTolerance']>1e-6 else 'candidate-coarse-terrain-correction'
  rows.append(row);print(uid,row['decision'],row['nativeRoofPointClearance'],native,flush=True)
 save(D/'audit.json',{'issue':'HKS-214','snapshotId':report['snapshotId'],'verticalScale':1,'networkDownloads':0,'liveChanges':0,'rows':rows,'rootTerrainSha256':sha(R/'3d-viewer/city/data/terrain.json'),'qualification':'Exact source TIN/footprint audit and native vertices; candidate geometry unchanged. A named source part does not establish complete landmark membership.'})
if __name__=='__main__':main()
