"""ROOT-only exact two-member terrain acquisition; no geometry decoding or publication."""
from pathlib import Path
import copy, gzip, hashlib, importlib.util, json, subprocess, sys, uuid, zipfile, zlib
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from timed_owned_lease_pulse_v1_20261014 import TimedOwnedLeasePulse
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
BASE=ROOT/'docs/astra-city/government-import'; UID='landsd/165054:0'
BATCH='government-xl-heritage165054-authentic-terrain-acquisition-v1-20261014'
DOC=BASE/BATCH; PROPOSAL=BASE/(BATCH+'-proposal'); LOCAL=HERE/'local'/BATCH; LEASE=LOCAL/'reservation.json'
CURRENT='12971667a74b07de90ce5ee29999f44a6bf297de84ec7916a629bc42725cd82c'; SNAPSHOT='be5f7671a989392d'
ORDINARY=BASE/'government-xl-heritage165054-current-ordinary-physical-v1-20261014'
JOB='09423e020fcce2205b300ecf4ecc60ca69f5ca23274bad3957490738d4d7cd1f'
DIRECTORY=HERE/'local/government-xl-held-current-directory-audit-20261007/sheets/7-SW-15D/directory'
OLD_DOWNLOAD=HERE/'local/government-xl-remaining-held-20260923/recovered/sheets/7-SW-15D/original/download.json'
DOWNLOADER=HERE.parent/'citywide-native/download.py'; PARSER=HERE.parent/'landmark-acquisition/acquire.py'
FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
MEMBERS=[dict(name='TERRAIN(TB)/T36750264000106E10/T36750264000106E10.bin',crc32=1845630318,compressedBytes=2868322,decodedBytes=10950960,headerOffset=2137846),dict(name='TERRAIN(TB)/T36750264000106E10/T36750264000106E10.gltf',crc32=212232407,compressedBytes=1308,decodedBytes=6334,headerOffset=46725480)]
PIN=dict(sheet='7-SW-15D',sourceURL='https://download.map.gov.hk/api/3d-zip/GLTF0/7-SW-15D.zip?key=ad5940a63bd344c48b0351ef1c7a905e',revision=1759075200000,etag='"2ca3455-63dd138119516"',archiveBytes=46806101,directorySHA256='a7044ac28237e106f7d6deaeab2aeebe2a11d34ca3f05e902c195bec58511be7',completeEntries=699,centralDirectoryBytes=79179,centralDirectoryOffset=46726900)
def read(p): return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def ref(p): return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(q):
    p=(ROOT/q['path']).resolve(); assert p.is_relative_to(ROOT) and ref(p)==q; return p

def save(p,o):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f: f.write(json.dumps(o,sort_keys=True,separators=(',',':'),allow_nan=False).encode()+b'\n')
def module(p,name):
    s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def terrain_selection(row,infos,parsed):
    assert {k:row[k] for k in PIN}==PIN and row['status']=='directory-verified'
    assert {k:parsed[k] for k in ['completeEntries','centralDirectoryBytes','centralDirectoryOffset','directorySHA256']}=={k:PIN[k] for k in ['completeEntries','centralDirectoryBytes','centralDirectoryOffset','directorySHA256']}
    actual=[dict(name=e.filename,crc32=e.CRC,compressedBytes=e.compress_size,decodedBytes=e.file_size,headerOffset=e.header_offset) for e in infos if e.filename.startswith('TERRAIN') and e.filename.endswith(('.gltf','.bin'))]
    assert sorted(actual,key=lambda r:r['name'])==MEMBERS
    target=copy.deepcopy(row); target['models']=[]
    return target

def inputs():
    row=read(DIRECTORY/'result.json'); infos,parsed=module(PARSER,'heritage_acquire_parser').parse_directory((DIRECTORY/'zip-directory.bin').read_bytes()); target=terrain_selection(row,infos,parsed)
    old=read(OLD_DOWNLOAD); assert old['terrainGeometryIncluded'] is False and not any(e['name'].startswith('TERRAIN') for e in old['entries'])
    r=read(ORDINARY/'result.json'); v=read(ORDINARY/'ROOT-VERIFIED.json'); d=read(ORDINARY/'diagnostic.json.gz')
    assert r['jobId']==v['jobId']==JOB and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased']
    assert d['uid']==UID and d['ordinaryNumericReasons']==['terrain-intersects-source-over-0.5m'] and d['completeOriginalFaces']==15140 and d['completeActualDrawnGroundFaces']==24
    assert d['currentManifestSHA256']==CURRENT and d['currentSnapshot']==SNAPSHOT and not d['strictFoundationAccepted'] and not d['physicalAccepted']
    manifest=ROOT/'3d-viewer/city/data/manifest.json'; assert ref(manifest)['sha256']==CURRENT
    pointer=ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'; assert read(pointer)['snapshotId']==SNAPSHOT
    rows=read(ORDINARY/'neighbour-inputs.json.gz')['rows']; scope=sorted(x['building']['uid'] for x in rows); assert len(scope)==len(set(scope))==10 and UID in scope and 'landsd/57455:0' in scope
    refs=distinct_refs(r['evidenceRefs']+[ref(p) for p in [ORDINARY/'result.json',ORDINARY/'ROOT-VERIFIED.json',DIRECTORY/'result.json',DIRECTORY/'zip-directory.bin',DIRECTORY/'transfer.json',OLD_DOWNLOAD,OLD_DOWNLOAD.parent/'7-SW-15D.zip',manifest,pointer]])
    for q in refs: check(q)
    return target,scope,refs

