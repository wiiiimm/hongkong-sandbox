"""Complete literal-runtime original assembly support and foundation diagnostics."""
from pathlib import Path
import subprocess,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-seven-support-v1-20261020';DOC=BASE/BATCH;CAP=BASE/'government-xl-yoho-seven-private-terrain-v1-20261020';POD='landsd/301636:0'
assert not DOC.exists();r=read(CAP/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),CAP/'result.json']
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
p=HERE/'local'/CAP.name/'runtime-geometry.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);rows=read(p)['rows'];sel=CAP/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))];refs.append(sel);buildings={x['uid']:x['source']['building']for x in read(sel)['rows']};world={x['uid']:np.asarray(x['position'],dtype='<f8').reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)]for x in rows};podium=world[POD]
save(DOC/'input.json.gz',dict(rows=[x for x in rows if x['uid']!=POD],podium=podium.tolist()));tool=HERE/'wave_retained_basic_support_v1_20261017.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);support=read(DOC/'support.json.gz');final=module('yoho_seven_foundation',HERE/'xl-final-script-pass.py');summary=[]
for x in rows:
 uid=x['uid'];ground=np.asarray(x['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);sup=np.concatenate([ground,podium])if uid!=POD else ground;b=buildings[uid];foundation=final.foundation_context(world[uid],sup,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/(uid.split('/')[1]+'-foundation.json'),foundation);contact=next((y['proof']for y in support['rows']if y['uid']==uid),None);line=dict(uid=uid,faces=len(world[uid]),completeFoundationFaces=foundation['completeTerrainTriangles'],buriedFaces=foundation['fullyBuriedTriangles'],buriedUpwardFaces=foundation['fullyBuriedUpwardTriangles'],supportPassed=contact['passed']if contact else None,unresolvedSamples=len(contact['unresolved'])if contact else None);summary.append(line);print(line,flush=True)
for p,h in support['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
refs.extend([tool,HERE/'xl-final-script-pass.py']);module('yoho_seven_support_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-original-literal-runtime-support',refs,dict(uids=list(world),rows=summary,installationApproved=False))
