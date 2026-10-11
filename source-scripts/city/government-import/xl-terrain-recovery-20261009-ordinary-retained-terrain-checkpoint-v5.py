"""Replay completed original terrain construction after a replacement-format guard.
Only repairs singular-vs-plural metadata in a fresh version; no terrain rebuild,
source change, neighbour waiver, threshold change or installation credit.
"""
import json,numpy as np
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect

def resume(resolution,prior):
 p=ROOT/prior;report=read(p/'result.json');assert read(p/'neon-sync.json')=={'jobId':report['jobId'],'resultVerified':True}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(report['jobId'],)).fetchone()==('complete',report)
 assert len(report['reasons'])==1 and 'acceptance-metrics-multi-retained.mjs' in report['reasons'][0]
 refs=report['evidenceRefs']
 for r in refs:assert digest((ROOT/r['path']).read_bytes())==r['sha256'],r
 selected=read(resolution.BASE/'check-selection.json.gz');old=read(p/'selection.json.gz');assert selected['manifestSHA256']==old['manifestSHA256']==digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())
 assert [r['uid'] for r in old['rows']]==resolution.UIDS
 for a,b in zip(selected['rows'],old['rows']):
  for key in ['sourceSHA256','source','native']:assert a[key]==b[key],key
 parent=read(p/'terrain-candidates.json');assert len(parent)==1 and len(parent[0]['replacesMany'])==1 and not parent[0].get('replaces')
 replacement=parent[0].pop('replacesMany')[0];assert [replacement['url']]==resolution.RETAIN_NATIVE_URLS
 assert digest((ROOT/'3d-viewer'/replacement['url']).read_bytes())==replacement['sha256']
 parent[0]['replaces']=replacement
 terrainpath=ROOT/parent[0]['path'];assert digest(terrainpath.read_bytes())==parent[0]['sha256']
 proof=read(p/'retained-native-proof.json');assert len(proof['parents'])==1 and proof['parents'][0]['supersededSHA256']==replacement['sha256']
 oldlocal=HERE/'local'/p.name
 for filename in ['catalogue.json','catalogue-index.json','source-forms.json']:
  dest=resolution.LOCAL/filename;dest.write_bytes((oldlocal/filename).read_bytes())
 for row in old['rows']:
  dest=resolution.LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];dest.write_bytes(raw)
 for f in p.iterdir():
  if f.name in ['result.json','neon-sync.json','guard-failure.json','owned-source-identity.json','terrain-candidates.json','terrain.json']:continue
  if f.is_file():(resolution.DOC/f.name).write_bytes(f.read_bytes())
 save(resolution.DOC/'selection.json.gz',old);save(resolution.DOC/'terrain-candidates.json',parent)
 n=read(p/'neighbour-inputs.json.gz');assert n['patches']==read(p/'terrain-candidates.json');n['patches']=parent;save(resolution.DOC/'neighbour-inputs.json.gz',n)
 t=read(p/'terrain.json');t['patch']=parent[0];save(resolution.DOC/'terrain.json',t)
 save(resolution.DOC/'construction-checkpoint.json',{'priorFencedResult':{'path':str((p/'result.json').relative_to(ROOT)),'sha256':digest((p/'result.json').read_bytes())},'completePriorEvidenceRefs':refs,'terrainPositionIndexAndBytesUnchanged':True,'oldMetadataContract':'single-row-replacesMany','freshMetadataContract':'replaces','modelGeometryChanges':0,'terrainGeometryChanges':0,'priorFailurePreserved':True,'publication':False})
 call=resolution.call;rel=resolution.rel;doc=resolution.DOC;local=resolution.LOCAL
 call(['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',rel(doc/'selection.json.gz'),'--candidates',rel(local),'--terrain-candidates',rel(doc/'terrain-candidates.json'),'--out',rel(doc/'metrics.json'),'--geometry-out',rel(local/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates_multi_retained.mjs'),'--candidates',rel(local),'--source-forms',rel(local/'source-forms.json'),'--terrain-candidates',rel(doc/'terrain-candidates.json'),'--out',rel(doc/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours-multi-retained.mjs'),rel(doc)+'/']);call(['node',str(HERE/'check-native-neighbours-multi-retained.mjs'),rel(doc)+'/'])
 final=resolution.module('ordinary_checkpoint_foundation','xl-final-script-pass.py');runtime={r['uid']:r for r in read(local/'runtime-geometry.json.gz')['rows']};foundations=[]
 for r in old['rows']:
  g=runtime[r['uid']];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);b=r['source']['building'];f=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]))
  foundations.append({'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'foundation':f,'strictFoundationAccepted':f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0})
 save(doc/'foundation.json',{'rows':foundations,'modelGeometryChanges':0})
