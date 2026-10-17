"""Search all unchanged government building members on both intersecting sheets for support."""
from pathlib import Path
import zipfile,uuid
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-hkust-complete-two-sheet-support-scan-v1-20261015';DOC=B/NAME;LOCAL=HERE/'local'/NAME
CACHES=[HERE/'local/government-xl-eight-further-original-closures-20261008/sheets/12-NW-6A/directory',HERE/'local/government-xl-hkust-adjoining-native-terrain-v1-20261015/12-NW-6C/directory']
def main():
 assert not DOC.exists();prior=B/'government-xl-hkust-unresolved-rim-source-context-v1-20261015';ip=prior/'source-incidence.json.gz';pins={x['path']:x['sha256'] for x in read(prior/'result.json')['evidenceRefs']};assert digest(ip.read_bytes())==pins[str(ip.relative_to(ROOT))]
 samples=[r['sample'] for r in read(ip)['rows']];points=np.array([s['position'] for s in samples]);assert len(samples)==52
 lease=reservations.claim('hkust-source-scan-'+str(uuid.uuid4()),['source-acquisition:'+NAME],batch=NAME,ttl=3600);assert lease['ok'];lease=lease['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True);f=module('hkust_support_scan_decoder',HERE/'xl-final-script-pass.py');f.s.LOCAL=LOCAL;paths=[Path(__file__),ip,prior/'result.json',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py'];rows=[]
  for cache in CACHES:
   directory=read(cache/'result.json');assert digest((cache/'zip-directory.bin').read_bytes())==directory['directorySHA256'];sheet=directory['sheet'];folder=LOCAL/sheet
   acquisition=f.s.acquire(directory,cache/'zip-directory.bin',folder/'original');save(DOC/(sheet+'-acquisition.json'),acquisition);paths.extend([cache/'result.json',cache/'zip-directory.bin',folder/'original/download.json'])
   with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as z:
    for name in z.namelist():
     if name.endswith(('.gltf','.bin')):
      p=folder/'members'/f.s.safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name));paths.append(p)
   for model in directory['models']:
    mid=model['modelId'];gp=next(folder/'members'/m['name'] for m in model['members'] if m['name'].endswith('.gltf'));row={'sheet':sheet,'modelId':mid,'geoRefNo':model['geoRefNo'],'sourceFiles':[{'path':str((folder/'members'/m['name']).relative_to(ROOT)),'sha256':digest((folder/'members'/m['name']).read_bytes())} for m in model['members']]}
    try:
     tri=f.s.terrain_triangles(gp);assert np.isfinite(tri).all();row['triangles']=len(tri);row['bounds']=[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()];polys=shapely.polygons(tri[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;heights=f.s.context.shared.samples(points[:,[0,2]],tri[valid],shapely.STRtree(polys[valid])) if valid.any() else np.full(len(points),np.nan)
     row['sampleSupport']=[{'sampleIndex':i,'height':float(h),'gap':float(points[i,1]-h),'strictPointContact':bool(abs(points[i,1]-h)<=.1)} for i,h in enumerate(heights) if np.isfinite(h)];row['state']='complete-original-scan'
    except Exception as e:row.update(state='decode-error',error=type(e).__name__+': '+str(e))
    rows.append(row);assert reservations.heartbeat(lease,ttl=3600)['ok'];print(sheet,mid,row['state'],len(row.get('sampleSupport',[])),flush=True)
  paths.extend(p for p in (LOCAL/'terrain-repairs').rglob('*') if p.is_file());existing={'B453782220901063C0','B453692221102063C0'};extra=[r for r in rows if r['modelId'] not in existing and r.get('sampleSupport')]
  summary={'uids':['landsd/309822:0','landsd/232155:0'],'modelsScanned':len(rows),'decodeErrors':[r['modelId'] for r in rows if r['state']=='decode-error'],'additionalModelsOverFailingPoints':[{'modelId':r['modelId'],'sampleCount':len(r['sampleSupport']),'strictContacts':sum(x['strictPointContact'] for x in r['sampleSupport'])} for r in extra],'sourceBuildingGeometryChanged':False,'supportAccepted':False,'installationApproved':False}
  save(DOC/'scan.json.gz',{'rows':rows,'samples':samples,'qualification':'Complete model inventory on two terrain-intersecting sheets, no claim of territory-wide source completeness or installation acceptance.'});save(DOC/'summary.json',summary)
  module('hkust_all_sheet_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(NAME,'hkust-complete-two-sheet-original-support-search-v1',paths,{**summary,'nextStep':'Use any newly located original support; otherwise preserve demonstrated two-sheet negative and investigate exact original frontage/source mismatch. No arbitrary terrain fill or model editing.'});print(summary,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
