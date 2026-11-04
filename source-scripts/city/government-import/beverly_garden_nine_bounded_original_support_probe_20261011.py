"""Distinct source-only Beverly9/80888 whole-finite interface and topology probe.
No terrain point/root recomputation, geometry edit or physical acceptance.
"""
from pathlib import Path
import sys,json,zipfile,hashlib,gzip
import numpy as np
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
sys.path.insert(0,str(BASE));from run import connect,read,save,digest,reservations
sys.path.insert(0,str(BASE.parent/'enhancement-screening'))
from shape_prepare import scan,acquire,_convert_one,canonical_bytes
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BATCH='government-xl-beverly-garden-nine-bounded-source-path-review-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=BASE/'local'/BATCH
UID='landsd/80888:0';MID='B450861908201063C0';EXPECTED='ae4dc9704760532250b955377524e8c3b482faf39bf35760c6c3c97040d44ccf'

def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 claim=reservations.claim('codex-beverly-nine-source-only-80888-20261011',['building:'+UID],ttl=1800,batch=BATCH)
 assert claim['ok'],'Source-only80888 reservation conflict'
 receipt=claim['reservation'];LOCAL.mkdir(parents=True,exist_ok=True)
 try:
  selection=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-beverly-garden-nine-retained-current-physical-v3-20261010/selection.json.gz';primary=read(selection)['rows'][0]
  with connect() as con:
   con.execute('SET TRANSACTION READ ONLY');nativeSHA,native=con.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(primary['native']['cacheKey'],)).fetchone();prior=con.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet='12-NW-21A' ORDER BY created_at DESC LIMIT 1").fetchone()[0]
  assert nativeSHA==primary['native']['resultSha'];m=next(q for q in native['models']if q['modelId']==MID);assert m['asset']['sha256']==EXPECTED
  folder=LOCAL/'sheets/12-NW-21A';current,_=scan({'SHEETNO':'12-NW-21A','Format_glTF':prior['sourceURL'],'REVISIONDATE':prior['revision']},folder/'directory')
  current['models']=[q for q in current['models']if q['modelId']==MID];assert len(current['models'])==1
  assert reservations.owns(receipt);proof=acquire(current,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir(exist_ok=True)
  with zipfile.ZipFile(folder/'original/12-NW-21A.zip')as z:converted=_convert_one(z,z.getinfo(m['sourceEntry']),folder/'decoded',packed,{}, {'modelId':MID})
  raw=canonical_bytes((packed/converted['asset']['asset']).read_bytes(),EXPECTED);assert len(raw)==m['asset']['bytes'];asset=LOCAL/'assets'/(EXPECTED+'.glb.gz');asset.parent.mkdir(exist_ok=True);asset.write_bytes(raw)
  source=ROOT/primary['candidate']['path'];raw=source.read_bytes();assert digest(raw)==primary['sourceSHA256'];a=decode_original_world_triangles(raw);b=decode_original_world_triangles(asset.read_bytes())
  topo=census(a,list(range(len(a))));components=[{'component':i,'completeOriginalFaces':g,'bounds':[a[g].min((0,1)).tolist(),a[g].max((0,1)).tolist()]}for i,g in enumerate(topo['sharedEdgeConnectedComponents'])]
  contact=exact_finite_contacts(a,list(range(len(a))),b,list(range(len(b))),maximum_pairs=200000)
  result={'batch':BATCH,'sourceUID':primary['uid'],'sourceSHA256':primary['sourceSHA256'],'supportUID':UID,'supportSHA256':EXPECTED,'sourceFaces':len(a),'supportFaces':len(b),'sourceCensus':topo,'sourceComponents':components,'completeFiniteSourceSupportContact':contact,'recovery':{'originalNativeResultSHA256':nativeSHA,'sourceDirectorySHA256':current['directorySHA256'],'previousDirectorySHA256':prior['directorySHA256'],'directoryUnchanged':current['directorySHA256']==prior['directorySHA256'],'originalSourceSHA256Unchanged':True,'receivedBytes':proof['newThisInvocationBytes']},'evidenceRefs':[ref(selection),ref(source),ref(asset),ref(Path(__file__))],'sourceOnly':True,'physicalSupportAccepted':False,'publication':False,'sourceGeometryChanges':0,'newlyInstalled':0,'qualification':'Complete exact original finite-face contact checks against previously omitted original80888. Topology retains open/nonmanifold/nonrendering evidence; no invented support, terrain root, F32 or installation approval.'}
  save(DOC/'original-support-contact-diagnostic.json.gz',result)
  print(json.dumps({'sourceComponents':len(components),'contacts':len(contact['contacts']),'trianglePairsTested':contact['trianglePairsTested'],'positiveDimensionContacts':sum(q['dimension']>0 for q in contact['contacts']),'directoryUnchanged':result['recovery']['directoryUnchanged'],'sourceOnly':True}))
 finally:reservations.release(receipt)
if __name__=='__main__':main()
