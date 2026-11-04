"""Test unchanged parent facets below source faces buried by a new terrain patch.

Existing source geometry, parent heights and all acceptance limits stay fixed.
Only lower parent facets qualify. Run full current source/foundation/neighbour
checks; preparation is never publication or acceptance.
"""
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations,connect
import importlib.util


def module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def owned(args,doc,local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    previous=ROOT/args.previous
    prior=read(previous/'result.json');sync=read(previous/'neon-sync.json')
    assert sync['resultVerified'] and sync['jobId']==prior['jobId']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    for evidence in prior['evidenceRefs']:assert digest((ROOT/evidence['path']).read_bytes())==evidence['sha256']
    selection=read(previous/'selection.json.gz')
    assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==selection['manifestSHA256']
    assert len(selection['rows'])==1
    row=selection['rows'][0];uid=row['uid'];original=read(previous/'terrain-candidates.json')[0]
    assert not original.get('replaces'),'Retained native terrain needs its dedicated preservation path'
    assert digest((ROOT/original['path']).read_bytes())==original['sha256']
    raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256']
    assert digest((ROOT/'3d-viewer'/row['source']['tile']).read_bytes())==row['source']['tileSHA256']
    second=module('face_parent_source','xl-second-pass.py');second.LOCAL=local
    dest=local/'assets'/(row['sourceSHA256']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    triangles=second.glb_triangles(row)
    patches=module('face_parent_planes','native_patch_resolution.py')
    parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path)
    sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
    patch=read(ROOT/original['path']);bounds=original['bounds'];native=patches._faces(patch)
    points=np.concatenate([triangles,triangles.mean(axis=1)[:,None,:]],axis=1)
    polys=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
    heights=second.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native[valid],shapely.STRtree(polys[valid])).reshape(-1,4)
    assert np.isfinite(heights).all(),'Complete existing patch coverage required'
    failed=(points[:,:,1]-heights<-.5).any(axis=1)
    assert failed.any(),'No buried source face needs investigation'
    source_projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in triangles])
    proposed=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in triangles[failed]]).buffer(.01,join_style='mitre')
    lower,lower_proof=patches.lower_parent_projection(patch,bounds,proposed,sampler)
    if lower.area<=1e-8:
        save(doc/'source-face-parent.json',{'uid':uid,'sourceSHA256':row['sourceSHA256'],
            'sourceFaces':np.flatnonzero(failed).tolist(),'lowerParent':lower_proof,
            'parent':{'path':str(parent_path.relative_to(ROOT)),'sha256':digest(parent_path.read_bytes())},
            'nativeCandidate':original,'previousResult':{'path':str((previous/'result.json').relative_to(ROOT)),
                'sha256':digest((previous/'result.json').read_bytes())},
            'runnerSHA256':digest(Path(__file__).read_bytes()),'modelGeometryChanges':0,
            'scriptExternalAICalls':0,'publication':False,
            'qualification':'No unchanged lower parent region exists under the failed face projection. Existing buried-source checks remain blocking; do not invent lower heights.'})
        reasons=read(previous/'result.json')['reasons']+['no-lower-original-parent-under-failed-source-faces']
        module('face_parent_no_lower_fence','xl-cell-indexed-terrain-continuation.py').finish(args,row,doc,local,reasons)
        return
    preservation=patches.preserve_parent_under_projection(patch,bounds,lower,sampler)
    terrain=read(previous/'terrain.json')
    for source in terrain['sourceFiles']:assert digest((ROOT/source['path']).read_bytes())==source['sha256']
    missing=patches.projected_context(patch,bounds)[2]
    if missing.intersection(source_projection).area>=1e-6:
        patches.fill_narrow_source_seam(patch,bounds,source_projection,sampler,tolerance=.02)
    else:patches.fill_parent_only_holes(patch,parent,bounds,source_projection,sampler)
    patch['nativeMesh']['source']['finalBoundarySnap']=patches.snap_boundary_to_parent(patch,bounds,sampler)
    path=local/Path(original['path']).name;save(path,patch)
    if patches.projected_context(patch,bounds)[3]>1e-8:
        patches.approve_original_overlap(patch,path,doc/'protected-overlap.json',terrain['sourceFiles'])
        patches.finalize_overlap_evidence(patch,doc/'protected-overlap.json')
    else:patch['nativeMesh'].pop('sourceOverlap',None)
    second.resolution.validate_patch(patch,parent);save(path,patch)
    candidate={**original,'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'triangles':len(patch['nativeMesh']['index'])//3}
    prepared=ROOT/'docs/astra-city/government-import'/(args.batch+'-prepared')
    prepared_local=HERE/'local'/prepared.name
    assert not prepared.exists(),'Prepared evidence is immutable'
    for name in ['selection.json.gz','neighbour-inputs.json.gz','identity-proof.json','owned-source-identity.json','owned-source-identity-contact.json','indexed-preflight.json']:
        save(prepared/name,read(previous/name))
    save(prepared/'terrain-candidates.json',[candidate]);save(prepared/'terrain.json',{**terrain,'patch':candidate})
    neighbours=read(prepared/'neighbour-inputs.json.gz');neighbours['patches']=[candidate];save(prepared/'neighbour-inputs.json.gz',neighbours)
    for name in ['catalogue.json','catalogue-index.json','source-forms.json']:
        save(prepared_local/name,read(HERE/'local'/previous.name/name))
    save(prepared/'source-face-parent.json',{'uid':uid,'sourceSHA256':row['sourceSHA256'],
        'sourceFaces':np.flatnonzero(failed).tolist(),'lowerParent':lower_proof,'preservation':preservation,
        'parent':{'path':str(parent_path.relative_to(ROOT)),'sha256':digest(parent_path.read_bytes())},
        'previousEvidenceRefs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in sorted(previous.iterdir()) if p.is_file() and p.name.endswith(('.json','.gz'))],
        'runnerSHA256':digest(Path(__file__).read_bytes()),'modelGeometryChanges':0,'scriptExternalAICalls':0,
        'publication':False,'qualification':'Only unchanged lower parent facets, followed by complete current checks. No invented lower surface or clearance increase.'})
    recheck=module('face_parent_full_checks','xl-cell-installation-recheck.py')
    recheck.owned(SimpleNamespace(previous=str(prepared.relative_to(ROOT)),batch=args.batch,base=Path(args.base)),doc,local)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--previous',required=True);p.add_argument('--batch',required=True);p.add_argument('--base',required=True)
    p.add_argument('--owned',action='store_true');args=p.parse_args()
    assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    if args.owned:owned(args,doc,local);return
    assert not doc.exists(),'Fresh explicit continuation only'
    prev=ROOT/args.previous
    uids={r['building']['uid'] for r in read(prev/'neighbour-inputs.json.gz')['rows']}|{r['uid'] for r in read(prev/'selection.json.gz')['rows']}
    claim=reservations.claim('codex-xl-source-face-parent-'+str(uuid.uuid4()),
        [('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(uids)],batch=args.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),
        '--',sys.executable,__file__,'--previous',args.previous,'--batch',args.batch,'--base',args.base,'--owned'],cwd=ROOT,check=True)


if __name__=='__main__':main()
