"""Fresh original-byte/GeoRef-cell identity for the explicit island follow-up.

Uses the established full-cell verifier; no acceptance, source edit or AI call.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import uuid
import numpy as np
import shapely
from shapely.geometry import box
from islands_direct_stage import ROOT,HERE,read,save,sha,rel,module
SELECTION = None

def selected_rows():
    selection = read(SELECTION)
    assert selection['manifestSHA256'] == sha(ROOT/'3d-viewer/city/data/manifest.json')
    rows = selection['rows']
    assert 0 < len(rows) == len({r['uid'] for r in rows}) <= 1000
    return rows
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles
from government_georef_cell_identity import verify
from run import jobs,reservations,connect,dict_row,Jsonb


def owned(batch):
    local=HERE/'local'/batch;doc=ROOT/'docs/astra-city/government-import'/batch
    receipts=read(local/'reservations.json');assert all(reservations.owns(r)for r in receipts)
    rows=selected_rows();pins={}
    for p in [Path(__file__),SELECTION,HERE/'government_georef_cell_identity.py',HERE/'original_source_ownership.py',HERE/'exact_packed_world_geometry_v2_20261103.py',HERE/'xl-final-script-pass.py',ROOT/'3d-viewer/city/data/manifest.json']:
        pins[rel(p)]=sha(p)
    final=module('islands_fresh_complete_identity',HERE/'xl-final-script-pass.py')
    bounds=np.asarray([r['candidate']['entry']['worldBounds']for r in rows]);extent=[bounds[:,:,0].min()-20,bounds[:,:,2].min()-20,bounds[:,:,0].max()+20,bounds[:,:,2].max()+20]
    forms=final.load_forms(extent);tree=shapely.STRtree([poly for _,poly,_ in forms])
    for _,_,url in forms:p=ROOT/'3d-viewer'/url;pins[rel(p)]=sha(p)
    outcomes=[]
    for n,original in enumerate(rows,1):
        entry=original['candidate']['entry'];row={**original,'sourceSHA256':entry['sha256'],'modelId':entry['modelId'],'triangles':entry['triangles']}
        raw=(ROOT/row['candidate']['path']).read_bytes();assert sha(ROOT/row['candidate']['path'])==entry['sha256'];pins[row['candidate']['path']]=entry['sha256']
        triangles=decode_original_world_triangles(raw);lo,hi=triangles.min(axis=(0,1)),triangles.max(axis=(0,1))
        nearby=[forms[int(i)]for i in tree.query(box(lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2))]
        identity=final.identity_context(row,triangles,nearby)
        context={'uid':row['uid'],'sourceSHA256':entry['sha256'],'identity':identity,'neighbourTileHashes':{url:sha(ROOT/'3d-viewer'/url)for _,_,url in nearby}}
        result=verify(raw,row,context,triangles,current_identity=identity)
        outcomes.append({**result,'context':context,'modelId':row['modelId'],'humanStatus':'in-process','requiresAI':False,'requiresUserDecision':False})
        if n%100==0:print(json.dumps({'identityChecked':n,'total':len(rows),'positiveIdentities':sum(r['passed']for r in outcomes)}),flush=True)
    for p,digest in pins.items():assert sha(ROOT/p)==digest,p
    report={'batch':batch,'models':len(rows),'rows':outcomes,'positiveIdentities':sum(r['passed']for r in outcomes),
        'reasonCounts':dict(Counter(x for r in outcomes for x in r['reasons'])),'inputHashes':pins,
        'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'aiCalls':0,
        'qualification':'Fresh exact source graphs and whole official geographic cells; no physical/placement/browser approval or source assignment edits.'}
    save(doc/'identities.json.gz',report)
    payload={'path':rel(doc/'identities.json.gz'),'sha256':sha(doc/'identities.json.gz')};stage='islands-exact-original-cell-identity-v1'
    jobid=jobs.enqueue(batch,stage,payload);job=jobs.claim(batch,receipts[0]['owner'],[stage],lease_seconds=1800);assert job and job['id']==jobid
    result={**report,'jobId':jobid,'evidence':payload}
    with connect()as db:
        db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,));groups=[reservations._current(db,r)for r in receipts];assert all(groups)
        assert {'building:'+r['uid']for r in rows}<=set().union(*(set(g['resources'])for g in groups))
        assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
    save(doc/'neon-sync.json',{'jobId':jobid,'exactResultMatch':True,'models':len(rows),'publication':False})
    save(doc/'summary.json',{k:v for k,v in report.items()if k not in ('rows','inputHashes')})
    print(json.dumps({'complete':True,'models':len(rows),'positiveIdentities':report['positiveIdentities'],'jobId':jobid}),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');p.add_argument('--selection',type=Path,required=True);a=p.parse_args()
    global SELECTION
    SELECTION=a.selection.resolve();assert SELECTION.is_relative_to(ROOT)
    assert a.batch.startswith('government-islands-') and '-identity-' in a.batch and '/' not in a.batch
    if a.owned:return owned(a.batch)
    local=HERE/'local'/a.batch;assert not local.exists() and not (ROOT/'docs/astra-city/government-import'/a.batch).exists();local.mkdir(parents=True);receipts=[];owner='codex-islands-identity-'+str(uuid.uuid4());rows=selected_rows()
    try:
        for offset in range(0,len(rows),1000):
            claim=reservations.claim(owner,['building:'+r['uid']for r in rows[offset:offset+1000]],batch=a.batch,ttl=3600);assert claim['ok']
            receipts.append(json.loads(json.dumps(claim['reservation'],default=str)));save(local/f'reservation-{len(receipts)}.json',receipts[-1])
        save(local/'reservations.json',receipts);cmd=[sys.executable,__file__,'--batch',a.batch,'--selection',str(SELECTION),'--owned']
        for i in range(len(receipts),0,-1):cmd=[sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',local/f'reservation-{i}.json','--ttl','3600','--',*cmd]
        subprocess.run([str(x)for x in cmd],cwd=ROOT,check=True)
    finally:
        for r in receipts:
            if reservations.owns(r):reservations.release(r)


if __name__=='__main__':main()
