"""Bind exact source-to-podium face context for three unresolved originals."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-remaining-forty-contact-context-v1-20261021'
DOC=BASE/BATCH

def main():
    assert not DOC.exists()
    prior=BASE/'government-xl-remaining-forty-assembly-support-v1-20261021'
    _,pins=authenticate(prior)
    refs=[Path(__file__),prior/'result.json']
    for name in ['support-inputs.json','support-checks.json.gz']:
        p=prior/name
        assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
        refs.append(p)
    inputs=read(prior/'support-inputs.json')
    uids={'landsd/198440:0','landsd/314698:0','landsd/278458:0'}
    pairs=[p for p in inputs['pairs'] if p['uid'] in uids]
    alluids=uids|{p['supportUid']for p in pairs}
    for row in inputs['sources']:
        if row['uid'] in alluids:
            p=ROOT/row['candidate']['path']
            assert digest(p.read_bytes())==row['sourceSHA256']==pins[str(p.relative_to(ROOT))]
            refs.append(p)
    helper=HERE/'xl_remaining_forty_contact_context_v1_20261021.mjs'
    refs.extend([helper,HERE/'source-face-query.mjs',HERE/'triangle-point-index.mjs',ROOT/'3d-viewer/city/official-model-assets.js'])
    DOC.mkdir(parents=True)
    subprocess.run(['node',str(helper),str((DOC/'context.json').relative_to(ROOT))],cwd=ROOT,check=True)
    result=read(DOC/'context.json');result['uids']=sorted(uids)
    module('contact_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-support-face-context',refs,result)
    print({r['uid']:len(r['contacts'])for r in result['rows']},flush=True)

if __name__=='__main__':main()
