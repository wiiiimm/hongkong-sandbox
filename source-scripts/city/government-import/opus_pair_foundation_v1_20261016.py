"""Capture both unchanged Opus sources against the private original terrain."""
from pathlib import Path
import subprocess,uuid,shutil
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-pair-foundation-v1-20261016';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PRIOR=BASE/'government-xl-opus-private-terrain-v2-20261016'
def main():
 assert not DOC.exists()and not LOCAL.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];refs.append(p)
 original=BASE/'government-xl-seven-new-original-closures-20261008/support-inputs.json';sources=[s for s in read(original)['sources']if s['uid']in ['landsd/322573:0','landsd/248432:0']];assert len(sources)==2;manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);tiles={x['id']:x['url']for x in m['tiles']};forms={}
 for s in sources:
  b=s['source']['building'];url=tiles[b['tile']];p=ROOT/'3d-viewer'/url;assert next(x for x in read(p)['buildings']if x['uid']==s['uid'])==b;s['source'].update(tile=url,tileSHA256=digest(p.read_bytes()));forms[s['uid']]=dict(tile=url,tileSHA256=digest(p.read_bytes()),building=b);asset=ROOT/s['candidate']['path'];assert digest(asset.read_bytes())==s['sourceSHA256']==s['candidate']['entry']['sha256'];refs += [p,asset]
 claim=reservations.claim('opus-compound-'+str(uuid.uuid4()),['building:'+s['uid']for s in sources],batch=BATCH,ttl=1800);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();LOCAL.mkdir(parents=True)
  for s in sources:
   p=LOCAL/s['candidate']['entry']['asset'];p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/s['candidate']['path'],p)
  save(LOCAL/'source-forms.json',forms);save(DOC/'selection.json.gz',dict(rows=sources,manifestSHA256=digest(manifest.read_bytes())));save(DOC/'terrain-candidates.json',read(PRIOR/'terrain-candidates.json'))
  tool=HERE/'acceptance-metrics-retained-group-parent.mjs'
  with(DOC/'worker.log').open('w')as log:subprocess.run(['node',str(tool),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900)
  metrics=read(DOC/'metrics.json');assert all(not r.get('error')for r in metrics['rows']);geometry=read(LOCAL/'runtime-geometry.json.gz')['rows'];helper=module('opus_pair_foundation',HERE/'xl-final-script-pass.py');tri=np.concatenate([np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for g in geometry]);ground=np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)for g in geometry]);polygon=shapely.union_all([Polygon(s['source']['building']['rings'][0],s['source']['building']['rings'][1:])for s in sources]);foundation=helper.foundation_context(tri,ground,polygon);summary=dict(foundation=foundation,metrics=metrics['rows'],sourceGeometryChanges=0,fullAcceptance=False)
  save(DOC/'summary.json',summary)
  for p,h in metrics['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  refs += [tool,original,LOCAL/'runtime-geometry.json.gz',HERE/'xl-final-script-pass.py',Path(helper.s.context.shared.__file__)]
  out=module('opus_pair_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'opus-two-original-source-runtime-compound-foundation-v1',list(dict.fromkeys(refs)),dict(uids=[s['uid']for s in sources],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],summary=summary),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
