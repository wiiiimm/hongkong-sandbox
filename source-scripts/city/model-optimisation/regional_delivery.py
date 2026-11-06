"""Run a source-bound regional compression delivery in dependent order.

Expected UIDs must match committed installed sources exactly before processing.
Completion produces unreviewed private variants and a read-back portable archive,
never approval or runtime publication.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import regional_batch as regional
import registry


def write_state(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False) as stream:
        stream.write(json.dumps(data,indent=2,allow_nan=False)+'\n');temporary=Path(stream.name)
    temporary.replace(path)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('scope','expected-uids','report','staging','recipes'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--batch',required=True);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    assert 1<=a.workers<=8
    paths=[a.scope,a.expected_uids,a.report,a.staging,a.recipes]
    assert all(path.resolve().is_relative_to(regional.ROOT) for path in paths)
    expected=registry.read(a.expected_uids)['uids'];assert expected and len(expected)==len(set(expected))
    assert not a.staging.exists() and not(a.report/'delivery-state.json').exists()
    here=Path(__file__).resolve().parent;snapshot=a.staging/'sources.json'
    steps=[('freeze',[sys.executable,here/'regional_batch.py','freeze','--source-root',regional.ROOT,'--scope',a.scope,'--output',a.staging]),
      ('process-four-tiers',[sys.executable,here/'regional_batch.py','launch','--snapshot',snapshot,'--recipes',a.recipes,'--output',a.staging,'--batch',a.batch,'--workers',a.workers]),
      ('independent-final-readback',[sys.executable,here/'summarise_regional_batch.py','--snapshot',snapshot,'--recipes',a.recipes,'--staging',a.staging,'--output',a.report,'--apply']),
      ('portable-member-readback',[sys.executable,here/'portable_regional_bundle.py','--report',a.report,'--recipes',a.recipes,'--output',a.report/'bundle'/(a.batch+'.tar.gz')])]
    completed=[]
    for phase,args in steps:
        write_state(a.report/'delivery-state.json',{'state':phase,'completed':completed,'published':False})
        subprocess.run([str(x) for x in args],cwd=regional.ROOT,check=True)
        if phase=='freeze':
            selected=registry.read(snapshot)['selected']
            assert len(selected)==len(expected) and {r['uid'] for r in selected}==set(expected),'Scope differs from the exact expected installed cohort; no processing started'
        completed.append(phase)
    summary=registry.read(a.report/'summary.json');bundle=registry.read(a.report/'portable-bundle.json')
    assert summary['models']==len(expected) and summary['variants']==4*len(expected) and summary['failedVariants']==0
    assert bundle['allMembersReadBackExactly'] and summary['published'] is False and bundle['published'] is False
    write_state(a.report/'delivery-state.json',{'state':'processing-complete-unreviewed','models':len(expected),'variants':4*len(expected),'completed':completed,'published':False})


if __name__=='__main__':main()
