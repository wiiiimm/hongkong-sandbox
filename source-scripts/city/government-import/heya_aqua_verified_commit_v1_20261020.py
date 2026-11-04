"""Commit/push only this completed installation and its authenticated evidence."""
from pathlib import Path
import subprocess
import sys
from run import ROOT, HERE, read, save, digest, connect

BATCH = 'government-xl-heya-aqua-original-installed-v1-20261020'
DOC = ROOT/'docs/astra-city/government-import'/BATCH
LOCAL = HERE/'local'/BATCH
BRANCH = 'codex/astra-hong-kong-city'
PROTECTED = 'docs/astra-city/government-import/government-xl-safe-boundary-recovery-sequence-20261006/working-commands.json'

def git(*args, **kwargs):
    return subprocess.check_output(['git', *args], cwd=ROOT, **kwargs)

def main():
    assert git('branch','--show-current').decode().strip() == BRANCH
    staged_before = set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
    assert not staged_before or sys.argv[1:] == ['--resume-staged'], 'Pre-existing staged work must remain untouched'
    result = read(DOC/'result.json')
    assert result['publication'] and result['newlyInstalled'] == 1
    assert result['fullXLCurrentCounts'] == dict(total=521, installedVerified=292, remaining=229)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone() == ('complete', result)
        for uid, sha in result['sourceSHA256ByUid'].items():
            assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(result['snapshotId'],uid)).fetchone() == ('installed-verified',sha)
    pointer = read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
    assert pointer['snapshotId'] == result['snapshotId']
    assert read(DOC/'live-browser.json')['passed']
    live_review=read(DOC/'ROOT-LIVE-IMAGE-REVIEW.json')
    assert live_review['reviewer']=='Codex ROOT' and live_review['visualAcceptance'] and len(live_review['imagesActuallyViewed'])==8
    for image in live_review['imagesActuallyViewed']:assert digest((ROOT/image['path']).read_bytes())==image['sha256']
    paths = set()
    for item in result['evidenceRefs']:
        path = ROOT/item['path']
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert digest(path.read_bytes()) == item['sha256'], item['path']
        paths.add(item['path'])
    paths.update(str(path.relative_to(ROOT)) for path in [DOC/'result.json',DOC/'neon-sync.json',Path(__file__)])
    paths.update(str(p.relative_to(ROOT))for p in [DOC/'README.md',DOC/'ROOT-LIVE-IMAGE-REVIEW.json',ROOT/'docs/astra-city/government-import/government-xl-next-five-resume-20261018/HANDOFF.md'])
    for name in ['heya_aqua_joint_browser_v1_20261020.py','heya_aqua_joint_browser_v1_20261020.mjs','heya_aqua_joint_browser_v2_20261020.py','heya_aqua_joint_browser_v3_20261020.py','heya_aqua_joint_browser_v3_20261020.mjs','heya_aqua_joint_browser_v4_20261020.py','heya_aqua_joint_browser_v4_20261020.mjs','heya_aqua_wall_adjacency_v1_20261020.py','heya_aqua_render_contacts_v1_20261020.py','heya_aqua_physical_review_v1_20261020.py','heya_aqua_current_applicability_v1_20261020.py','heya_aqua_current_applicability_v2_20261020.py','heya_aqua_neighbour_attributes_v1_20261020.mjs','heya_aqua_neighbour_attributes_v2_20261020.mjs','heya_aqua_neighbour_clearance_v1_20261020.py','heya_aqua_neighbour_clearance_v2_20261020.py','heya_aqua_publication_plan_v1_20261020.py','heya_aqua_live_install_v1_20261020.py']:
        paths.add(str((HERE/name).relative_to(ROOT)))
    for name in ['joint-browser-v1','joint-browser-v2','joint-browser-v4','wall-adjacency-v1','render-contacts-v1','physical-review-v1','current-applicability-v2','neighbour-clearance-v2','qualified-publication-plan-v1']:
        folder=DOC.parent/('government-xl-heya-aqua-'+name+'-20261020')
        receipt=read(folder/'result.json')
        for item in receipt['evidenceRefs']:
            p=ROOT/item['path']
            if p.is_relative_to(folder):assert digest(p.read_bytes())==item['sha256'];paths.add(item['path'])
        paths.update(str(p.relative_to(ROOT))for p in [folder/'result.json',folder/'neon-sync.json'])
    paths.discard(PROTECTED)
    # Historical evidence can mention old lease receipts. Authenticate their
    # bytes above, but never include lease tokens or private environment files
    # in a source-control commit.
    paths = {path for path in paths if Path(path).name!='reservation.json'
             and '/local/' not in path
             and not any(part.startswith('.env') for part in Path(path).parts)}
    checked = subprocess.run(['git','check-ignore','-z','--stdin'],cwd=ROOT,input=('\0'.join(sorted(paths))+'\0').encode(),capture_output=True)
    assert checked.returncode in (0,1), checked.stderr
    paths -= set(checked.stdout.decode().rstrip('\0').split('\0'))
    assert all(Path(path).name!='reservation.json' and not any(part.startswith('.env') for part in Path(path).parts) for path in paths)
    assert staged_before <= paths, 'Staged work outside the authenticated installation must remain untouched'
    pathspec = LOCAL/'commit-paths.nul'
    pathspec.write_bytes(('\0'.join(sorted(paths))+'\0').encode())
    git('add','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul')
    staged = set(git('diff','--cached','--name-only','-z').decode().rstrip('\0').split('\0'))
    assert staged and staged <= paths and PROTECTED not in staged
    # Do not reformat hash-bound completed producers (two blank lines) or source captures. Authored
    # files and all other changes still receive the whitespace check.
    git('-c','core.whitespace=-blank-at-eof,-blank-at-eol','diff','--cached','--check','--','.',
        ':(exclude)docs/astra-city/government-import/government-xl-olympian-two-primary-architect-v1-20261018/architect.html',
        ':(exclude)docs/astra-city/government-import/government-xl-olympian-two-primary-architect-v1-20261018/page-text.txt',
        ':(exclude)source-scripts/city/government-import/pacifica_original_towers_v2_20261019.py',
        ':(exclude)source-scripts/city/government-import/star_house_pair_loader_v1_20261020.py',
        ':(exclude)source-scripts/city/government-import/yoho_seven_loader_v1_20261020.py',
        ':(exclude)source-scripts/city/government-import/star_house_podium_loader_v1_20261020.py',
        ':(exclude)source-scripts/city/government-import/parkview_two_loader_v1_20261020.py',
        ':(exclude)source-scripts/city/government-import/parkview5_loader_v1_20261020.py',
        ':(exclude)source-scripts/city/government-import/yoho_seven_loader_v1_20261020.py')
    message = LOCAL/'commit-message.txt'
    message.write_text('feat(city): install original Heya Aqua Tower 2\n\nInstall one unchanged government tower using its verified original podium. Exact identity, source-specific wall joint, four-mode foundations and neighbour separation, and live desktop/mobile recovery verified. No retained model or terrain edits.\nXL coverage292/521; detailed catalogue6782. No AI geometry modelling.\n\nRefs: HKS-203\n')
    subprocess.run(['git','commit','-F',str(message)],cwd=ROOT,check=True)
    commit = git('rev-parse','HEAD').decode().strip()
    subprocess.run(['git','push','origin','HEAD:refs/heads/'+BRANCH],cwd=ROOT,check=True)
    remote = git('ls-remote','origin','refs/heads/'+BRANCH).decode().split()[0]
    assert remote == commit
    save(LOCAL/'commit-push-receipt.json',dict(commit=commit,branch=BRANCH,remoteVerified=True,installedJobId=result['jobId']))
    print(dict(commit=commit,branch=BRANCH,remoteVerified=True),flush=True)

if __name__ == '__main__': main()
