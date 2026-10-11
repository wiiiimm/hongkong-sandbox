"""Bounded local government-model validation. Reuse exact sources; never AI or automatic acceptance."""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent/'shared-modelling'))
from db import connect
import jobs
import reservations
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
STAGE = 'government-import-validation-v1'
NATIVE_RUN = 'e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec'

def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)

def digest(raw): return hashlib.sha256(raw).hexdigest()
def encode(value): return jobs.encode(value).encode()
def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    raw = encode(value)
    path.write_bytes(gzip.compress(raw, mtime=0) if str(path).endswith('.gz') else raw+b'\n')

def select_candidates(cached, current, plan, completed, limit):
    selected = []
    for uid, row in sorted(cached.items(), key=lambda item: (item[1]['candidate']['entry']['sourceTile'], item[0])):
        b = current.get(uid, {}).get('building'); p = plan.get(uid)
        if not b or not p or p['action']=='skip' or b.get('modelGeometry') or row.get('currentNative') or uid in completed: continue
        e = row['candidate']['entry']
        if b.get('buildingCSUID')!=e['buildingCSUID'] or b.get('objectId')!=e['objectId']: continue
        selected.append(uid)
        if len(selected)==limit: break
    if len(selected)!=limit: raise ValueError('Not enough eligible locally cached sources; extend cache discovery explicitly')
    return selected

def prepare(batch, count):
    folder = HERE/'local'/batch
    if folder.exists(): raise ValueError('Batch output already exists; resume its frozen selection with --execute')
    plan_path = HERE/'local/plan/inputs.json.gz'; plan = read(plan_path)
    if not read(HERE/'local/plan/summary.json')['authoritative']: raise ValueError('Live acceptance plan required')
    cached = {}; outcomes = {}
    for name in ['shape-inputs.json.gz', 'shape-5000/inputs.json.gz']:
        e = read(HERE.parent/'enhancement-screening/local'/name)
        if e['nativeRun']!=NATIVE_RUN: raise ValueError('Unexpected source run')
        for o in e['native']:
            for v in o['model'].get('matching',{}).get('viewerMatches',[]):
                outcomes.setdefault(v['uid'], {})[o['cacheKey']+o['model']['modelId']] = o
    for name in ['shapes/geometry-inputs.json', 'shape-5000/geometry-inputs.json']:
        for row in read(HERE.parent/'enhancement-screening/local'/name)['rows']: cached[row['uid']] = row
    manifest = read(ROOT/'3d-viewer/city/data/manifest.json')
    current = {}; installed = set()
    for url in manifest.get('officialModelCatalogues',[]): installed.update(m['uid'] for m in read(ROOT/'3d-viewer'/url)['models'])
    for tile in manifest['tiles']:
        path = ROOT/'3d-viewer'/tile['url']; raw = path.read_bytes(); sha = digest(raw)
        for b in json.loads(raw)['buildings']:
            if b['uid'] in cached: current[b['uid']] = {'building':b,'tile':tile['url'],'tileSHA256':sha}
    planned = {r['uid']:r for r in plan['rows']}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        previous = c.execute("SELECT x->>'uid',x->>'inputHash',x->>'sourceSHA256' FROM astra_modelling.jobs j CROSS JOIN LATERAL jsonb_array_elements(j.result->'rows') x WHERE j.stage=%s AND j.status='complete'", (STAGE,)).fetchall()
    completed = {uid for uid,input_hash,source_sha in previous if uid in planned and uid in cached and planned[uid]['inputHash']==input_hash and cached[uid]['candidate']['entry']['sha256']==source_sha}
    ids = select_candidates(cached,current,planned,completed|installed,count)
    chosen = []
    for uid in ids:
        o = list(outcomes.get(uid,{}).values())
        if len(o)!=1 or o[0]['model']['state']!='packed-needs-placement-review': raise ValueError('Source ambiguous or held: '+uid)
        row = cached[uid]; raw = Path(row['candidate']['path']).read_bytes(); e = row['candidate']['entry']
        if digest(raw)!=e['sha256'] or len(raw)!=e['bytes'] or o[0]['model']['asset']['sha256']!=e['sha256']: raise ValueError('Cached source bytes changed')
        chosen.append({'uid':uid,'inputHash':planned[uid]['inputHash'],'source':current[uid],'candidate':row['candidate'],'native':o[0]})
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        frozen = dict(c.execute('SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=ANY(%s)',(NATIVE_RUN, sorted({r['native']['cacheKey'] for r in chosen}))))
    if any(frozen.get(r['native']['cacheKey'])!=r['native']['resultSha'] for r in chosen): raise ValueError('Frozen native results do not match live Neon')
    inputs = {'batch':batch,'stage':STAGE,'nativeRun':NATIVE_RUN,'rows':chosen,'planSHA256':digest(plan_path.read_bytes()),'contextHash':plan['contextHash'],'manifestSHA256':digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes()),'sourceCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
    save(folder/'selection.json.gz', inputs)
    print(json.dumps({'selected':len(ids),'sheets':len({r['candidate']['entry']['sourceTile'] for r in chosen}),'originalBytes':sum(r['candidate']['entry']['bytes'] for r in chosen),'aiCalls':0}),flush=True)
    receipt = reservations.claim('codex-government-import-'+str(uuid.uuid4()),['building:'+uid for uid in ids],batch=batch)
    if not receipt['ok']: raise ValueError('Source reservation conflict; batch not started')
    save(folder/'reservation.json',json.loads(json.dumps(receipt['reservation'],default=str)))
    return subprocess.call([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(folder/'reservation.json'),'--',sys.executable,str(Path(__file__)),'--execute',str(folder)],cwd=ROOT)

