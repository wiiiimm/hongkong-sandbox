"""Bounded original-source/terrain diagnostics for explicit island follow-up.

Diagnostic only: retains all raw failures; no source edits, approval or install.
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
from islands_direct_stage import ROOT, HERE, read, save, sha, rel, module
from run import jobs, reservations, connect, dict_row, Jsonb


def paths(batch):
    return ROOT/'docs/astra-city/government-import'/batch, HERE/'local'/batch


SELECTION = None

def selected_rows():
    data=read(SELECTION)
    assert data['manifestSHA256']==sha(ROOT/'3d-viewer/city/data/manifest.json')
    rows=data['rows']
    assert 0<len(rows)==len({r['uid'] for r in rows})<=1000
    return rows


def owned(batch):
    doc,local=paths(batch);receipts=read(local/'reservations.json')
    assert all(reservations.owns(r) for r in receipts)
    rows=selected_rows();selection={r['uid']:r for r in rows}
    terrain_doc=ROOT/'docs/astra-city/government-import/government-islands-cheung-chau-source-terrain-20261106-v1'
    terrain_local=HERE/'local/government-islands-cheung-chau-source-terrain-20261106-v1'
    old=module('islands_existing_context',HERE/'tai-o-exact-pass.py')
    pins={}
    def pin(path):pins[rel(path)]=sha(path)
    for p in [Path(__file__),SELECTION,HERE/'tai-o-exact-pass.py',terrain_doc/'check-selection.json.gz',terrain_doc/'source-terrain.json',terrain_local/'geometry.json.gz',ROOT/'3d-viewer/city/data/manifest.json']:
        pin(p)
    geometry=read(terrain_local/'geometry.json.gz')
    for p,digest in geometry['inputHashes'].items():assert sha(ROOT/p)==digest;pins[p]=digest
    geometries={r['uid']:r for r in geometry['rows']}
    assert set(selection)<=set(geometries)
    terrains={};terrain_errors={}
    needed_sheets={r['native']['sheet'] for r in rows}
    for proof in read(terrain_doc/'source-terrain.json')['sheets']:
        for p in proof['members']:assert sha(ROOT/p['path'])==p['sha256'];pins[p['path']]=p['sha256']
        if proof['sheet'] not in needed_sheets:continue
        try:
            terrains[proof['sheet']]=np.concatenate([old.context.triangles(p) for p in sorted((terrain_local/'source-terrain'/proof['sheet']/'decoded').rglob('*.gltf'))])
        except (ValueError,AssertionError) as error:
            # Do not admit malformed terrain or stop unrelated valid sheets.
            terrain_errors[proof['sheet']]={'error':str(error),'sourceFiles':proof['members'],
                'sourceCorruptionEstablished':False,'acceptance':False}

    # Build only the bounded island form tree; every source tile is still pinned.
    limits=np.array([r['candidate']['entry']['worldBounds'] for r in rows])
    extent=box(limits[:,:,0].min()-20,limits[:,:,2].min()-20,limits[:,:,0].max()+20,limits[:,:,2].max()+20)
    forms=[]
    for tile in read(ROOT/'3d-viewer/city/data/manifest.json')['tiles']:
        p=ROOT/'3d-viewer'/tile['url'];pin(p)
        for form in read(p)['buildings']:
            if not form.get('rings'):continue
            shape=old.polygon(form)
            if shape.intersects(extent):forms.append((form,shape,tile['url']))
    tree=shapely.STRtree([shape for _,shape,_ in forms]);outcomes=[]
    for n,row in enumerate(rows,1):
        triangles=old.geometry_triangles(geometries[row['uid']]);lo,hi=triangles.min(axis=(0,1)),triangles.max(axis=(0,1))
        nearby=[forms[int(i)] for i in tree.query(box(lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2))]
        identity,_=old.identity_context(row,triangles,nearby)
        terrain_error=terrain_errors.get(row['native']['sheet'])
        foundation=({'available':False,'validationException':terrain_error} if terrain_error else
                    old.foundation_context(triangles,terrains[row['native']['sheet']]))
        reasons=[]
        if not identity['exactObjectAndCSUID']:reasons.append('exact-identity-mismatch')
        if identity['officialOverlapOfSmallerFootprint']<.98 or identity['officialFootprintCentroidDistanceM']>1:reasons.append('strict-identity-fit')
        if terrain_error:
            reasons.append('source-terrain-validation-exception')
        else:
            if foundation['completeTerrainTriangles']!=foundation['triangles']:reasons.append('source-terrain-coverage')
            if foundation['minimumGapM'] is None or foundation['minimumGapM']<-.5:reasons.append('source-terrain-burial-over-0.5m')
            if foundation['minimumGapM'] is not None and foundation['minimumGapM']>.1:reasons.append('source-terrain-contact-unresolved')
        outcomes.append({'uid':row['uid'],'sourceSHA256':row['candidate']['entry']['sha256'],'sourceSheet':row['native']['sheet'],
             'identity':identity,'foundation':foundation,'diagnosticReasons':reasons,'humanStatus':'in-process',
             'next':'Current rendered-terrain construction/contact and identity continuation; diagnostic grants no acceptance',
             'requiresAI':False,'requiresUserDecision':False,'publication':False})
        if n%50==0:print(json.dumps({'contextChecked':n,'total':len(rows),'sourceTINStrictPreliminary':sum(not r['diagnosticReasons'] for r in outcomes)}),flush=True)
    for p,digest in pins.items():assert sha(ROOT/p)==digest,p
    report={'batch':batch,'terrainValidationExceptions':terrain_errors,'rows':outcomes,'models':len(rows),'reasonCounts':dict(Counter(x for r in outcomes for x in r['diagnosticReasons'])),
            'sourceTINStrictPreliminary':sum(not r['diagnosticReasons'] for r in outcomes),'inputHashes':pins,
            'modelGeometryChanges':0,'terrainChanges':0,'aiCalls':0,'newlyInstalled':0,'publication':False,
            'qualification':'Reuses original full-face terrain and projected identity diagnostics, not acceptance or runtime terrain. All failures retained.'}
    save(doc/'context.json.gz',report)
    payload={'evidence':{'path':rel(doc/'context.json.gz'),'sha256':sha(doc/'context.json.gz')},'models':len(rows)}
    stage='islands-original-source-context-v1';jobid=jobs.enqueue(batch,stage,payload);job=jobs.claim(batch,receipts[0]['owner'],[stage],lease_seconds=1800)
    assert job and job['id']==jobid
    result={**report,'jobId':jobid,'evidence':payload['evidence']}
    with connect()as db:
        db.row_factory=dict_row;db.execute('SELECT pg_advisory_xact_lock(%s)',(reservations.LOCK_ID,))
        groups=[reservations._current(db,r) for r in receipts];assert all(groups)
        assert {'building:'+r['uid'] for r in rows}<=set().union(*(set(g['resources']) for g in groups))
        assert db.execute("UPDATE astra_modelling.jobs SET status='complete',result=%s,owner=NULL,token=NULL,lease_until=NULL,updated_at=clock_timestamp() WHERE id=%s AND owner=%s AND token=%s AND status='running' AND lease_until>clock_timestamp()",(Jsonb(result),jobid,job['owner'],job['token'])).rowcount==1
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()[0]==result
    save(doc/'neon-sync.json',{'jobId':jobid,'exactResultMatch':True,'models':len(rows),'publication':False})
    save(doc/'summary.json',{k:v for k,v in report.items() if k not in ('rows','inputHashes')})
    print(json.dumps({'complete':True,'models':len(rows),'jobId':jobid,'reasonCounts':report['reasonCounts']}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',required=True);parser.add_argument('--owned',action='store_true');parser.add_argument('--selection',type=Path,required=True);a=parser.parse_args()
    global SELECTION
    SELECTION=a.selection.resolve();assert SELECTION.is_relative_to(ROOT)
    assert a.batch.startswith('government-islands-cheung-chau-context-') and '/' not in a.batch
    if a.owned:return owned(a.batch)
    doc,local=paths(a.batch);assert not local.exists() and not doc.exists()
    local.mkdir(parents=True);rows=selected_rows();receipts=[];owner='codex-islands-context-'+str(uuid.uuid4())
    try:
        for offset in range(0,len(rows),1000):
            claim=reservations.claim(owner,['building:'+r['uid'] for r in rows[offset:offset+1000]],batch=a.batch,ttl=3600)
            assert claim['ok'],'Existing source owner; no takeover'
            receipts.append(json.loads(json.dumps(claim['reservation'],default=str)))
            save(local/f'reservation-{len(receipts)}.json',receipts[-1])
        save(local/'reservations.json',receipts)
        cmd=[sys.executable,__file__,'--batch',a.batch,'--selection',str(SELECTION),'--owned']
        for i in range(len(receipts),0,-1):cmd=[sys.executable,HERE.parent/'shared-modelling/reservations.py','run','--lease-file',local/f'reservation-{i}.json','--ttl','3600','--',*cmd]
        subprocess.run([str(x)for x in cmd],cwd=ROOT,check=True)
    finally:
        for r in receipts:
            if reservations.owns(r):reservations.release(r)


if __name__=='__main__':main()
