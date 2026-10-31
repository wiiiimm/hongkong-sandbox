"""Exact original tower/podium relationship diagnostic, not identity approval."""
from pathlib import Path
import numpy as np,subprocess
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-original-podium-contacts-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-next-twenty-current-terrain-v2-20261020';UID='landsd/300857:0';POD='landsd/301636:0'
assert not DOC.exists();receipt=read(SRC/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};sel=SRC/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))];refs=[Path(__file__),SRC/'result.json',sel];worlds={};bindings=[]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in read(sel)['rows']:
  if r['uid']not in [UID,POD]:continue
  assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['native']['cacheKey'],)).fetchone()==(r['native']['resultSha'],)
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);t=decode_original_world_triangles(p.read_bytes());worlds[r['uid']]=t;bindings.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],nativeStageKey=r['native']['cacheKey'],nativeStageSHA256=r['native']['resultSha']))
assert set(worlds)=={UID,POD}
def geom(t):return dict(position=t.reshape(-1).tolist(),index=list(range(t.size//3)))
save(DOC/'input.json.gz',dict(rows=[dict(uid=UID,mode='original',source=geom(worlds[UID]),support=geom(worlds[POD]),sourceWorldSHA256=digest(worlds[UID].tobytes()),supportWorldSHA256=digest(worlds[POD].tobytes()))]));save(DOC/'source-bindings.json',dict(bindings=bindings,proposedSupportUid=POD,identityApproval=False))
tool=HERE/'parkview-three-four-world-contacts-v1-20261020.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'contacts.json.gz').relative_to(ROOT))],cwd=ROOT,check=True);report=read(DOC/'contacts.json.gz');summary=[{k:v for k,v in r.items()if k not in ['mapped','rawInterface']}for r in report['rows']]
for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('yoho_podium_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-podium-source-contacts',list(dict.fromkeys(refs)),dict(uids=[UID,POD],rows=summary,installationApproved=False))
