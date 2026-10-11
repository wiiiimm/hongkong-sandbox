"""Commit an actually verified XL installation or exact support pair after coordinator image inspection.

Exact source-specific paths only; no broad staging, model processing or approval
inference. Current snapshot, source bytes, receipts, Neon and goal counts must agree.
"""
import argparse, re, subprocess
from pathlib import Path
from run import ROOT, HERE, read, digest, connect

def call(command):
    subprocess.run(command,cwd=ROOT,check=True)

def check_auxiliary_scope(original_inputs,uids,shas,catalogue,xl):
    original_sources={r['uid']:r for r in original_inputs['sources']}
    supports={r['supportUid'] for r in original_inputs['pairs']}
    assert set(uids)<=supports and not set(uids)&xl,'Auxiliary support must not add XL credit'
    assert {m['uid'] for m in catalogue['models']}==set(uids)
    for model in catalogue['models']:
        original=original_sources[model['uid']]
        assert original['sourceSHA256']==shas[model['uid']]
        assert original['source']['building']['structureType']=='Podium'
        for key in ('uid','objectId','buildingCSUID','sha256','worldBounds'):
            assert model[key]==original['candidate']['entry'][key]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True,help='Exact installed evidence directory within government-import')
    p.add_argument('--browser-inspected',action='store_true',required=True,help='Coordinator has viewed the exported live browser image')
    p.add_argument('--push',action='store_true')
    p.add_argument('--support-closure',help='Exact verified original closure for a supporting podium outside XL352; gives zero XL credit')
    a=p.parse_args();doc=(ROOT/a.source).resolve()
    assert doc.parent==ROOT/'docs/astra-city/government-import' and doc.name.startswith('government-xl-')
    assert not (doc/'README.md').exists(),'Do not rewrite a completed installation note'
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    assert branch=='codex/astra-hong-kong-city','Only the explicitly authorised non-main branch'
    assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).strip(),'Never combine with pre-existing staging'
    result=read(doc/'result.json');assert result['passed'] and result['newlyInstalled']==len(result['installedUids']) and result['newlyInstalled'] in (1,2)
    assert result['publication'] and result['modelGeometryChanges']==result['scriptExternalAICalls']==0 and not result['failures']
    uids=result['installedUids'];assert result['uids']==uids and len(set(uids))==len(uids)
    shas=result.get('sourceSHA256s') or {uids[0]:result['sourceSHA256']};assert set(shas)==set(uids)
    assert read(doc/'neon-sync.json')=={'installedUids':uids,'jobId':result['jobId'],'resultVerified':True,'snapshotId':result['snapshotId']}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    for ref in [*result['evidenceRefs'],*result['evidence'].values()]:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    previous=(ROOT/result['evidence'].get('physical-result',result['evidence'].get('result'))['path']).parent
    prior=read(previous/'result.json');assert previous.parent==doc.parent and (prior.get('uids')==uids or prior.get('uid')==uids[0] and len(uids)==1)
    pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json');assert pointer['snapshotId']==result['snapshotId']
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert digest((ROOT/result['manifest']['path']).read_bytes())==result['manifest']['sha256']
    models=[m for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']]
    actual=[m for m in models if m['uid'] in uids];assert len(actual)==len(uids) and {m['uid']:m['sha256'] for m in actual}==shas
    inventory=ROOT/pointer['inventory'];assert inventory.exists()
    staged=HERE/'accepted'/doc.name;catalogue=read(staged/'catalogue.json');assert [m['uid'] for m in catalogue['models']]==uids
    for model in catalogue['models']:assert digest((staged/model['asset']).read_bytes())==shas[model['uid']]
    published_batch=result.get('recoveredPublishedBatch',doc.name)
    assert Path(published_batch).name==published_batch and published_batch.startswith('government-xl-')
    published=ROOT/'3d-viewer/city/data/official-models'/published_batch
    for model in catalogue['models']:assert digest((published/model['asset']).read_bytes())==shas[model['uid']]
    xl={r['uid'] for r in read(ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923/selection.json.gz')['rows']};assert len(xl)==352
    support_closure=None
    if a.support_closure:
        support_closure=(ROOT/a.support_closure).resolve();assert support_closure.parent==doc.parent
        closure_result=read(support_closure/'result.json')
        assert closure_result['publication'] is False and closure_result['newlyInstalled']==0
        assert closure_result['modelGeometryChanges']==closure_result['scriptExternalAICalls']==0
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(closure_result['jobId'],)).fetchone()==('complete',closure_result)
        for ref in closure_result['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
        original_inputs=read(support_closure/'support-inputs.json')
        check_auxiliary_scope(original_inputs,uids,shas,catalogue,xl)
    else:assert set(uids)&xl,'Use the exact support-closure route for non-XL podiums'
    deployed={m['uid']:m for m in models if m['uid'] in xl}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        verified=c.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',
                           (pointer['snapshotId'],list(deployed))).fetchall()
    completed={u for u,state,sha in verified if state=='installed-verified' and sha==deployed[u]['sha256']}
    assert set(uids)&xl <= completed, 'Every XL installation must have an exact current installed review'
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        installed=c.execute('SELECT uid,review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=ANY(%s)',(pointer['snapshotId'],uids)).fetchall()
    assert {u:sha for u,state,sha in installed if state=='installed-verified'}==shas
    done=len(completed);new=done-44;assert 1<=new<=308
    progress=read(ROOT/'3d-viewer/city/data/building-progress.json');assert progress==result['progress']
    label=' and '.join(m.get('label') or m['uid'] for m in catalogue['models']);uid=', '.join(uids)
    note=(f'Codex, 7 October 2026. {label} ({uid}) is installed with unchanged original government geometry. '
          f'Verified Neon job `{result["jobId"]}`, installed snapshot `{result["snapshotId"]}`, source hashes `{shas}`. '
          'Complete original source identity/contact/foundation/basic/native/runtime and guarded publication pass. '
          'Staged/live desktop/mobile day/night, picking/collision and failed-load/retry pass; exported live mobile PNG inspected by coordinator. '
          'Zero model geometry edits or architectural/model AI calls. No historical Lantau imagery used.\n\n'
          f'{new} new XL installations from44/308: **{done} installed / {352-done} not installed**, {max(0,100-new)} further installations required. '
          f'Public counters: {progress["totalForms"]:,} total source forms, {progress["breakdown"]["enhanced"]:,} enhanced, '
          f'{progress["government"]["enhanced"]:,} / {progress["government"]["available"]:,} government matches installed. '
          'Queued/running rows remain In process. Commits and reports are checkpoints; the active goal continues.\n')
    if support_closure:note+='\nThis auxiliary original podium is outside XL352 and adds zero XL target credit. Exact source closure: '+str(support_closure.relative_to(ROOT))+'.\n'
    (doc/'README.md').write_text('# '+label+' — verified original installation\n\n'+note)
    skill=ROOT/'.agents/skills/hong-kong-model-improvement/SKILL.md';s=skill.read_text()
    match=re.search(r'version: "(\d+)\.(\d+)\.(\d+)"',s);assert match
    version=f'{match[1]}.{match[2]}.{int(match[3])+1}'
    skill.write_text(s.replace(match[0],f'version: "{version}"',1)+'\n## Latest actual XL installation checkpoint\n\n'+note)
    tracking=ROOT/'docs/astra-city/LINEAR-TRACKING.md';tracking.write_text(tracking.read_text()+'\n## 6 October 2026 — '+label+' installed\n\n'+note)
    paths=[doc,previous,staged,published,Path(__file__).resolve(),
           ROOT/'docs/astra-city/model-integration-20260909'/published_batch,inventory,skill,tracking]
    if support_closure:paths += [support_closure,HERE/'test_auxiliary_commit_scope.py']
    paths += [ROOT/'3d-viewer'/patch['destination'] for patch in read(staged/'plan.json').get('topLevelTerrainPatches',[])]
    if result.get('recoveredPublishedBatch'):
        historical=read(previous/'historical-installed-proof.json')
        prior=(ROOT/historical['previousInstalledAcceptance']['path']).parent
        assert prior.name==published_batch and prior.parent==doc.parent
        paths += [prior,HERE/'accepted'/published_batch]
    paths += [ROOT/n for n in ['3d-viewer/city/data/building-progress.json','3d-viewer/city/data/manifest.json','3d-viewer/scripts/building-progress/review-proof.json','3d-viewer/scripts/building-progress/screening-proof.json','docs/astra-city/landmark-completion-audit/neon-snapshot.json','docs/astra-city/model-integration-20260909/current-source-review.json']]
    assert uids==['landsd/12854:0'], 'Exact cold-framed Tung Yip installation only'
    for key in ['installer-runner','browser-framing-runner']:
        paths.append(ROOT/result['evidence'][key]['path'])
    assert all(x.exists() and x.is_relative_to(ROOT) for x in paths)
    call(['git','add','--',*[str(x.relative_to(ROOT)) for x in paths]])
    call(['git','diff','--cached','--check'])
    call(['git','commit','-m','feat: install original '+label+' (HKS-203)'])
    if a.push:call(['git','push','origin',branch])
    print({'uids':uids,'newXLInstalled':new,'xlInstalled':done,'xlNotInstalled':352-done,'sourceGeometryChanges':0})
if __name__=='__main__':main()
