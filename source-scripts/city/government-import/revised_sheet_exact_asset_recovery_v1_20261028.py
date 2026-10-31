"""Fresh archive acquisition, usable only when exact indexed model bytes survive.

Preserve old revision rejection; no old archive/identity approval is transferred.
The existing acquisition guard is untouched. Changed model bytes stay unresolved.
"""
import argparse,json,shutil,sys,uuid,zipfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
import shape_prepare
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-revised-sheet-two-exact-assets-recovery-v1-20261028';PRIOR='government-xl-nine-missing-originals-grouped-recovery-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UIDS={'landsd/203428:0','landsd/203844:0'}
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and{'building:'+u for u in UIDS}<=set(lease['resources']);assert not DOC.exists()and shutil.disk_usage(ROOT).free>=3*1024**3;prior,pins=authenticate(BASE/PRIOR);assert set(prior['errors'])==UIDS and all('Source revision changed'in s for s in prior['errors'].values());oldlocal=HERE/'local'/PRIOR
 def pinned(path):assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];return read(path)
 inp=oldlocal/'recovery-inputs.json.gz';meta=oldlocal/'recovered/source-metadata.json';inputs=pinned(inp);metadata=pinned(meta);native=[n for n in inputs['native']if n['model']['candidate']['uid']in UIDS];assert len(native)==2 and len({n['sheet']for n in native})==1;sheet=native[0]['sheet'];old=metadata['directories'][sheet];folder=LOCAL/'fresh-sheet';refs=[Path(__file__),BASE/PRIOR/'result.json',inp,meta,Path(shape_prepare.__file__)];recovered=[];errors={}
 # This scanner creates NEW provenance, never overwrites the pinned old record.
 directory,_=shape_prepare.scan({'SHEETNO':sheet,'Format_glTF':old['sourceURL'],'REVISIONDATE':old['revision']},folder/'directory');assert directory['etag']!=old['etag']or directory['directorySHA256']!=old['directorySHA256'];wanted={n['model']['modelId']for n in native};directory['models']=[m for m in directory['models']if m['modelId']in wanted];assert {m['modelId']for m in directory['models']}==wanted
 acquired=shape_prepare.acquire(directory,folder/'directory/zip-directory.bin',folder/'original');packed=folder/'packed';packed.mkdir(parents=True,exist_ok=True);archive=folder/'original'/(sheet+'.zip')
 with zipfile.ZipFile(archive)as z:
  for n in native:
   m=n['model'];entry=m['candidate'];uid=entry['uid'];assert m['asset']['sha256']==entry['sha256'];assert sum(i.filename==m['sourceEntry']for i in z.infolist())==1
   try:
    result=shape_prepare._convert_one(z,z.getinfo(m['sourceEntry']),folder/'decoded',packed,{},dict(modelId=m['modelId']));actual=packed/result['asset']['asset'];raw=shape_prepare.canonical_bytes(actual.read_bytes(),entry['sha256']);assert len(raw)==entry['bytes'];dest=LOCAL/'assets'/(entry['sha256']+'.glb.gz');dest.parent.mkdir(exist_ok=True);dest.write_bytes(raw);assert digest(dest.read_bytes())==entry['sha256'];refs.append(dest)
    identity=dict(sheet=sheet,sourceURL=old['sourceURL'],archiveETag=directory['etag'],directorySHA256=directory['directorySHA256'],modelId=m['modelId'],sourceEntry=m['sourceEntry'],assetSHA256=entry['sha256']);recovered.append(dict(uid=uid,originalIndexedSourceKey=n['cacheKey']+'/'+m['modelId'],sourceSHA256=entry['sha256'],sourceAsset=dict(path=str(dest.relative_to(ROOT)),sha256=entry['sha256']),newAcquisitionIdentitySHA256=digest(json.dumps(identity,sort_keys=True,separators=(',',':')).encode()),newAcquisitionProvenance=identity,exactIndexedAssetBytesUnchanged=True,freshIdentityAndPlacementAcceptanceRequired=True,installationApproved=False))
   except Exception as error:errors[uid]=type(error).__name__+': '+str(error)[:180]
 # Preserve new source metadata and acquisition facts independently of old input.
 provenance=dict(sheet=sheet,oldArchiveETag=old['etag'],oldDirectorySHA256=old['directorySHA256'],newArchiveETag=directory['etag'],newDirectorySHA256=directory['directorySHA256'],sourceURL=old['sourceURL'],download=acquired,oldRevisionGuardFailurePreserved=True,oldArchiveAcceptedAsCurrent=False)
 save(DOC/'fresh-archive-provenance.json',provenance)
 for name in ['directory','decoded','packed']:
  refs.extend(p for p in(folder/name).rglob('*')if p.is_file())
 result=dict(uids=sorted(UIDS),recovered=recovered,recoveredCount=len(recovered),errors=errors,oldRevisionGuardFailurePreserved=True,oldArchiveAcceptedAsCurrent=False,newArchiveProvenanceRecorded=True,freshIdentityAndPlacementAcceptanceRequired=True,sourceGeometryChanges=0,sourcePoseChanges=0,qualification='Separate fresh-source acquisition, not a relaxation of the old archive guard. A model is recovered only if canonical GLB/gzip bytes and size equal the immutable indexed original exactly. Fresh archive provenance has its own identity; no old source/placement/optimisation approval transfers. Different model bytes remain an explicit failure; no remodelling, reindex, source overwrite or publication.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('revised_sheet_exact_asset_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-archive-exact-indexed-asset-recovery-no-approval-transfer',refs,result);print(dict(recovered=len(recovered),errors=errors),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('fresh-archive-exact-asset-'+str(uuid.uuid4()),['building:'+u for u in sorted(UIDS)],batch=BATCH,ttl=1800);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
