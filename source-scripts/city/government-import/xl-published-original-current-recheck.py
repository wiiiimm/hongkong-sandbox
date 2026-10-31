"""Fresh full checks for an exactly published original with a verified historical installed receipt."""
import argparse,importlib.util,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from terrain_diagnostic_resolution import resolve_global_bottom_warning

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def owned(args,doc,local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    previous=ROOT/args.previous;selection=read(previous/'selection.json.gz');assert len(selection['rows'])==1
    row=selection['rows'][0];uid=row['uid'];manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path)
    matches=[(m,u) for u in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models'] if m['uid']==uid]
    assert len(matches)==1 and matches[0][0]['sha256']==row['sourceSHA256']
    prior=ROOT/args.prior_installed;installed=read(prior/'installed-acceptance.json')
    assert installed['uids']==[uid] and installed['sourceSHA256']==row['sourceSHA256'] and installed['publication']
    assert installed['passed'] and read(prior/'staged-browser.json')['passed'] and read(prior/'live-browser.json')['passed']
    with __import__('run').connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        review=con.execute('SELECT review_state,source_sha256,result FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',(installed['snapshotId'],uid)).fetchone()
    assert review and review[0]=='installed-verified' and review[1]==row['sourceSHA256']
    assert review[2]['evidence']==str((prior/'installed-acceptance.json').relative_to(ROOT)) and review[2]['sha256']==digest((prior/'installed-acceptance.json').read_bytes())
    actual=ROOT/'3d-viewer'/matches[0][1]
    assert digest((actual.parent/matches[0][0]['asset']).read_bytes())==row['sourceSHA256']
    save(doc/'historical-installed-proof.json',{'previousInstalledAcceptance':{'path':review[2]['evidence'],'sha256':review[2]['sha256']},'historicalSnapshotId':installed['snapshotId'],'uid':uid,'sourceSHA256':row['sourceSHA256'],'catalogueURL':matches[0][1]})
    assert digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())==row['source']['tileSHA256']
    inputs=read(previous/'neighbour-inputs.json.gz')
    for path,sha in inputs['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    native_uids={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    rebound=[]
    for neighbour in inputs['rows']:
        actual=neighbour['building']['uid'] in native_uids
        if bool(neighbour['existingNative'])!=actual:rebound.append({'uid':neighbour['building']['uid'],'previous':bool(neighbour['existingNative']),'current':actual})
        neighbour['existingNative']=actual
    identity=read(previous/'identity-proof.json')
    from government_georef_cell_identity import verify_files, POLICY
    from terrain_source_preflight import SourceSheetIndex, preflight
    assert identity['method']==POLICY
    context=next(r for r in read(ROOT/args.base/'context.json.gz')['rows'] if r['uid']==uid)
    positive=verify_files(row,context,local/'identity-current-recheck')
    assert positive['passed'] and positive==read(previous/'owned-source-identity.json')
    assert positive==read(previous/'owned-source-identity-contact.json')
    assert identity['ownedSourceProofSHA256']==digest((previous/'owned-source-identity.json').read_bytes())
    save(doc/'owned-source-identity.json',positive)
    save(doc/'owned-source-identity-contact.json',positive)
    index_path=ROOT/'source-scripts/city/landmark-acquisition/index.json'
    routing=preflight(row,context,SourceSheetIndex(read(index_path)))
    routing['legacyProjectionIdentity']=routing['identity']
    routing['identity']={'passed':positive['passed'],'proof':positive['proof'],'reasons':positive['reasons'],'method':POLICY}
    routing['canStartTerrainWork']=positive['passed'] and routing['primarySheetIntersects']
    assert routing['canStartTerrainWork'], 'Fresh source-sheet preflight failed'
    routing['inputHashes']={str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [index_path,ROOT/args.base/'context.json.gz',HERE/'terrain_source_preflight.py',HERE/'government_georef_cell_identity.py',Path(__file__)]}
    routing['qualification']='Fresh original source sheet and positive identity preflight; current full terrain/contact/foundation/neighbour checks and installation acceptance remain mandatory.'
    save(doc/'indexed-preflight.json',routing)
    patch=read(previous/'terrain-candidates.json')[0];assert digest((ROOT/patch['path']).read_bytes())==patch['sha256']
    raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
    dest=local/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    row['candidate']['path']=str(dest.relative_to(ROOT))
    old_local=HERE/'local'/previous.name
    for name in ('catalogue.json','catalogue-index.json','source-forms.json'):save(local/name,read(old_local/name))
    save(doc/'selection.json.gz',{**selection,'batch':args.batch,'rows':[row],
        'previousManifestSHA256':selection['manifestSHA256'],'manifestSHA256':digest(manifest_path.read_bytes())})
    save(doc/'terrain-candidates.json',[patch]);save(doc/'terrain.json',read(previous/'terrain.json'))
    save(doc/'neighbour-inputs.json.gz',inputs);save(doc/'identity-proof.json',read(previous/'identity-proof.json'))
    save(doc/'recheck-inputs.json',{'previousEvidenceRefs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
        for p in sorted(previous.iterdir()) if p.is_file() and p.name.endswith(('.json','.gz'))],
        'runnerSHA256':digest(Path(__file__).read_bytes()),'diagnosticResolverSHA256':digest((HERE/'terrain_diagnostic_resolution.py').read_bytes()),
        'currentNativeNeighbourRebindings':rebound,'candidateModelSHA256':row['sourceSHA256'],'candidateTerrainSHA256':patch['sha256'],'modelGeometryChanges':0,'publication':False})
    rel=lambda p:str(p.relative_to(ROOT))
    def call(command,allowed=(0,)):
        assert subprocess.run(command,cwd=ROOT).returncode in allowed
        assert reservations.owns(lease)
    save(doc/'already-published-terrain.json',[])
    call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(doc/'selection.json.gz'),'--candidates',rel(local),
        '--terrain-candidates',rel(doc/'already-published-terrain.json'),'--out',rel(doc/'metrics.json'),'--geometry-out',rel(local/'runtime-geometry.json.gz')])
    call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(local),'--source-forms',rel(local/'source-forms.json'),
        '--terrain-candidates',rel(doc/'already-published-terrain.json'),'--out',rel(doc/'validation.json')],(0,1))
    call(['node',str(HERE/'check-neighbours.mjs'),rel(doc)+'/']);call(['node',str(HERE/'check-native-neighbours.mjs'),rel(doc)+'/'])
    geometry=read(local/'runtime-geometry.json.gz')['rows'][0];triangles=np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)]
    ground=np.asarray(geometry['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building']
    foundation=module('recheck_foundation','xl-final-script-pass.py').foundation_context(triangles,ground,Polygon(b['rings'][0],b['rings'][1:]))
    f={'uid':uid,'sourceSHA256':row['sourceSHA256'],'foundation':foundation,
       'strictFoundationAccepted':foundation['completeTerrainTriangles']==foundation['triangles'] and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0}
    save(doc/'foundation.json',{'rows':[f],'modelGeometryChanges':0})
    metrics=read(doc/'metrics.json');m=metrics['rows'][0];validation=read(doc/'validation.json')
    proof=resolve_global_bottom_warning(validation['results'][0],m,f);save(doc/'diagnostic-resolution.json',proof)
    reasons=module('recheck_policy','acceptance-policy.py').reasons({'state':'runtime-validated-awaiting-acceptance',
        'sourceSHA256':row['sourceSHA256'],'identityProof':read(doc/'identity-proof.json')['proof']},m,metrics['profiles']['mobile'])
    if not f['strictFoundationAccepted']:reasons.append('whole-source-foundation')
    for path,sha in metrics['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    assert digest(manifest_path.read_bytes())==read(doc/'selection.json.gz')['manifestSHA256']
    reasons.extend(proof['remaining']);native=read(doc/'native-neighbour-checks.json');resolved=set(native['resolved'])
    reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved)
    reasons.extend('terrain-regresses-neighbour:'+r['uid'] for r in read(doc/'neighbour-checks.json')['rows'] if r['reasons'] and r['uid'] not in resolved)
    module('recheck_fenced','xl-cell-indexed-terrain-continuation.py').finish(args,row,doc,local,reasons)

def main():
    p=argparse.ArgumentParser();p.add_argument('--previous',required=True);p.add_argument('--batch',required=True);p.add_argument('--base',required=True);p.add_argument('--owned',action='store_true');p.add_argument('--prior-installed',required=True);a=p.parse_args()
    assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
    if a.owned:owned(a,doc,local);return
    assert not doc.exists(),'Fresh recheck only'
    prev=ROOT/a.previous;uids={r['building']['uid'] for r in read(prev/'neighbour-inputs.json.gz')['rows']}|{r['uid'] for r in read(prev/'selection.json.gz')['rows']}
    claim=reservations.claim('codex-xl-current-recheck-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(uids)],batch=a.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),
        '--',sys.executable,__file__,'--previous',a.previous,'--batch',a.batch,'--base',a.base,'--prior-installed',a.prior_installed,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
