"""Merge a passing root candidate with exact existing native terrain, then recheck.

No new source reconstruction. Preserve old facets over their entire extent, use
the already-passing candidate outside, and fill uncovered outer cells from the
unchanged parent. Complete fresh model/neighbour/source checks decide acceptance.
"""
import argparse, importlib.util, json, subprocess, sys, uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
import native_patch_resolution as patches
from rendered_patch_sampler import RenderedPatchSampler

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def owned(args,doc,local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    previous=ROOT/args.previous;wrapper=ROOT/args.wrapper
    selection=read(previous/'selection.json.gz');assert len(selection['rows'])==1
    row=selection['rows'][0];original=read(previous/'terrain-candidates.json')[0]
    assert digest((ROOT/original['path']).read_bytes())==original['sha256']
    assert read(previous/'result.json')['scriptChecksPassed'] and not original.get('replaces')
    assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256']
    shape=read(wrapper/'terrain-candidates.json')[0];replacement=shape['replaces']
    old_path=ROOT/'3d-viewer'/replacement['url'];assert digest(old_path.read_bytes())==replacement['sha256']
    assert digest((ROOT/shape['path']).read_bytes())==shape['sha256']
    old=read(old_path);patch=read(ROOT/shape['path']);candidate=read(ROOT/original['path']);parent=read(ROOT/'3d-viewer/city/data/terrain.json')
    assert old.get('nativeMesh') and candidate.get('nativeMesh') and not patch.get('patches')
    patch['nativeMesh']=candidate['nativeMesh'];patch['meta']['targetUids']=sorted(set(old['meta']['targetUids'])|{row['uid']})
    patch['nativeMesh'].pop('sourceOverlap',None)
    second=module('retained_passing_decoder','xl-second-pass.py');second.LOCAL=local
    raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
    asset=local/'assets'/(row['sourceSHA256']+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(raw)
    row['candidate']['path']=str(asset.relative_to(ROOT));body=second.glb_triangles(row)
    projection=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for face in body])
    root_sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
    retained_sampler=RenderedPatchSampler(old,root_sampler,second.resolution.terrain.fine.DemSampler(old,rendered=True))
    proof=patches.preserve_parent_under_projection(patch,shape['bounds'],shapely.box(*patches._patch_bounds(old)),retained_sampler,edge_sampler=root_sampler)
    missing=patches.projected_context(patch,shape['bounds'])[2]
    assert missing.intersection(projection).area<1e-6,'Missing surface under original source requires separate exact coverage handling'
    # Retain coarse parent triangle breaks throughout outer holes. A single
    # triangulation of a large hole would bridge several parent grid planes.
    parent_faces=patches.grid_surface_faces(root_sampler,missing)
    assert not missing.area>1e-8 or parent_faces,'No exact parent plane fill'
    offset=len(patch['nativeMesh']['position'])//3
    flat=np.asarray(parent_faces).reshape(-1,3) if parent_faces else np.empty((0,3))
    patch['nativeMesh']['position'].extend(flat.reshape(-1).tolist())
    patch['nativeMesh']['index'].extend(range(offset,offset+len(flat)))
    fill={'missingAreaM2':float(missing.area),'triangles':len(parent_faces),'policy':'Exact unchanged rendered parent grid planes, clipped at every cell edge and diagonal.'}
    patch['nativeMesh']['source']['parentHoleFill']=fill
    snap=patches.snap_boundary_to_parent(patch,shape['bounds'],root_sampler)
    path=local/Path(original['path']).name;save(path,patch)
    terrain=read(previous/'terrain.json');sources=list(terrain['sourceFiles'])
    for source in read(wrapper/'terrain.json')['sourceFiles']:
        assert digest((ROOT/source['path']).read_bytes())==source['sha256']
        if source not in sources:sources.append(source)
    if patches.projected_context(patch,shape['bounds'])[3]>1e-8:
        patches.approve_original_overlap(patch,path,doc/'protected-overlap.json',sources);patches.finalize_overlap_evidence(patch,doc/'protected-overlap.json')
    else:patch['nativeMesh'].pop('sourceOverlap',None)
    second.resolution.validate_patch(patch,parent);save(path,patch)
    merged={**shape,'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'triangles':len(patch['nativeMesh']['index'])//3}
    final=module('retained_passing_context','xl-final-script-pass.py');forms=final.load_forms(shape['bounds'])
    manifest=read(ROOT/'3d-viewer/city/data/manifest.json');installed={m['uid'] for u in manifest['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models']}
    neighbours={'candidateIds':[row['uid']],'patches':[merged],'rows':[{'building':b,'existingNative':b['uid'] in installed,'patchIndexes':[0]} for b,_,_ in forms],
        'inputHashes':{str((ROOT/'3d-viewer'/tile).relative_to(ROOT)):digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in forms}}
    save(doc/'selection.json.gz',{**selection,'batch':args.batch,'rows':[row]});save(doc/'terrain-candidates.json',[merged]);save(doc/'terrain.json',{**terrain,'patch':merged,'sourceFiles':sources,'parentHoleFill':fill})
    save(doc/'neighbour-inputs.json.gz',neighbours)
    for name in ['identity-proof.json','owned-source-identity.json','owned-source-identity-contact.json','indexed-preflight.json']:save(doc/name,read(previous/name))
    for name in ['catalogue.json','catalogue-index.json','source-forms.json']:save(local/name,read(HERE/'local'/previous.name/name))
    save(doc/'retained-native-proof.json',{'supersededURL':replacement['url'],'supersededSHA256':replacement['sha256'],'retainedUids':replacement['retainedUids'],'preservation':proof,'outerParentFill':fill,'boundarySnap':snap,'modelGeometryChanges':0,'scriptExternalAICalls':0,'publication':False})
    save(doc/'merge-inputs.json',{'previous':{'path':args.previous,'sourceSHA256':row['sourceSHA256'],'terrainSHA256':original['sha256']},'wrapper':{'path':args.wrapper,'sha256':shape['sha256']},'runnerSHA256':digest(Path(__file__).read_bytes()),'mergedSHA256':merged['sha256'],'qualification':'Candidate only; old facets retained over their full extent. Complete fresh model and neighbour checks remain required.'})
    print(json.dumps({'candidateMerged':row['uid'],'retained':replacement['retainedUids'],'triangles':merged['triangles'],'publication':False}),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['previous','wrapper','batch','recheck-batch','base']:p.add_argument('--'+name,required=True)
    p.add_argument('--owned',action='store_true');a=p.parse_args();assert Path(a.batch).name==a.batch and a.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/a.batch;local=HERE/'local'/a.batch
    if a.owned:return owned(a,doc,local)
    assert not doc.exists(),'Fresh merged candidate only'
    old=read(ROOT/a.wrapper/'terrain-candidates.json')[0]['replaces'];scope={r['building']['uid'] for r in read(ROOT/a.wrapper/'neighbour-inputs.json.gz')['rows']}|{r['uid'] for r in read(ROOT/a.previous/'selection.json.gz')['rows']}
    claim=reservations.claim('codex-xl-passing-native-merge-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(scope)]+['terrain-surface:'+old['url']],batch=a.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(HERE/'xl-cell-installation-recheck.py'),'--previous',str(doc.relative_to(ROOT)),'--batch',a.recheck_batch,'--base',a.base],cwd=ROOT,check=True)

if __name__=='__main__':main()