def load():
    pins=read(PROPOSAL/'draft-pins.json'); assert pins['caller']==ref(Path(__file__))
    for q in pins['codeRefs']+pins['inputRefs']: check(q)
    data=inputs(); assert data[2]==pins['inputRefs']; return pins,data

def verify_record(record,archive):
    assert record['sheet']==PIN['sheet'] and record['source']==PIN['sourceURL'] and record['sourceETag']==PIN['etag'] and record['directorySHA256']==PIN['directorySHA256']
    assert record['expectedModels']==0 and record['terrainGeometryIncluded'] is True and record['terrainPhotographsOmitted'] is True
    assert record['sourceArchiveBytes']==PIN['archiveBytes'] and record['dependencyScanVersion']==1 and hashlib.sha256(archive.read_bytes()).hexdigest()==record['sha256']
    assert sorted(e['name'] for e in record['entries'])==[e['name'] for e in MEMBERS]
    with zipfile.ZipFile(archive) as z:
        assert sorted(z.namelist())==[e['name'] for e in MEMBERS]
        for expected in MEMBERS:
            b=z.read(expected['name']); e=next(x for x in record['entries'] if x['name']==expected['name'])
            assert len(b)==e['bytes']==expected['decodedBytes'] and zlib.crc32(b)&0xffffffff==e['sourceCRC32']==expected['crc32'] and e['sourceCompressedBytes']==expected['compressedBytes'] and hashlib.sha256(b).hexdigest()==e['sha256']
    return record

def owned():
    from run import connect,reservations
    pins,data=load(); target,scope,refs=data; prep=read(PROPOSAL/'actual-readonly-preparation.json'); assert prep['passed'] and prep['caller']==ref(Path(__file__))
    lease=read(LEASE); assert reservations.owns(lease) and not DOC.exists() and not (LOCAL/'original').exists()
    refs=distinct_refs(refs+pins['codeRefs']+prep['evidenceRefs']+[ref(PROPOSAL/'draft-pins.json'),ref(PROPOSAL/'actual-readonly-preparation.json')])
    pulse=TimedOwnedLeasePulse(lambda:reservations.owns(lease),lambda:reservations.heartbeat(lease,ttl=3600))
    def fence():
        pulse(force=True)
        for q in refs: check(q); pulse()
        assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT; pulse(force=True)
    fence()
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY'); assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',read(ORDINARY/'result.json'))
    DOC.mkdir(); save(DOC/'selection.json',dict(uid=UID,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,sourceArchive=PIN,exactTerrainMembers=MEMBERS,requestedBuildingModels=[],sourceOrdinaryDiagnostic=ref(ORDINARY/'diagnostic.json.gz'),scope=scope,noGeometryDecode=True))
    try:
        record=module(DOWNLOADER,'heritage_terrain_download').acquire(target,DIRECTORY/'zip-directory.bin',LOCAL/'original',include_terrain=True)
        archive=LOCAL/'original/7-SW-15D.zip'; verify_record(record,archive); fence()
        with zipfile.ZipFile(archive) as z:
            for e in MEMBERS:
                path=LOCAL/'terrain'/e['name']; path.parent.mkdir(parents=True,exist_ok=True)
                with path.open('xb') as out: out.write(z.read(e['name']))
        save(DOC/'authentic-terrain-members.json',dict(uid=UID,sourceArchive=PIN,originalUnmodifiedMembers=[dict(**e,extracted=ref(LOCAL/'terrain'/e['name'])) for e in MEMBERS],download=ref(LOCAL/'original/download.json'),compactArchive=ref(archive),rawPriorOrdinaryDiagnosticRetained=ref(ORDINARY/'diagnostic.json.gz'),geometryDecoded=False,terrainNominated=False,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
        refs=distinct_refs(refs+[ref(p) for folder in [DOC,LOCAL] for p in folder.rglob('*') if p.is_file() and p.name!='reservation.json']); fence()
        module(FREEZER,'heritage_acquire_freezer').freeze(BATCH,'exact-pinned-original-two-terrain-member-acquisition-no-decode',[check(q) for q in refs],dict(uids=[UID],sourceOnly=True,authenticTerrainAcquired=True,geometryDecoded=False,terrainNominated=False,physicalAccepted=False,newlyInstalled=0))
    except Exception as error:
        save(DOC/'acquisition-failure.json',dict(errorType=type(error).__name__,error=str(error),partialSourceOutputsPreserved=True,modelDefectInferred=False)); raise

def main():
    if '--schema-only' in sys.argv:
        pins,data=load(); print(json.dumps(dict(passed=True,caller=ref(Path(__file__)),exactTerrainMembers=2,compressedMemberBytes=2869630,currentManifestSHA256=CURRENT,currentSnapshot=SNAPSHOT,scope=data[1],geometryDecodeDBLeaseWorker=False))); return
    if '--owned' in sys.argv: return owned()
    assert sys.argv[1:]==['--acquire-authentic-terrain-only'] and not DOC.exists() and not LOCAL.exists()
    pins,data=load(); assert read(PROPOSAL/'actual-readonly-preparation.json')['passed']
    from run import reservations
    resources=['building:'+u for u in data[1]]+['terrain-patch:'+u for u in data[1]]+['immutable-source-proof:'+BATCH]
    claim=reservations.claim('heritage-terrain-acquire-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600); assert claim['ok']; lease=claim['reservation']
    try:
        save(LEASE,json.loads(json.dumps(lease,default=str)))
        subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
    finally:
        if reservations.owns(lease): assert reservations.release(lease)['ok']
if __name__=='__main__': main()
