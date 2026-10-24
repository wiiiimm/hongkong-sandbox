"""Preserve complete mobile live verification from an interrupted transaction."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-harbourfront-tower-original-installed-v3-20261021';BATCH='government-xl-harbourfront-live-mobile-checkpoint-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();assert not reservations.owns(read(HERE/'local'/OLD.name/'reservation.json'))
h=read(OLD/'historical-input-context.json');refs=[Path(__file__),OLD/'historical-input-context.json',OLD/'acceptance.json',OLD/'supervisor-recovery.json']
for r in h['mutableCurrentByteSnapshots']:assert digest((ROOT/r['originalPath']).read_bytes())==r['originalSHA256']
for q in h['originalEvidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
r=read(OLD/'390/live-browser.json');assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==2
for v in views:assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']=='landsd/118230:0'
assert any(v.get('phase')=='failed-download'and v['fallbackRetained']for v in r['views'])
refs.extend(p for p in (OLD/'390').rglob('*')if p.is_file())
plan=BASE/'government-xl-harbourfront-tower-qualified-publication-plan-v1-20261021/publication-plan.json';refs.append(plan)
result=dict(uids=['landsd/118230:0'],mobilePassed=True,desktopPassed=False,installationApproved=False,newlyInstalled=0,planSHA256=digest(plan.read_bytes()),preInstallSnapshot=h['preInstallSnapshot'],qualification='Complete mobile live report retained after supervisor termination. Exact original preinstall bytes restored and all prior input refs revalidated. Reuse only for byte-identical publication plan and same input refs; desktop completion and ledger publication remain required.')
save(DOC/'summary.json',result);module('hf_mobile_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'completed-live-mobile-verification-checkpoint',refs,result)
