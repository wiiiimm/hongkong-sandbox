"""Freeze a bounded explicit XL source list with fresh ownership and geometry context."""
import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations,connect
from terrain_source_preflight import SourceSheetIndex,preflight
sys.path.insert(0,str(HERE.parent/'enhancement-screening'))
from shape_prepare import entry


def owned(args,doc,local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    uids=read(ROOT/args.uids_file)['uids']
    macro_path=ROOT/'docs/astra-city/government-import/government-xl-remaining-20260923/selection.json.gz'
    macro=read(macro_path);by_uid={r['uid']:r for r in macro['rows']}
    assert set(uids)<=set(by_uid)
    manifest_path=ROOT/'3d-viewer/city/data/manifest.json';manifest_sha=digest(manifest_path.read_bytes());manifest=read(manifest_path)
    installed={m['uid'] for url in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    assert not set(uids)&installed,'Already installed source in explicit list'
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        reviews=con.execute('SELECT uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s)',(uids,)).fetchall()
    assert not reviews,'Existing reviews require explicit resolution'
    forms={}
    for tile in manifest['tiles']:
        path=ROOT/'3d-viewer'/tile['url'];data=read(path)
        for b in data['buildings']:
            if b['uid'] in uids:
                assert b['uid'] not in forms,'Ambiguous current source form'
                forms[b['uid']]={'building':b,'tile':tile['url'],'tileSHA256':digest(path.read_bytes())}
    assert set(forms)==set(uids)
    wanted={by_uid[u]['sourceSHA256'] for u in uids};assets={}
    for path in (HERE/'local').rglob('*.glb.gz'):
        sha=path.name.removesuffix('.glb.gz')
        if sha in wanted and digest(path.read_bytes())==sha:
            assets[sha]=path;wanted.remove(sha)
        if not wanted:break
    assert not wanted,('Exact original assets must be recovered before freeze',sorted(wanted))
    spec=importlib.util.spec_from_file_location('explicit_context',HERE/'xl-final-script-pass.py')
    context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);context.s.LOCAL=local
    index_path=ROOT/'source-scripts/city/landmark-acquisition/index.json';index=SourceSheetIndex(read(index_path))
    rows=[];contexts=[];routes=[]
    for uid in uids:
        assert reservations.owns(lease)
        old=by_uid[uid];source=forms[uid];sha=old['sourceSHA256'];path=local/'assets'/(sha+'.glb.gz')
        path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(assets[sha],path)
        candidate=entry(old['native'],source['building']);candidate['asset']='assets/'+path.name
        row={**old,'source':source,'currentReview':None,'candidate':{'entry':candidate,'path':str(path.relative_to(ROOT))}}
        triangles=context.s.glb_triangles(row);lo,hi=triangles.min(axis=(0,1)),triangles.max(axis=(0,1))
        neighbours=context.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2])
        evidence={'uid':uid,'sourceSHA256':sha,'identity':context.identity_context(row,triangles,neighbours),
                  'neighbourTileHashes':{tile:digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in neighbours}}
        route=preflight(row,evidence,index);rows.append(row);contexts.append(evidence);routes.append(route)
        print(json.dumps({'frozen':len(rows),'total':len(uids),'uid':uid,'name':old['name'],'identityPassed':route['canStartTerrainWork']}),flush=True)
    assert reservations.owns(lease) and digest(manifest_path.read_bytes())==manifest_sha
    for evidence in contexts:
        for tile,sha in evidence['neighbourTileHashes'].items():assert digest((ROOT/'3d-viewer'/tile).read_bytes())==sha
    save(doc/'explicit-uids.json',read(ROOT/args.uids_file))
    save(doc/'check-selection.json.gz',{**macro,'batch':args.batch,'rows':rows,'manifestSHA256':manifest_sha,
        'qualification':'Explicit bounded source freeze; complete current source/context hashes. Failed preflight rows remain accounted. No review, publication or installation credit.'})
    save(doc/'context.json.gz',{'rows':contexts})
    save(doc/'preflight.json',{'rows':routes,'originalSelectionSHA256':digest(macro_path.read_bytes()),
        'explicitUIDsSHA256':digest((ROOT/args.uids_file).read_bytes()),'runnerSHA256':digest(Path(__file__).read_bytes()),
        'modelGeometryChanges':0,'scriptExternalAICalls':0,'publication':False})


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--uids-file',required=True);p.add_argument('--batch',required=True)
    p.add_argument('--owned',action='store_true',help=argparse.SUPPRESS);args=p.parse_args()
    assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    path=(ROOT/args.uids_file).resolve();assert path.is_relative_to(ROOT)
    uids=read(path)['uids'];assert 1<=len(uids)<=200 and len(uids)==len(set(uids))
    resources=reservations.normalise(['building:'+u for u in uids])
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    if args.owned:owned(args,doc,local);return
    assert not doc.exists(),'Immutable completed inputs; use a fresh explicit batch'
    claim=reservations.claim('codex-xl-explicit-freeze-'+str(uuid.uuid4()),resources,batch=args.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),
        '--',sys.executable,__file__,'--uids-file',args.uids_file,'--batch',args.batch,'--owned'],cwd=ROOT,check=True)


if __name__=='__main__':main()
