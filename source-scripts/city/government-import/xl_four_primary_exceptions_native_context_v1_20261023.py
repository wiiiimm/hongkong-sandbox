"""Preserve original native cache records and conservative current target candidates."""
from pathlib import Path
import json
import shapely
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-four-primary-exceptions-native-context-v1-20261023';out=base/batch;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        p=base/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    compared='government-xl-remaining-186-exact-primary-targets-v1-20261023';rows=take(compared,'target-comparisons.json.gz')['rows'];exceptions=[r for r in rows if not r['exactTargetMetadataQualified']];assert len(exceptions)==4
    primary=take('government-xl-remaining-186-primary-metadata-v1-20261023','metadata.json.gz');primary={r['sourceKey']:r for r in primary['rows']};inventorybatch='government-xl-after-fu-tor-loy-current-inventory-v1-20261023';inventory=take(inventorybatch,'complete-bounds.json.gz')['rows']
    manifestpath=ROOT/'3d-viewer/city/data/manifest.json';raw=manifestpath.read_bytes();sha=digest(raw);assert sha==exceptions[0]['currentManifestSHA256'];assert sha==pins[inventorybatch][str(manifestpath.relative_to(ROOT))];manifest=json.loads(raw);refs.append(manifestpath);summaries=[];snapshots=[]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for row in exceptions:
            key,modelid=row['sourceKey'].split('/');found=db.execute("SELECT r.result_sha,m.value FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members s USING(cache_key) CROSS JOIN LATERAL jsonb_array_elements(r.result->'models')m WHERE s.run_id=%s AND r.cache_key=%s AND m.value->>'modelId'=%s",(NATIVE_RUN,key,modelid)).fetchall();assert len(found)==1;resultsha,m=found[0];assert m['asset']['sha256']==row['indexedSourceSHA256']and m['modelId']==modelid
            forms=[];current=row['currentTarget'];official=primary[row['sourceKey']]['footprintMatches'];exact=[r for r in official if current and r['BuildingCSUID']==current['buildingCSUID']];link=False
            if len(exact)==1:
                q=exact[0];link=q['Status']=='Active'and all(q[k]==current[v]for k,v in [('BuildingID','buildingId'),('BuildingBlockType','structureType'),('BaseHeight','baseHeightHKPD'),('TopHeight','topHeightHKPD')])
            if row['uid']is None:
                lo,hi=m['worldBounds'];box=shapely.box(lo[0],lo[2],hi[0],hi[2])
                for tile in manifest['tiles']:
                    if not shapely.box(*tile['bounds']).intersects(box):continue
                    path=ROOT/'3d-viewer'/tile['url'];blob=path.read_bytes();assert digest(blob)==pins[compared][str(path.relative_to(ROOT))];refs.append(path)
                    for f in json.loads(blob)['buildings']:
                        poly=shapely.Polygon(f['rings'][0],f['rings'][1:]);area=float(poly.intersection(box).area)
                        if area>0:forms.append(dict(uid=f['uid'],name=f.get('name'),buildingCSUID=f.get('buildingCSUID'),sourceForm=f,tile=str(path.relative_to(ROOT)),tileSHA256=digest(blob),sourceAABBFloorOverlapM2=area,candidateOnly=True))
            installed=[r['uid']for r in inventory if r['sourceSHA256']==m['asset']['sha256']]
            record=dict(sourceKey=row['sourceKey'],uid=row['uid'],nativeCacheKey=key,nativeResultSHA256=resultsha,nativeModel=m,originalIndexedSHA256=row['indexedSourceSHA256'],exactActiveCSUIDRecordWithCurrentFields=link,cachedOfficialRecords=official,originalTargetMetadataComparison=row,currentAABBCandidates=sorted(forms,key=lambda r:r['sourceAABBFloorOverlapM2'],reverse=True),existingExactAssetSHAInstallations=installed,sourceBytesOrGraphRechecked=False,sourceIdentityAccepted=False,physicalAccepted=False,installationApproved=False,permanentRejection=False)
            save(out/(modelid+'.json.gz'),record);snapshots.append(dict(cacheKey=key,resultSHA256=resultsha,modelId=modelid));summaries.append(dict(uid=row['uid'],sourceKey=row['sourceKey'],nativeState=m['state'],triangles=m['triangles'],exactActiveCSUIDRecordWithCurrentFields=link,currentAABBCandidates=len(forms),candidateUids=[r['uid']for r in record['currentAABBCandidates']],existingExactAssetSHAInstallations=installed));print(summaries[-1],flush=True)
    assert digest(manifestpath.read_bytes())==sha
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        for r in snapshots:assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['cacheKey'],)).fetchone()==(r['resultSHA256'],)
    result=dict(uids=sorted(r['uid']for r in exceptions if r['uid']is not None),sourceKeys=[r['sourceKey']for r in exceptions],rows=summaries,nativeRun=NATIVE_RUN,cacheSnapshots=snapshots,currentManifestSHA256=sha,sourceGeometryChanges=0,sourceIdentityAccepted=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,permanentRejection=False,qualification='Two mapped sources have exact Active CSUID/current-field links despite a3DModelID/2Dstructure classification difference. Two unmapped source keys retain packed native assets and have no cached explicit viewer/official matches; current AABB candidates are lookup evidence only, never identity, source footprint, legal relationship, support, coverage tolerance or installation approval. No asset downloaded, geometry edited, queue created or installed credit given. Exact byte-installation lookup uses the authenticated current full native inventory; an absent match is not proof the source cannot be installed.')
    save(out/'summary.json',result);module('four_exception_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-four-primary-exceptions-native-and-current-target-context',refs,result)

if __name__=='__main__':main()
