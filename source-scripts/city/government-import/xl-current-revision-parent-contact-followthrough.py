"""Reuse exact existing regional facets under diagnosed contact-gap faces.

Original models and parent grids remain unchanged. This prepares a candidate and
reruns all physical gates; it cannot install or waive any acceptance threshold.
"""
import argparse
import importlib.util
import json
import subprocess
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations,connect


def module(name,file):
    spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def owned(args,doc,local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    previous=ROOT/args.previous;prior=read(previous/'result.json')
    assert prior['reasons']==['ground-contact-unresolved'] and not prior['publication']
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY');assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    for ref in prior['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
    selection=read(previous/'selection.json.gz');assert len(selection['rows'])==1
    row=selection['rows'][0];uid=row['uid'];assert row['native'].get('revisionAcquisition')
    candidate=read(previous/'terrain-candidates.json')[0]
    assert digest((ROOT/candidate['path']).read_bytes())==candidate['sha256']
    replaced=candidate['replaces'];parent_path=ROOT/'3d-viewer'/replaced['url']
    assert digest(parent_path.read_bytes())==replaced['sha256']
    parent=read(parent_path);wrapper=read(ROOT/candidate['path'])
    assert wrapper.get('patches') and len(wrapper['patches'])==len(parent['patches'])+1
    for old,new in zip(parent['patches'],wrapper['patches']):
        for key in ('elev','renderedElev','vegetation','coarseCells'):assert old.get(key)==new.get(key)
        for key in ('position','index'):assert old.get('nativeMesh',{}).get(key)==new.get('nativeMesh',{}).get(key)
    patch=wrapper['patches'][-1];assert patch['meta']['targetUids']==[uid]
    geometry_path=HERE/'local'/previous.name/'runtime-geometry.json.gz';geometry=read(geometry_path)
    runtime=geometry['rows'][0];assert runtime['uid']==uid and runtime['sourceSHA256']==row['sourceSHA256']
    diagnostic_path=ROOT/args.diagnostic;diagnostic=read(diagnostic_path)
    assert diagnostic['diagnosticOnly'] and not diagnostic['publication']
    assert diagnostic['runnerSHA256']==digest((HERE/'xl-cached-runtime-complete-contact-diagnostic.mjs').read_bytes())
    assert diagnostic['geometry']=={'path':str(geometry_path.relative_to(ROOT)),'sha256':digest(geometry_path.read_bytes())}
    for path,sha in diagnostic['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
    failure=diagnostic['rows'][0];assert failure['uid']==uid and failure['sourceSHA256']==row['sourceSHA256']
    indices=np.asarray(runtime['index']).reshape(-1,3);vertices=np.asarray(runtime['position']).reshape(-1,3);faces=vertices[indices]
    affected=np.zeros(len(faces),dtype=bool)
    for point in failure['failed']:
        assert point['gap']>1 and point['point'][1]<=vertices[:,1].min()+.35
        if point['face'] is None:affected[(indices==point['vertex']).any(axis=1)]=True
        else:affected[point['face']]=True
    assert affected.any()
    projection=shapely.union_all([shapely.MultiPoint(f[:,[0,2]]).convex_hull for f in faces[affected]]).buffer(.01,join_style='mitre')
    patches=module('current_revision_original_parent','native_patch_resolution.py')
    second=module('current_revision_parent_sampler','xl-second-pass.py')
    sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
    proof=patches.preserve_parent_under_projection(patch,candidate['bounds'],projection,sampler)
    proof.update(diagnosedSourceFaces=np.flatnonzero(affected).tolist(),contactDiagnostic={'path':args.diagnostic,'sha256':digest(diagnostic_path.read_bytes())},
                 parentURL=replaced['url'],parentSHA256=replaced['sha256'],runnerSHA256=digest(Path(__file__).read_bytes()),
                 policy='Existing regional parent facets only in the diagnosed gap-face projection; source and parent elevations unchanged. Full source/foundation/neighbour/runtime checks required.')
    assert proof['preservedAreaM2']>0 if 'preservedAreaM2' in proof else proof['areaM2']>0
    raw_path=local/(patch['id']+'.json');save(raw_path,patch)
    terrain=read(previous/'terrain.json')
    excess=patches.projected_context(patch,candidate['bounds'])[3]
    if excess>1e-6:
        patches.approve_original_overlap(patch,raw_path,doc/'protected-overlap.json',terrain['sourceFiles'])
        patches.finalize_overlap_evidence(patch,doc/'protected-overlap.json')
    else:patch['nativeMesh'].pop('sourceOverlap',None)
    save(raw_path,patch)
    path=local/Path(candidate['path']).name;save(path,wrapper)
    updated={**candidate,'path':str(path.relative_to(ROOT)),'sha256':digest(path.read_bytes()),'triangles':sum(len(p.get('nativeMesh',{}).get('index',[]))//3 for p in wrapper['patches'])}
    prepared=doc.parent/(args.batch+'-prepared');assert not prepared.exists()
    for name in ('selection.json.gz','neighbour-inputs.json.gz','identity-proof.json','owned-source-identity.json','owned-source-identity-contact.json','indexed-preflight.json'):save(prepared/name,read(previous/name))
    save(prepared/'terrain-candidates.json',[updated]);save(prepared/'terrain.json',{**terrain,'patch':updated,'originalParentContact':proof})
    inputs=read(prepared/'neighbour-inputs.json.gz');inputs['patches']=[updated];save(prepared/'neighbour-inputs.json.gz',inputs)
    save(prepared/'parent-preservation.json',{'proof':proof,'priorJobId':prior['jobId'],'modelGeometryChanges':0,'publication':False})
    for name in ('catalogue.json','catalogue-index.json','source-forms.json'):save(HERE/'local'/prepared.name/name,read(HERE/'local'/previous.name/name))
    module('current_revision_full_recheck','xl-current-revision-installation-recheck.py').owned(SimpleNamespace(previous=str(prepared.relative_to(ROOT)),base=args.base,batch=args.batch),doc,local)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('previous','base','batch','diagnostic'):p.add_argument('--'+name,required=True)
    p.add_argument('--owned',action='store_true');args=p.parse_args()
    assert Path(args.batch).name==args.batch and args.batch.startswith('government-xl-')
    doc=ROOT/'docs/astra-city/government-import'/args.batch;local=HERE/'local'/args.batch
    if args.owned:owned(args,doc,local);return
    assert not doc.exists()
    previous=ROOT/args.previous;uids={r['building']['uid'] for r in read(previous/'neighbour-inputs.json.gz')['rows']}|{read(previous/'selection.json.gz')['rows'][0]['uid']}
    claim=reservations.claim('codex-revision-parent-contact-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(uids)],batch=args.batch);assert claim['ok'],claim
    save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,*sys.argv[1:],'--owned'],cwd=ROOT,check=True)


if __name__=='__main__':main()
