"""Read-only complete production attributes for seven unchanged YOHO originals."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-seven-runtime-capture-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-yoho-seven-private-terrain-v1-20261020'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
assert not DOC.exists();receipt=read(SRC/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};sel=SRC/'selection.json.gz';assert ref(sel)['sha256']==pins[str(sel.relative_to(ROOT))]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
rows=read(sel)['rows'];assert len(rows)==7;mp=ROOT/'3d-viewer/city/data/manifest.json';mh=ref(mp);refs=[Path(__file__),SRC/'result.json',sel,mp]
for r in rows:
 asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
 tile=ROOT/'3d-viewer'/r['source']['tile'];assert next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building'];refs.append(tile)
save(DOC/'input.json.gz',dict(currentManifest=mh,currentCatalogueRefs=[ref(ROOT/'3d-viewer'/url)for url in read(mp)['officialModelCatalogues']],evidenceRefs=[ref(sel)],rows=[dict(uid=r['uid'],entry=r['candidate']['entry'],building=r['source']['building'],path=r['candidate']['path'])for r in rows]))
tool=HERE/'yoho_seven_actual_attributes_v1_20261020.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
capture=read(DOC/'attributes.json.gz');assert capture['startEndAllInputsVerified']and ref(mp)==mh
for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
assert sum(len(r['completeOriginalIndex'])//3 for r in capture['rows'])==83161
module('yoho_seven_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-original-production-renderer-attributes',list(dict.fromkeys(refs)),dict(uids=sorted(r['uid']for r in rows),completeFaces=83161,representations=['literal','explicitLeftF32','explicitBalancedF32'],sourceGeometryChanges=0,installationApproved=False))
