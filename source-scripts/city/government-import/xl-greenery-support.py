"""Recover Greenery Garden Block C from the pinned government directory; never AI."""
import json,sys,zipfile
from pathlib import Path
from shapely.geometry import MultiPoint,Polygon
sys.path.insert(0,str(Path(__file__).resolve().parent));from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'citywide-native'));from download import acquire
from convert import _convert_one
SHEET='11-SW-11B';UID='landsd/233384:0';MODEL='B312541513002063C0'
DOC=ROOT/'docs/astra-city/government-import/government-xl-50-20260913/second-pass/third-pass/greenery-garden';LOCAL=HERE/'local/government-xl-50-second-20260913/third-pass-greenery-support';SOURCE=HERE/'local/government-xl-50-second-20260913/sheets'/SHEET
def main():
 directory=read(SOURCE/'directory/result.json');assert directory['directorySHA256']=='56a09a64cb6b27b1c05cb0b3dd32f5651916adbda2b886c1670f8182d039c584';by_model={row['modelId']:row for row in directory['models']};directory['models']=[by_model[MODEL]];out=LOCAL/'source';acquired=acquire(directory,SOURCE/'directory/zip-directory.bin',out/'original');(out/'packed').mkdir(parents=True,exist_ok=True)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');found=[]
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];raw=path.read_bytes()
  for building in json.loads(raw)['buildings']:
   if building['uid']==UID:found.append((building,tile['url'],digest(raw)))
 assert len(found)==1;building,tile,tile_hash=found[0]
 with zipfile.ZipFile(out/'original'/(SHEET+'.zip')) as archive:
  converted=_convert_one(archive,archive.getinfo('BUILDING/'+MODEL+'/'+MODEL+'.gltf'),out/'decoded',out/'packed',{}, {'modelId':MODEL})
 footprint=Polygon(building['rings'][0],building['rings'][1:]);hull=MultiPoint([[x,z] for x,_,z in converted['terrainSamples']['position']]).convex_hull;intersection=hull.intersection(footprint).area
 entry={**converted['asset'],'uid':UID,'modelId':MODEL,'objectId':building['objectId'],'buildingCSUID':building['buildingCSUID'],'label':building['name'],'recordedBaseHeight':building['baseHeightHKPD'],'recordedTopHeight':building['topHeightHKPD'],'worldBounds':converted['worldBounds'],'triangles':converted['triangles'],'footprintCentroidDistanceMetres':hull.centroid.distance(footprint.centroid),'overlapOfSmallerFootprint':intersection/min(hull.area,footprint.area),'placementReviewed':False,'priority':'unreviewed','publicationApproved':False,'rootTranslation':[-834500,0,816500],'sourceTile':SHEET}
 asset=out/'packed'/entry['asset'];assert digest(asset.read_bytes())==entry['sha256'];row={'uid':UID,'source':{'building':building,'tile':tile,'tileSHA256':tile_hash},'candidate':{'path':str(asset),'entry':entry},'native':{'sheet':SHEET,'model':converted,'directPinnedRecovery':True}}
 save(LOCAL/'support-runtime.json.gz',{'rows':[row],'aiCalls':0,'modelGeometryChanges':0});save(DOC/'support-source-recovery.json',{'sheet':SHEET,'directorySHA256':directory['directorySHA256'],'sourceETag':directory['etag'],'models':[{'uid':UID,'modelId':MODEL,'sourceSHA256':entry['sha256'],'triangles':entry['triangles'],'overlapOfSmallerFootprint':entry['overlapOfSmallerFootprint'],'centroidDistanceMetres':entry['footprintCentroidDistanceMetres'],'worldBounds':entry['worldBounds']}],'acquisition':{k:v for k,v in acquired.items() if k!='source'},'aiCalls':0,'modelGeometryChanges':0,'publication':False});print(json.dumps({'uid':UID,'triangles':entry['triangles'],'bounds':entry['worldBounds'],'overlap':entry['overlapOfSmallerFootprint'],'aiCalls':0}))
if __name__=='__main__':main()
