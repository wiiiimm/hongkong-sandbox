"""Freeze exact Primrose Hill podium74573; retain its empty pending decision."""
import argparse, importlib.util, json, shutil, subprocess, sys, uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, NATIVE_RUN
from primrose_podium_pending_review import verify
from publication_lock import locked_publication

UID = 'landsd/74573:0'
CLOSURE = ROOT/'docs/astra-city/government-import/government-xl-primrose-podium-original-closure-20261007'


def owned(a, doc, local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    result=read(CLOSURE/'result.json')
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
    for ref in result['evidenceRefs']:
        assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    row=next(r for r in read(CLOSURE/'selection.json.gz')['rows'] if r['uid']==UID)
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        row['currentReview']=verify(con,UID,row['sourceSHA256'])
        assert con.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifest_path);manifest_sha=digest(manifest_path.read_bytes())
    assert not any(m['uid']==UID for u in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models'])
    path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256']
    source_tile=ROOT/'3d-viewer'/row['source']['tile']
    assert digest(source_tile.read_bytes())==row['source']['tileSHA256']
    matches=[b for b in read(source_tile)['buildings'] if b['uid']==UID]
    assert matches==[row['source']['building']]
    dest=local/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
    row['candidate']['path']=str(dest.relative_to(ROOT));row['candidate']['entry']['asset']='assets/'+dest.name
    spec=importlib.util.spec_from_file_location('primrose_exact_context',HERE/'xl-final-script-pass.py')
    final=importlib.util.module_from_spec(spec);spec.loader.exec_module(final);final.s.LOCAL=local
    triangles=final.s.glb_triangles(row);lo,hi=triangles.min(axis=(0,1)),triangles.max(axis=(0,1))
    neighbours=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
    context={'uid':UID,'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,triangles,neighbours),
        'neighbourTileHashes':{tile:digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in neighbours}}
    assert reservations.owns(lease) and digest(manifest_path.read_bytes())==manifest_sha
    save(doc/'check-selection.json.gz',{'batch':a.batch,'rows':[row],'manifestSHA256':manifest_sha})
    save(doc/'context.json.gz',{'rows':[context]})
    save(doc/'pending-review-continuation.json',row['currentReview'])
    refs=[CLOSURE/'result.json',CLOSURE/'selection.json.gz',source_tile,Path(__file__),HERE/'primrose_podium_pending_review.py',HERE/'test_primrose_podium_pending_review.py']
    save(doc/'input-proof.json',{'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in refs},
        'publication':False,'newlyInstalled':0,'modelGeometryChanges':0,'scriptExternalAICalls':0})
    print(json.dumps({'frozen':UID,'pendingReviewRetained':True,'newlyInstalled':0}),flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');a=p.parse_args()
    assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
    if a.owned:
        with locked_publication(ROOT):owned(a,doc,local)
        return
    assert not doc.exists(),'Fresh exact source freeze required'
    claim=reservations.claim('codex-primrose-podium-freeze-'+str(uuid.uuid4()),['building:'+UID],batch=a.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)


if __name__=='__main__':main()
