"""Commit/push only this completed installation and its authenticated evidence."""
from pathlib import Path
import subprocess
import sys
from run import ROOT, HERE, read, save, digest, connect

BATCH = 'government-xl-sheung-shui-original-installed-v1-20261020'
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
    assert result['fullXLCurrentCounts'] == dict(total=521, installedVerified=276, remaining=245)
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone() == ('complete', result)
        for uid, sha in result['sourceSHA256ByUid'].items():
            assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(result['snapshotId'],uid)).fetchone() == ('installed-verified',sha)
    pointer = read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
    assert pointer['snapshotId'] == result['snapshotId']
    assert read(DOC/'live-browser.json')['passed']
    live_review=read(DOC/'ROOT-LIVE-IMAGE-REVIEW.json')
    assert live_review['reviewer']=='Codex ROOT' and live_review['visualAcceptance'] and len(live_review['imagesActuallyViewed'])==4
    for image in live_review['imagesActuallyViewed']:assert digest((ROOT/image['path']).read_bytes())==image['sha256']
    paths = set()
    for item in result['evidenceRefs']:
        path = ROOT/item['path']
        assert path.resolve().is_relative_to(ROOT.resolve())
        assert digest(path.read_bytes()) == item['sha256'], item['path']
        paths.add(item['path'])
    paths.update(str(path.relative_to(ROOT)) for path in [DOC/'result.json',DOC/'neon-sync.json',Path(__file__)])
    paths.update(str(p.relative_to(ROOT))for p in [DOC/'README.md',DOC/'ROOT-LIVE-IMAGE-REVIEW.json',ROOT/'docs/astra-city/government-import/government-xl-next-five-resume-20261018/HANDOFF.md'])
    paths.discard(PROTECTED)
    # Historical evidence can mention old lease receipts. Authenticate their
    # bytes above, but never include lease tokens or private environment files
    # in a source-control commit.
    paths = {path for path in paths if not path.endswith('reservation.json')
             and '/local/' not in path
             and not any(part.startswith('.env') for part in Path(path).parts)}
    checked = subprocess.run(['git','check-ignore','-z','--stdin'],cwd=ROOT,input=('\0'.join(sorted(paths))+'\0').encode(),capture_output=True)
    assert checked.returncode in (0,1), checked.stderr
    paths -= set(checked.stdout.decode().rstrip('\0').split('\0'))
    assert all(not path.endswith('reservation.json') and not any(part.startswith('.env') for part in Path(path).parts) for path in paths)
    assert staged_before <= paths, 'Staged work outside the authenticated installation must remain untouched'
    pathspec = LOCAL/'commit-paths.nul'
    pathspec.write_bytes(('\0'.join(sorted(paths))+'\0').encode())
    git('add','--pathspec-from-file='+str(pathspec),'--pathspec-file-nul')
    staged = set(git('diff','--cached','--name-only','-z').decode().rstrip('\0').split('\0'))
    assert staged and staged <= paths and PROTECTED not in staged
    # Do not reformat the hash-bound third-party source capture. Authored
    # files and all other changes still receive the whitespace check.
    git('-c','core.whitespace=-blank-at-eof','diff','--cached','--check','--','.',
        ':(exclude)docs/astra-city/government-import/government-xl-olympian-two-primary-architect-v1-20261018/architect.html',
        ':(exclude)docs/astra-city/government-import/government-xl-olympian-two-primary-architect-v1-20261018/page-text.txt',
        ':(exclude)source-scripts/city/government-import/pacifica_original_towers_v2_20261019.py')
    message = LOCAL/'commit-message.txt'
    message.write_text('feat(city): install original Sheung Shui Slaughter House\n\nInstall the unchanged government slaughterhouse with validated native terrain.\nExact original stair and panel base interpretation and desktop/mobile checks recorded.\nXL coverage is 276/521. Original geometry and placement are unchanged.\n\nRefs: HKS-203\n')
    subprocess.run(['git','commit','-F',str(message)],cwd=ROOT,check=True)
    commit = git('rev-parse','HEAD').decode().strip()
    subprocess.run(['git','push','origin','HEAD:refs/heads/'+BRANCH],cwd=ROOT,check=True)
    remote = git('ls-remote','origin','refs/heads/'+BRANCH).decode().split()[0]
    assert remote == commit
    save(LOCAL/'commit-push-receipt.json',dict(commit=commit,branch=BRANCH,remoteVerified=True,installedJobId=result['jobId']))
    print(dict(commit=commit,branch=BRANCH,remoteVerified=True),flush=True)

if __name__ == '__main__': main()