def execute(folder):
    folder = Path(folder).resolve(); inputs = read(folder/'selection.json.gz'); receipt = read(folder/'reservation.json')
    if not reservations.owns(receipt): raise ValueError('Live source ownership required')
    if digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())!=inputs['manifestSHA256']: raise ValueError('Manifest changed since selection')
    for row in inputs['rows']:
        if digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())!=row['source']['tileSHA256']: raise ValueError('Current source changed since selection')
    catalogue = {k:v for k,v in read(HERE.parent/'kai-tak-port/staged/catalogue.json').items() if k not in ('models','counts','area')}
    catalogue.update(area=inputs['batch'],counts={'packedModels':len(inputs['rows'])},models=[])
    for row in inputs['rows']:
        entry = {**row['candidate']['entry']}; raw = Path(row['candidate']['path']).read_bytes()
        if digest(raw)!=entry['sha256'] or len(raw)!=entry['bytes']: raise ValueError('Source hash changed before staging')
        target = folder/'candidates'/entry['asset']; target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        catalogue['models'].append(entry)
    save(folder/'candidates/catalogue.json',catalogue);save(folder/'candidates/catalogue-index.json',{'models':len(catalogue['models']),'catalogues':['catalogue.json']})
    save(folder/'source-forms.json',{r['uid']:r['source'] for r in inputs['rows']})
    code = [HERE/'run.py',HERE.parent/'building-batch/validate_candidates.mjs']
    payload = {'stage':STAGE,'selectionSHA256':digest((folder/'selection.json.gz').read_bytes()),'pipelineSHA256':digest(b''.join(p.read_bytes() for p in code)),'contextHash':inputs['contextHash'],'uids':[r['uid'] for r in inputs['rows']]}
    job_id = jobs.enqueue(inputs['batch'],STAGE,payload);job = jobs.claim(inputs['batch'],receipt['owner'],[STAGE],lease_seconds=1800)
    if not job or job['id']!=job_id: raise ValueError('No claimable matching validation job; inspect shared status before retry')
    command = ['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(folder/'candidates'),'--source-forms',str(folder/'source-forms.json'),'--out',str(folder/'validation.json')]
    result = subprocess.run(command,cwd=ROOT)
    if result.returncode not in (0,1) or not (folder/'validation.json').exists(): raise ValueError('Validation did not produce complete outcomes')
    validation = read(folder/'validation.json'); by_uid = {r['uid']:r for r in validation['results']}
    if set(by_uid)!=set(payload['uids']) or len(validation['results'])!=len(payload['uids']): raise ValueError('Incomplete validation outcomes')
    rows = []
    for row in inputs['rows']:
        uid=row['uid'];v=by_uid[uid];e=row['candidate']['entry'];b=row['source']['building']
        reasons=list(v.get('concerns',[]))
        if v['outcome']=='validation-exception': reasons.append('runtime-validation-exception')
        if e.get('recordedBaseHeight')!=b.get('baseHeightHKPD') or e.get('recordedTopHeight')!=b.get('topHeightHKPD'): reasons.append('source-recorded-height-mismatch')
        if e.get('overlapOfSmallerFootprint',0)<.9 or e.get('footprintCentroidDistanceMetres',float('inf'))>2: reasons.append('footprint-match-needs-investigation')
        rows.append({'uid':uid,'inputHash':row['inputHash'],'modelId':e['modelId'],'sourceSHA256':e['sha256'],'sourceTile':e['sourceTile'],'state':'retained-pending-placement' if reasons else 'runtime-validated-awaiting-acceptance','reasons':reasons,'validation':{k:value for k,value in v.items() if k!='seconds'},'geometryMethod':'scripted','aiCalls':0,'published':False})
    summary={'batch':inputs['batch'],'stage':STAGE,'jobId':job_id,'models':len(rows),'counts':dict(Counter(r['state'] for r in rows)),'reasons':dict(Counter(reason for r in rows for reason in r['reasons'])),'preparedBytes':sum(r['candidate']['entry']['bytes'] for r in inputs['rows']),'cacheHits':len(rows),'sourceDownloadBytes':0,'aiCalls':0,'published':False,'newAcceptanceDecisions':0,'rows':rows,'inputHashes':validation['hashes'],'selectionSHA256':payload['selectionSHA256'],'pipelineSHA256':payload['pipelineSHA256'],'qualification':'Mechanical runtime and sampled placement validation only; unresolved context and architectural acceptance remain pending. No AI modelling or geometry edits.'}
    doc=ROOT/'docs/astra-city/government-import'/inputs['batch'];save(doc/'results.json.gz',summary)
    evidence={'path':str((doc/'results.json.gz').relative_to(ROOT)),'sha256':digest((doc/'results.json.gz').read_bytes())}
    with connect() as c:
        c.row_factory=dict_row;c.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
        group=reservations._current(c,receipt)
        if not group or not {'building:'+uid for uid in payload['uids']}<=set(group['resources']): raise ValueError('Source ownership lost before result sync')
        updated=c.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb({**summary,'evidence':evidence}),job_id,job['owner'],job['token'])).rowcount
        if updated!=1: raise ValueError('Job ownership lost before sync')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');stored=c.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s AND status=\'complete\'',(job_id,)).fetchone()[0]
    if stored!={**summary,'evidence':evidence}: raise ValueError('Neon result readback differs')
    save(doc/'summary.json',{k:v for k,v in summary.items() if k not in ('rows','inputHashes')})
    save(doc/'neon-sync.json',{'jobId':job_id,'verifiedRows':len(stored['rows']),'exactResultMatch':True,'sourceReservationFenced':True,'modelReviewWrites':0})
    shutil.copyfile(folder/'selection.json.gz',doc/'selection.json.gz');shutil.copyfile(folder/'validation.json',doc/'validation.json')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('rows','inputHashes')}),flush=True)
    return 0

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch');p.add_argument('--count',type=int,default=200);p.add_argument('--execute',type=Path);a=p.parse_args()
    if a.execute: sys.exit(execute(a.execute))
    if not a.batch or not a.batch.replace('-','').isalnum() or not 1<=a.count<=1000:p.error('Named batch and count 1..1000 required')
    sys.exit(prepare(a.batch,a.count))
