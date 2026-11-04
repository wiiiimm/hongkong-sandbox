"""Acquire five exact untouched upper government sources; never publish."""
import importlib.util,uuid,zipfile,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
BATCH='government-xl-miami-five-upper-original-acquisition-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
DISCOVERY=ROOT/'docs/astra-city/government-import/government-xl-miami-intersecting-upper-source-discovery-20261009'
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not (DOC/'result.json').exists(),'Completed checkpoint immutable'
 discovered=read(DISCOVERY/'complete-upper-source-discovery.json.gz')['rows'];claim=reservations.claim('miami-upper-originals-'+str(uuid.uuid4()),['building:'+r['uid'] for r in discovered],batch=BATCH,ttl=3600);assert claim['ok'],claim;lease=claim['reservation'];rows=[];containers=[]
 try:
  helper=module('miami_upper_original_acquire','xl-next-support-recovery-20261005.py');by_sheet={}
  for r in discovered:
   found=[m for m in r['cachedExactGeoRefSources'] if m['sameExactSourceIdentity']];assert len(found)==1;native={k:found[0][k] for k in ['cacheKey','resultSha','sheet','model']};by_sheet.setdefault(native['sheet'],[]).append((r,native))
  for sheet,group in by_sheet.items():
   with connect() as c:
    c.execute('SET TRANSACTION READ ONLY');pinned=c.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
   folder=LOCAL/'sheets'/sheet;directory,_=helper.scan({'SHEETNO':sheet,'Format_glTF':pinned['sourceURL'],'REVISIONDATE':pinned['revision']},folder/'directory',refresh=True);wanted={n['model']['modelId'] for _,n in group};directory['models']=[m for m in directory['models'] if m['modelId'] in wanted];assert {m['modelId'] for m in directory['models']}==wanted;receipt=helper.acquire(directory,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir(exist_ok=True);containers.append({'sheet':sheet,'freshContainer':{k:v for k,v in directory.items() if k!='models'},'acquisition':receipt})
   with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as archive:
    for discovery,native in group:
     model=native['model'];entry,basis=helper.diagnostic_entry(native,discovery['currentForm']);converted=helper._convert_one(archive,archive.getinfo(model['sourceEntry']),folder/'decoded',packed,{}, {'modelId':model['modelId']});raw=helper.canonical_bytes((packed/converted['asset']['asset']).read_bytes(),model['asset']['sha256']);assert digest(raw)==model['asset']['sha256'];path=LOCAL/'assets'/(digest(raw)+'.glb.gz');path.parent.mkdir(exist_ok=True);path.write_bytes(raw);b=discovery['currentForm'];tile='city/data/tiles/'+b['tile']+'.json';row={'uid':b['uid'],'source':{'building':b,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())},'native':native,'modelId':model['modelId'],'sourceSHA256':digest(raw),'candidate':{'entry':entry,'path':str(path.relative_to(ROOT))},'triangles':model['triangles'],'sourceLookupBasis':basis};rows.append(row);print({'uid':b['uid'],'modelId':model['modelId'],'sourceSHA256':digest(raw),'originalFaces':model['triangles']},flush=True);assert reservations.heartbeat(lease)['ok']
  save(DOC/'five-exact-upper-original-selection.json.gz',{'rows':rows,'freshContainers':containers,'geometryChanges':0,'installationApproved':False});freezer=module('miami_upper_original_fence','xl-popcorn-source-investigations-checkpoints-20261009.py');freezer.freeze(BATCH,'five-exact-upper-original-source-acquisition-v1',[Path(__file__),DISCOVERY/'result.json',DISCOVERY/'complete-upper-source-discovery.json.gz']+[ROOT/r['candidate']['path'] for r in rows],{'uids':[r['uid'] for r in rows],'originalSources':len(rows),'originalTriangles':sum(r['triangles'] for r in rows),'requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'identityAccepted':False,'physicalAccepted':False,'remainingReason':'complete-original-upper-family-identity-and-support-checks-pending','nextStep':'Decode all original roots/attributes/poses and independently check the current complete source family, actual podium support, foreign interfaces, foundations and runtime; no modelling or installation credit from acquisition.'})
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
