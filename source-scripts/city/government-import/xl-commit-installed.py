"""Commit one actually verified XL installation after coordinator image inspection.

Exact source-specific paths only; no broad staging, model processing or approval
inference. Current snapshot, source bytes, receipts, Neon and goal counts must agree.
"""
import argparse, re, subprocess
from pathlib import Path
from run import ROOT, HERE, read, digest, connect

def call(command):
    subprocess.run(command,cwd=ROOT,check=True)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True,help='Exact installed evidence directory within government-import')
    p.add_argument('--browser-inspected',action='store_true',required=True,help='Coordinator has viewed the exported live browser image')
    p.add_argument('--push',action='store_true')
    a=p.parse_args();doc=(ROOT/a.source).resolve()
    assert doc.parent==ROOT/'docs/astra-city/government-import' and doc.name.startswith('government-xl-')
    assert not (doc/'README.md').exists(),'Do not rewrite a completed installation note'
    branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    assert branch=='codex/astra-hong-kong-city','Only the explicitly authorised non-main branch'
    assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).strip(),'Never combine with pre-existing staging'
    result=read(doc/'result.json');assert result['passed'] and result['newlyInstalled']==1 and len(result['installedUids'])==1
    assert result['publication'] and result['modelGeometryChanges']==result['scriptExternalAICalls']==0 and not result['failures']
    uid=result['installedUids'][0];assert result['uids']==[uid]
    assert read(doc/'neon-sync.json')=={'installedUids':[uid],'jobId':result['jobId'],'resultVerified':True,'snapshotId':result['snapshotId']}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    for ref in [*result['evidenceRefs'],*result['evidence'].values()]:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    previous=(ROOT/result['evidence']['result']['path']).parent
    assert previous.parent==doc.parent and read(previous/'result.json')['uid']==uid
    pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json');assert pointer['snapshotId']==result['snapshotId']
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert digest((ROOT/result['manifest']['path']).read_bytes())==result['manifest']['sha256']
    models=[m for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']]
    actual=[m for m in models if m['uid']==uid];assert len(actual)==1 and actual[0]['sha256']==result['sourceSHA256']
    inventory=ROOT/pointer['inventory'];assert inventory.exists()
    staged=HERE/'accepted'/doc.name;catalogue=read(staged/'catalogue.json');assert [m['uid'] for m in catalogue['models']]==[uid]
    model=catalogue['models'][0];assert digest((staged/model['asset']).read_bytes())==result['sourceSHA256']
    published=ROOT/'3d-viewer/city/data/official-models'/doc.name;assert digest((published/model['asset']).read_bytes())==result['sourceSHA256']
    xl={r['uid'] for r in read(ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923/selection.json.gz')['rows']};assert len(xl)==352 and uid in xl
    done=len(xl & {m['uid'] for m in models});new=done-44;assert 1<=new<=308
    progress=read(ROOT/'3d-viewer/city/data/building-progress.json');assert progress==result['progress']
    label=model.get('label') or uid;token=uid.split('/')[1].replace(':','-')
    note=(f'Codex, 6 October 2026. {label} ({uid}) is installed with unchanged original government geometry. '
          f'Verified Neon job `{result["jobId"]}`, installed snapshot `{result["snapshotId"]}`, source SHA `{result["sourceSHA256"]}`. '
          'Complete original source identity/contact/foundation/basic/native/runtime and guarded publication pass. '
          'Staged/live desktop/mobile day/night, picking/collision and failed-load/retry pass; exported live mobile PNG inspected by coordinator. '
          'Zero model geometry edits or architectural/model AI calls. No historical Lantau imagery used.\n\n'
          f'{new} new XL installations from44/308: **{done} installed / {352-done} not installed**, {max(0,100-new)} further installations required. '
          f'Public counters: {progress["totalForms"]:,} total source forms, {progress["breakdown"]["enhanced"]:,} enhanced, '
          f'{progress["government"]["enhanced"]:,} / {progress["government"]["available"]:,} government matches installed. '
          'Queued/running rows remain In process. Commits and reports are checkpoints; the active goal continues.\n')
    (doc/'README.md').write_text('# '+label+' — verified original installation\n\n'+note)
    skill=ROOT/'.agents/skills/hong-kong-model-improvement/SKILL.md';s=skill.read_text()
    match=re.search(r'version: "(\d+)\.(\d+)\.(\d+)"',s);assert match
    version=f'{match[1]}.{match[2]}.{int(match[3])+1}'
    skill.write_text(s.replace(match[0],f'version: "{version}"',1)+'\n## Latest actual XL installation checkpoint\n\n'+note)
    tracking=ROOT/'docs/astra-city/LINEAR-TRACKING.md';tracking.write_text(tracking.read_text()+'\n## 6 October 2026 — '+label+' installed\n\n'+note)
    paths=[doc,previous,staged,published,ROOT/f'3d-viewer/city/data/government-native-{token}.json',
           ROOT/'docs/astra-city/model-integration-20260909'/doc.name,inventory,skill,tracking]
    paths += [ROOT/n for n in ['3d-viewer/city/data/building-progress.json','3d-viewer/city/data/manifest.json','3d-viewer/scripts/building-progress/review-proof.json','3d-viewer/scripts/building-progress/screening-proof.json','docs/astra-city/landmark-completion-audit/neon-snapshot.json','docs/astra-city/model-integration-20260909/current-source-review.json']]
    assert all(x.exists() and x.is_relative_to(ROOT) for x in paths)
    call(['git','add','--',*[str(x.relative_to(ROOT)) for x in paths]])
    call(['git','diff','--cached','--check'])
    call(['git','commit','-m','feat: install original '+label+' (HKS-203)'])
    if a.push:call(['git','push','origin',branch])
    print({'uid':uid,'newXLInstalled':new,'xlInstalled':done,'xlNotInstalled':352-done,'sourceGeometryChanges':0})
if __name__=='__main__':main()
