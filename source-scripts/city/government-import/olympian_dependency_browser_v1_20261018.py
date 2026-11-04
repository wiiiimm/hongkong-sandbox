"""Private original-source browser checks with exact reviewed support metadata."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module
import olympian_two_thirteen_private_browser_v2_20261018 as prior

def main():
    width = int(sys.argv[1])
    assert width in (390, 1280)
    batch = f'government-xl-olympian-dependency-browser-{width}-v1-20261018'
    doc, local = prior.BASE / batch, HERE / 'local' / batch
    assert not doc.exists() and not local.exists()
    names = [*prior.NAMES, 'government-xl-olympian-support-dependencies-v1-20261018']
    pins, refs = {}, [Path(__file__)]
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        for name in names:
            result_path = prior.BASE / name / 'result.json'
            result = read(result_path)
            assert connection.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (result['jobId'],)).fetchone() == ('complete', result)
            refs.append(result_path)
            for item in result['evidenceRefs']:
                assert item['path'] not in pins or pins[item['path']] == item['sha256']
                pins[item['path']] = item['sha256']
    for path, sha in pins.items():
        assert digest((ROOT / path).read_bytes()) == sha, path
    catalogue = read(prior.LOCAL / 'catalogue.json')
    entries = {entry['uid']: entry for entry in catalogue['models']}
    assert len(entries) == 13
    dependencies = read(prior.BASE / names[-1] / 'dependencies.json')['dependencies']
    assert len(dependencies) == 10
    for uid, entry in entries.items():
        assert not entry.get('publicationApproved') and not entry.get('placementReviewed')
        entry['supportDependencies'] = [dict(uid=provider, state='candidate', sha256=entries[provider]['sha256'], **({'csuid': entries[provider]['csuid']} if entries[provider].get('csuid') else {})) for provider in dependencies.get(uid, [])]
        source = prior.LOCAL / entry['asset']
        assert digest(source.read_bytes()) == entry['sha256']
        target = local / entry['asset']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    save(local / 'catalogue.json', catalogue)
    shutil.copyfile(prior.LOCAL / 'source-forms.json', local / 'source-forms.json')
    config = read(prior.LOCAL / 'browser-config.json')
    # Retained geometry and terrain are unchanged; repeat selected-source and
    # assembly residency checks for the new dependency metadata only.
    config.update(stage=str(local.relative_to(ROOT))+'/', doc=str(doc.relative_to(ROOT))+'/',
                  viewportWidths=[width], failureTestUids=[], skipRetainedVisits=True,
                  skipRetainedOwnViews=True)
    save(local / 'browser-config.json', config)
    doc.mkdir()
    tool = HERE / 'olympian_thirteen_assembly_browser_v7_20261018.mjs'
    command = ['node', str(tool), 'staged', str((local / 'browser-config.json').relative_to(ROOT))]
    with (doc / 'browser.log').open('w') as log:
        process = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                 env={**os.environ, 'CHROME_PATH':'/opt/google/chrome/chrome'}, timeout=900)
    save(doc / 'command.json', dict(command=command, exitCode=process.returncode, publication=False))
    for path, sha in pins.items():
        assert digest((ROOT / path).read_bytes()) == sha, path
    refs.extend([tool, *[ROOT / path for path in pins], *[path for path in local.rglob('*') if path.is_file()]])
    result = module('dependency_browser_freezer', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch, 'olympian-original-support-dependency-browser-v1', refs,
        dict(uids=list(entries), width=width, browserExitCode=process.returncode, fullAcceptance=False))
    print(result['jobId'], flush=True)

if __name__ == '__main__':
    main()
