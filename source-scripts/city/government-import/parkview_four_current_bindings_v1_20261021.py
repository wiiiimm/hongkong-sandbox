"""Bind whole-source four-world representations and contact witnesses to current candidate."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-four-current-bindings-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
def take(n,p):
 _,ps=authenticate(BASE/n)
 for k,v in ps.items():assert k not in pins or pins[k]==v;pins[k]=v
 assert digest(p.read_bytes())==ps[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
cap='government-xl-parkview-12-15-shared-runtime-v1-20261021';selection=take(cap,BASE/cap/'selection.json.gz');runtime=take(cap,HERE/'local'/cap/'runtime-geometry.json.gz');attr='government-xl-parkview-12-15-actual-render-attributes-v1-20261021';attributes=take(attr,BASE/attr/'attributes.json.gz');sup='government-xl-parkview-12-15-shared-support-v1-20261021';support=take(sup,BASE/sup/'support-checks.json.gz');foundation=take(sup,BASE/sup/'summary.json');contacts=[]
for n in ['government-xl-parkview-13-14-four-world-contacts-v1-20261021','government-xl-parkview-12-15-four-world-contacts-v1-20261021']:contacts+=take(n,BASE/n/'contacts.json.gz')['rows']
summary=[]
for r in selection['rows']:
 uid=r['uid'];p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);original=decode_original_world_triangles(p.read_bytes());rt=next(x for x in runtime['rows']if x['uid']==uid);current=np.asarray(rt['position'],dtype='<f8').reshape(-1,3)[np.asarray(rt['index']).reshape(-1,3)];assert np.array_equal(original,current)
 a=next(x for x in attributes['rows']if x['uid']==uid);idx=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
 for key in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:assert np.array_equal(np.asarray(a[key],dtype='<f8').reshape(-1,3)[idx],current)
 row=dict(uid=uid,sourceSHA256=r['sourceSHA256'],completeFaces=len(current),worldSHA256=digest(current.tobytes()),allFourCompleteWorldsIdentical=True)
 if uid!='landsd/254491:0':
  interface=next(x for x in support['rows']if x['uid']==uid)['interface'];matched=[x for x in contacts if x['uid']==uid];assert {x['mode']for x in matched}=={'original','literal','explicitLeftF32','explicitBalancedF32'}
  for c in matched:assert c['rawInterface']==interface and c['sourceWorldSHA256']==row['worldSHA256']
  f=next(x for x in foundation['rows']if x['uid']==uid);row.update(exactCurrentContactWitnessListsMatch=True,rawCanonicalPassed=interface['passed'],rawUnresolved=len(interface['unresolved']),currentFoundation=f['foundation'],drawnGroundSHA256=digest(np.asarray(rt['drawnGroundGeometry'],dtype='<f8').tobytes()))
 summary.append(row)
manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
result=dict(uids=[r['uid']for r in summary],rows=summary,installationApproved=False,physicalReviewApproved=False,qualification='Exact complete coordinate equality binds the existing whole-source foundation measurements and unchanged current contact witness lists to all four representations. Raw failures remain failures; this adds no interpretation or acceptance.')
save(DOC/'bindings.json.gz',result);module('parkview_current_binding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-source-four-world-and-current-contact-binding',refs,result);print({k:v for k,v in result.items()if k!='rows'},flush=True)
