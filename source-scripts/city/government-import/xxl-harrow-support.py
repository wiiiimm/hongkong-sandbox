"""Recover Harrow's adjacent podium from the pinned government directory; never AI."""
import json,sys,zipfile
from pathlib import Path
from shapely.geometry import Polygon,MultiPoint
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run import ROOT,HERE,read,save,digest
sys.path.insert(0,str(HERE.parent/'citywide-native'));from download import acquire;from convert import _convert_one
DOC=ROOT/'docs/astra-city/government-import/government-xxl-20260911/second-pass/fourth-pass/harrow';LOCAL=HERE/'local/government-xxl-second-20260911/fourth-pass-harrow';UID='landsd/193532:0';MODEL='B171532634202062G0';SHEET='6-SW-17A'

def main():
 source=HERE/'local/government-xxl-second-20260911/sheets'/SHEET;directory=read(source/'directory/result.json');assert directory['directorySHA256']=='480d8596917d2759c1a474896cf85bc4e9c7d46b5aebbce069c2ad2dfd2040d0';directory['models']=[m for m in directory['models'] if m['modelId']==MODEL];assert len(directory['models'])==1
 out=LOCAL/'support-download';acquired=acquire(directory,source/'directory/zip-directory.bin',out/'original')
 (out/'packed').mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out/'original'/(SHEET+'.zip')) as z:
  row={'modelId':MODEL};converted=_convert_one(z,z.getinfo('BUILDING/'+MODEL+'/'+MODEL+'.gltf'),out/'decoded',out/'packed',{},row)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');tile=next(t['url'] for t in manifest['tiles'] if any(b['uid']==UID for b in read(ROOT/'3d-viewer'/t['url'])['buildings']));tile_raw=(ROOT/'3d-viewer'/tile).read_bytes();building=next(b for b in json.loads(tile_raw)['buildings'] if b['uid']==UID);foot=Polygon(building['rings'][0],building['rings'][1:]);hull=MultiPoint([[x,z] for x,_,z in row['terrainSamples']['position']]).convex_hull;intersection=hull.intersection(foot).area
 entry={**row['asset'],'uid':UID,'modelId':MODEL,'objectId':building['objectId'],'buildingCSUID':building['buildingCSUID'],'label':building['name'],'recordedBaseHeight':building['baseHeightHKPD'],'recordedTopHeight':building['topHeightHKPD'],'worldBounds':row['worldBounds'],'triangles':row['triangles'],'footprintCentroidDistanceMetres':hull.centroid.distance(foot.centroid),'overlapOfSmallerFootprint':intersection/min(hull.area,foot.area),'placementReviewed':False,'priority':'unreviewed','publicationApproved':False,'rootTranslation':[-834500,0,816500],'sourceTile':SHEET};asset=out/'packed'/entry['asset'];assert digest(asset.read_bytes())==entry['sha256']
 runtime={'uid':UID,'source':{'building':building,'tile':tile,'tileSHA256':digest(tile_raw)},'candidate':{'path':str(asset),'entry':entry},'native':{'sheet':SHEET,'model':row,'directPinnedRecovery':True}};save(LOCAL/'support-runtime.json',runtime);save(DOC/'support-source-recovery.json',{'uid':UID,'modelId':MODEL,'sheet':SHEET,'sourceSHA256':entry['sha256'],'bytes':entry['bytes'],'directorySHA256':directory['directorySHA256'],'sourceETag':directory['etag'],'acquisition':{k:v for k,v in acquired.items() if k!='source'},'overlapOfSmallerFootprint':entry['overlapOfSmallerFootprint'],'centroidDistanceMetres':entry['footprintCentroidDistanceMetres'],'aiCalls':0,'geometryChanges':0,'publication':False});print(json.dumps(read(DOC/'support-source-recovery.json')))
if __name__=='__main__':main()
