"""Restore exact original terrain members from existing local ZIPs; no downloads."""
import argparse,hashlib,subprocess,zipfile
from pathlib import Path,PurePosixPath
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module

def file_sha(path):
    h=hashlib.sha256()
    with path.open('rb')as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    for key in ['batch','capture','uid']:p.add_argument('--'+key,required=True)
    a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
    base=ROOT/'docs/astra-city/government-import';doc=base/a.batch;local=HERE/'local'/a.batch;assert not doc.exists()and not local.exists();_,pins=authenticate(base/a.capture)
    selected=base/a.capture/'selection.json.gz';assert digest(selected.read_bytes())==pins[str(selected.relative_to(ROOT))];row=next(r for r in read(selected)['rows']if r['uid']==a.uid)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(row['native']['cacheKey'],)).fetchone()
    assert sha==row['native']['resultSha'];sheet=row['candidate']['entry']['sourceTile'];records=native.get('terrain',[]);assert records and all(t.get('sourceHashes')and t.get('sourceEntry')for t in records)
    archives=[ROOT/name for name in subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g',sheet+'.zip','source-scripts/city'],cwd=ROOT,text=True).splitlines()];found=[];refs=[Path(__file__),selected,base/a.capture/'result.json']
    for terrain in records:
        expected=terrain['sourceHashes'];assert terrain['sourceEntry']in expected
        for entry in expected:
            part=PurePosixPath(entry);assert not part.is_absolute()and '..'not in part.parts and part.parts[0].startswith('TERRAIN')
        matched=None
        for archive in archives:
            try:
                with zipfile.ZipFile(archive)as z:
                    if not set(expected)<=set(z.namelist()):continue
                    raw={entry:z.read(entry)for entry in expected}
                    if any(digest(raw[entry])!=h for entry,h in expected.items()):continue
                    members=[dict(sourceEntry=entry,bytes=len(raw[entry]),sha256=expected[entry],crc32=z.getinfo(entry).CRC)for entry in expected]
                    matched=(archive,raw,members);break
            except zipfile.BadZipFile:continue
        if matched is None:found.append(dict(sourceEntry=terrain['sourceEntry'],state='exact-cached-members-unavailable'));continue
        archive,raw,members=matched
        for entry,data in raw.items():
            target=local/'decoded'/entry;target.parent.mkdir(parents=True,exist_ok=True);assert not target.exists();target.write_bytes(data);assert digest(target.read_bytes())==expected[entry];refs.append(target)
        found.append(dict(sourceEntry=terrain['sourceEntry'],state='exact-original-restored',sourceTerrainPath=str((local/'decoded'/terrain['sourceEntry']).relative_to(ROOT)),archivePath=str(archive.relative_to(ROOT)),archiveSHA256=file_sha(archive),members=members))
    result=dict(uids=[a.uid],sourceSHA256=row['sourceSHA256'],nativeCacheKey=row['native']['cacheKey'],nativeResultSHA256=sha,rows=found,allExactOriginalTerrainRestored=all(r['state']=='exact-original-restored'for r in found),sourceGeometryChanges=0,downloads=0,installationApproved=False,qualification='ZIP CRC validation plus exact pinned native-stage SHA256 for every restored original GLTF/buffer member. Existing archives remain untouched; restored bytes are new immutable private cache files. No model/terrain transformation, network acquisition, acceptance or publication.')
    save(doc/'summary.json',result);module('cached_zip_terrain_restore_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-native-original-terrain-members-local-zip-restoration',refs,result);print(dict(uid=a.uid,allRestored=result['allExactOriginalTerrainRestored'],terrainRecords=len(found)),flush=True)

if __name__=='__main__':main()
