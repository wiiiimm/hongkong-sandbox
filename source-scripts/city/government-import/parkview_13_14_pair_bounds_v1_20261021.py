"""Measure existing compound limits without inventing a tower-on-tower interface."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_assembly_diagnostic import evaluate
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-13-14-pair-bounds-v1-20261021';DOC=BASE/BATCH;UIDS={'landsd/253980:0','landsd/255260:0'};refs=[Path(__file__)]
assert not DOC.exists()
def take(n,f):
 _,ps=authenticate(BASE/n);p=BASE/n/f;assert digest(p.read_bytes())==ps[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
n='government-xl-parkview-four-raw-identity-v1-20261021';selected=take(n,'selection.json.gz');rows=[r for r in selected['rows']if r['uid']in UIDS];assert len(rows)==2;individual={r['uid']:take(n,r['uid'].split('/')[1]+'-identity.json')for r in rows};world={};forms={};final=module('parkview_pair_current_forms',HERE/'xl-final-script-pass.py')
for r in rows:
 p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);t=decode_original_world_triangles(p.read_bytes());world[r['uid']]=t;lo,hi=t.min((0,1)),t.max((0,1))
 for b,_,url in final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]):forms[b['uid']]=b;refs.append(ROOT/'3d-viewer'/url)
support=take('government-xl-parkview-12-15-shared-support-v2-20261021','support-checks.json.gz');actual=next(r for r in support['rows']if r['uid']=='landsd/253980:0');assert actual['supportUid']=='landsd/254491:0'
result=evaluate(rows,individual,world,actual,list(forms.values()),tower='landsd/253980:0',podium='landsd/255260:0');assert not result['passed'];save(DOC/'raw-compound.json',result);summary=dict(uids=sorted(UIDS),measures=result['measures'],rawReasons=result['reasons'],actualSupportUid=actual['supportUid'],identityApproved=False,installationApproved=False,qualification='Both candidates are towers on the installed podium, not a tower/podium pair. The raw predicate and all failures remain; numeric compound bounds are measured without a fabricated interface.');save(DOC/'summary.json',summary);refs.extend(HERE/x for x in ['original_source_assembly_diagnostic.py','xl-final-script-pass.py','exact_packed_world_geometry_20261009.py']);module('parkview_pair_bounds_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'actual-original-pair-compound-bound-diagnostic',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
