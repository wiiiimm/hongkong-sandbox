"""Recover byte-identical authored support actors; never certify or publish them."""
import importlib.util
import json
import subprocess
import sys
import uuid
import zipfile
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN

BATCH='government-xl-southside-station-original-recovery-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
GROUPS={'315025':[315025,300867]}

def reference(path):
    return {'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes())}

def owned():
    lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';pinned=digest(manifest.read_bytes())
    wanted={'landsd/'+str(i)+':0' for ids in GROUPS.values() for i in ids}
    sources={}
    for tile in read(manifest)['tiles']:
        path=ROOT/'3d-viewer'/tile['url']
        for b in read(path)['buildings']:
            if b['uid'] in wanted:
                assert b['uid'] not in sources
                sources[b['uid']]={'building':b,'tile':tile['url'],'tileSHA256':digest(path.read_bytes())}
    assert set(sources)==wanted
    spec=importlib.util.spec_from_file_location('support_exact_recovery',HERE/'xl-next-support-recovery-20261005.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    rows=[];missing=[];refs=[reference(manifest),reference(Path(__file__)),reference(HERE/'xl-next-support-recovery-20261005.py')]
    for uid,source in sorted(sources.items()):
        assert reservations.heartbeat(lease)['ok'];b=source['building'];matches=[]
        with connect() as con:
            con.execute('SET TRANSACTION READ ONLY')
            profiles=con.execute('SELECT DISTINCT cache_key,sheet FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,'B'+b['buildingCSUID'][:10]+'%')).fetchall()
            for key,sheet in profiles:
                sha,data=con.execute('SELECT r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,key)).fetchone()
                for model in data['models']:
                    if model['modelId'][1:11]==b['buildingCSUID'][:10] and any(v['objectId']==b['objectId'] and v['buildingCSUID']==b['buildingCSUID'] for v in model.get('matching',{}).get('officialCandidates',[])):
                        matches.append({'cacheKey':key,'resultSha':sha,'sheet':sheet,'model':model})
        if len(matches)!=1:
            missing.append({'uid':uid,'currentSource':source,'exactNativeMatches':len(matches),'profiles':profiles});continue
        native=matches[0];entry,basis=helper.diagnostic_entry(native,b);sha=native['model']['asset']['sha256'];cached=[]
        found=subprocess.run(['rg','--files','--hidden','--no-ignore','-g',sha+'.glb.gz',str(HERE/'local'),str(ROOT/'3d-viewer/city/data/official-models')],capture_output=True,text=True,check=False)
        assert found.returncode in (0,1)
        for value in found.stdout.splitlines():
            path=Path(value)
            if digest(path.read_bytes())==sha:cached.append(path)
        if cached:
            raw=cached[0].read_bytes();recovery={'method':'verified-local-original','transferredBytes':0};refs.append(reference(cached[0]))
        else:
            sheet=native['sheet'];folder=LOCAL/'sheets'/sheet
            with connect() as con:
                con.execute('SET TRANSACTION READ ONLY')
                directory_pin=con.execute("SELECT result-'models' FROM astra_modelling.city_source_directories WHERE sheet=%s ORDER BY created_at DESC LIMIT 1",(sheet,)).fetchone()[0]
            directory,_=helper.scan({'SHEETNO':sheet,'Format_glTF':directory_pin['sourceURL'],'REVISIONDATE':directory_pin['revision']},folder/'directory')
            directory['models']=[m for m in directory['models'] if m['modelId']==native['model']['modelId']];assert len(directory['models'])==1
            receipt=helper.acquire(directory,folder/'directory/zip-directory.bin',folder/'original')
            packed=folder/'packed';packed.mkdir(exist_ok=True)
            with zipfile.ZipFile(folder/'original'/(sheet+'.zip')) as archive:
                converted=helper._convert_one(archive,archive.getinfo(native['model']['sourceEntry']),folder/'decoded',packed,{}, {'modelId':native['model']['modelId']})
                raw=helper.canonical_bytes((packed/converted['asset']['asset']).read_bytes(),sha)
            recovery={'method':'exact-original-government-recovery','transferredBytes':receipt['newThisInvocationBytes']}
        assert digest(raw)==sha and len(raw)==native['model']['asset']['bytes']
        destination=LOCAL/'assets'/(sha+'.glb.gz');destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
        entry['asset']='assets/'+destination.name
        row={'uid':uid,'source':source,'native':native,'modelId':native['model']['modelId'],'sourceSHA256':sha,
             'candidate':{'entry':entry,'path':str(destination.relative_to(ROOT))},'sourceLookupBasis':basis,'currentReview':None,'recovery':recovery}
        rows.append(row);refs.extend([reference(destination),reference(ROOT/'3d-viewer'/source['tile'])])
        save(DOC/'partial-selection.json.gz',{'rows':rows,'missing':missing,'manifestSHA256':pinned,'groups':GROUPS})
        print(json.dumps({'uid':uid,'name':b.get('name'),'modelId':row['modelId'],'triangles':native['model']['triangles'],'bounds':native['model']['worldBounds'],'transferredBytes':recovery['transferredBytes']}),flush=True)
    assert reservations.owns(lease) and digest(manifest.read_bytes())==pinned
    save(DOC/'selection.json.gz',{'rows':rows,'missing':missing,'manifestSHA256':pinned,'groups':GROUPS,'evidenceRefs':list({r['path']:r for r in refs}.values()),'sourceGeometryChanges':0,'publication':False,'installationApproved':False})

def main():
    if '--owned' in sys.argv:return owned()
    assert not DOC.exists() and not LOCAL.exists()
    resources=['building:landsd/'+str(i)+':0' for ids in GROUPS.values() for i in ids]
    claim=reservations.claim('southside-station-originals-'+str(uuid.uuid4()),resources,batch=BATCH);assert claim['ok'],claim
    save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)

if __name__=='__main__':main()
