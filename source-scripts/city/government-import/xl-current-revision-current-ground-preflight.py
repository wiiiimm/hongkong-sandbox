"""Full unchanged-current-ground checks for an explicit freshly receipted original.

No terrain is replaced. No installed-support exception is applied. Full contact/foundation, all physical/runtime and neighbour gates
remain mandatory; this runner never installs or grants progress credit.
"""
import argparse,importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect
from government_georef_cell_identity import verify_files,POLICY
from terrain_source_preflight import preflight,SourceSheetIndex
from terrain_diagnostic_resolution import resolve_global_bottom_warning

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def owned(a,doc,local):
 lease=read(local/'reservation.json');assert reservations.owns(lease)
 BASE=(ROOT/a.base).resolve();assert BASE.is_relative_to(ROOT/'docs/astra-city/government-import')
 row=next(r for r in read(BASE/'check-selection.json.gz')['rows'] if r['uid']==a.uid)
 context=next(r for r in read(BASE/'context.json.gz')['rows'] if r['uid']==a.uid)
 with connect() as con:
  con.execute('SET TRANSACTION READ ONLY')
  from native_source_receipt import verify
  assert row['native'].get('revisionAcquisition')
  verify(con,row)
  assert row['currentReview'] is None
  assert con.execute('SELECT 1 FROM astra_modelling.model_reviews WHERE uid=%s LIMIT 1',(a.uid,)).fetchone() is None
  retained={'uid':a.uid,'sourceSHA256':row['sourceSHA256'],'noExistingReview':True}
 save(doc/'unreviewed-source-continuation.json',{'current':retained,'pinned':row['currentReview'],'publication':False})
 assert digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())==row['source']['tileSHA256']
 for tile,sha in context['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
 positive=verify_files(row,context,local/'identity-current');assert positive['passed'],positive['reasons']
 save(doc/'owned-source-identity.json',positive);save(doc/'owned-source-identity-contact.json',positive)
 index=ROOT/'source-scripts/city/landmark-acquisition/index.json';routing=preflight(row,context,SourceSheetIndex(read(index)))
 routing['legacyProjectionIdentity']=routing['identity'];routing['identity']={'passed':True,'proof':positive['proof'],'reasons':[],'method':POLICY}
 routing['canStartTerrainWork']=routing['primarySheetIntersects'];assert routing['canStartTerrainWork']
 routing['inputHashes']={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [index,BASE/'context.json.gz',Path(__file__),HERE/'xl-current-revision-terrain-continuation.py',HERE/'native_source_receipt.py',HERE/'government_georef_cell_identity.py']}
 save(doc/'indexed-preflight.json',routing)
 raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
 dest=local/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);row['candidate']['path']=str(dest.relative_to(ROOT))
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path);manifest_sha=digest(manifest_path.read_bytes())
 assert not any(m['uid']==a.uid for u in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models'])
 catalogue=read(HERE/'accepted/government-xxl-20260911/catalogue.json');catalogue.update(area=a.batch,models=[row['candidate']['entry']],counts={'packedModels':1})
 save(local/'catalogue.json',catalogue);save(local/'catalogue-index.json',{'models':1,'catalogues':['catalogue.json']});save(local/'source-forms.json',{a.uid:row['source']})
 save(doc/'selection.json.gz',{'rows':[row],'batch':a.batch,'manifestSHA256':manifest_sha})
 save(doc/'terrain-candidates.json',[]);save(doc/'terrain.json',{'patches':[],'sourceFiles':[],'modelGeometryChanges':0,'terrainGeometryChanges':0})
 save(doc/'existing-terrain-only.json',{'manifestSHA256':manifest_sha,'qualification':'Unchanged current rendered terrain only. Every original contact, whole foundation, neighbour and runtime gate required; no installed-support exception.'})
 final=module('current_support_foundation','xl-final-script-pass.py');lo,hi=row['native']['model']['worldBounds'];neighbours=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);native={e['uid'] for u in manifest['officialModelCatalogues'] for e in read(ROOT/'3d-viewer'/u)['models']}
 save(doc/'neighbour-inputs.json.gz',{'rows':[{'building':b,'patchIndexes':[],'existingNative':b['uid'] in native or bool(b.get('modelGeometry'))} for b,_,_ in neighbours],
  'inputHashes':{str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in neighbours},'candidateIds':[a.uid],'patches':[]})
 rel=lambda p:str(p.relative_to(ROOT))
 def call(command,allowed=(0,)):
  assert subprocess.run(command,cwd=ROOT).returncode in allowed;assert reservations.owns(lease)
 call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(doc/'selection.json.gz'),'--candidates',rel(local),'--terrain-candidates',rel(doc/'terrain-candidates.json'),'--out',rel(doc/'metrics.json'),'--geometry-out',rel(local/'runtime-geometry.json.gz')])
 call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(local),'--source-forms',rel(local/'source-forms.json'),'--terrain-candidates',rel(doc/'terrain-candidates.json'),'--out',rel(doc/'validation.json')],(0,1))
 call(['node',str(HERE/'check-neighbours.mjs'),rel(doc)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(doc)+'/'])
 geom=read(local/'runtime-geometry.json.gz')['rows'][0];triangles=np.asarray(geom['position']).reshape(-1,3)[np.asarray(geom['index']).reshape(-1,3)];ground=np.asarray(geom['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building']
 foundation=final.foundation_context(triangles,ground,Polygon(b['rings'][0],b['rings'][1:]))
 f={'uid':a.uid,'sourceSHA256':row['sourceSHA256'],'foundation':foundation,'strictFoundationAccepted':foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0};save(doc/'foundation.json',{'rows':[f],'modelGeometryChanges':0})
 save(doc/'identity-proof.json',{'uid':a.uid,'sourceSHA256':row['sourceSHA256'],'proof':positive['proof'],'method':POLICY,'ownedSourceProofSHA256':digest((doc/'owned-source-identity.json').read_bytes()),'preflightSHA256':digest((doc/'indexed-preflight.json').read_bytes())})
 metrics=read(doc/'metrics.json');diagnostic=resolve_global_bottom_warning(read(doc/'validation.json')['results'][0],metrics['rows'][0],f);save(doc/'diagnostic-resolution.json',diagnostic)
 reasons=module('current_support_policy','acceptance-policy.py').reasons({'state':'runtime-validated-awaiting-acceptance','sourceSHA256':row['sourceSHA256'],'identityProof':positive['proof']},metrics['rows'][0],metrics['profiles']['mobile'])
 reasons+=diagnostic['remaining']
 if not f['strictFoundationAccepted']:reasons.append('whole-source-foundation')
 for path,sha in metrics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 assert digest(manifest_path.read_bytes())==manifest_sha
 assert all(not x['reasons'] and x['maxGroundChange']==0 for x in read(doc/'neighbour-checks.json')['rows'])
 native_checks=read(doc/'native-neighbour-checks.json');assert not set(native_checks['blocked'])-set(native_checks['resolved'])
 module('current_revision_fenced','xl-current-revision-terrain-continuation.py').finish(a,row,doc,local,reasons)

def main():
 p=argparse.ArgumentParser();p.add_argument('--uid',required=True);p.add_argument('--batch',required=True);p.add_argument('--base',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args();assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
 doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
 if a.owned:
  from publication_lock import locked_publication
  with locked_publication(ROOT):owned(a,doc,local)
  return
 assert not doc.exists(),'Fresh full current support proof only'
 BASE=(ROOT/a.base).resolve();assert BASE.is_relative_to(ROOT/'docs/astra-city/government-import')
 assert a.uid in {r['uid'] for r in read(BASE/'check-selection.json.gz')['rows']}
 claim=reservations.claim('codex-xl-current-provisional-support-'+str(uuid.uuid4()),['building:'+a.uid],batch=a.batch);assert claim['ok'],claim
 save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
