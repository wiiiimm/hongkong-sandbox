"""Preserve the existing root terrain height floor outside every original mesh."""
import argparse
import json
import subprocess
import sys
import uuid
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT, read, save, digest, reservations, connect
from rendered_patch_sampler import RenderedPatchSampler
from government_georef_cell_identity import verify_files, POLICY
import importlib.util

DIR = ROOT/'source-scripts/city/government-import'
BASE = ROOT/'docs/astra-city/government-import/government-xl-sustained-131-inputs-20261006'
PREVIOUS = ROOT/'docs/astra-city/government-import/government-xl-alto6-common-original-terrain-20261007'
UID = 'landsd/338637:0'
NEIGHBOR = 'way/627834829:0'

def module(name, filename):
    spec=importlib.util.spec_from_file_location(name,DIR/filename)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def ref(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':digest(path.read_bytes())}

def owned(args,doc,local):
    lease=read(local/'reservation.json');assert reservations.owns(lease)
    prior=read(PREVIOUS/'result.json')
    assert prior['reasons'] and all(r.startswith('terrain-regresses-neighbour:') for r in prior['reasons'])
    with connect() as con:
        con.execute('SET TRANSACTION READ ONLY')
        assert con.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
    for evidence in prior['evidenceRefs']:assert ref(ROOT/evidence['path'])==evidence
    original=read(PREVIOUS/'terrain-candidates.json')[0]
    assert ref(ROOT/original['path'])['sha256']==original['sha256']
    old_path=ROOT/'3d-viewer'/original['replaces']['url']
    assert ref(old_path)['sha256']==original['replaces']['sha256']
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    selection=read(PREVIOUS/'selection.json.gz');row=selection['rows'][0]
    assert ref(manifest)['sha256']==selection['manifestSHA256']
    context=next(r for r in read(BASE/'context.json.gz')['rows'] if r['uid']==UID)
    identity=verify_files(row,context,local/'identity-current')
    assert identity['passed'] and identity['policy']==POLICY
    assert identity==read(PREVIOUS/'owned-source-identity.json')
    save(doc/'owned-source-identity.json',identity);save(doc/'owned-source-identity-contact.json',identity)
    save(doc/'identity-proof.json',{'uid':UID,'sourceSHA256':row['sourceSHA256'],'proof':identity['proof'],'method':POLICY,'ownedSourceProofSHA256':ref(doc/'owned-source-identity.json')['sha256']})
    request=local/'retained-request.json';export=local/'retained-native-geometry.json.gz'
    save(request,{'uids':original['replaces']['retainedUids']})
    subprocess.run(['node',str(DIR/'retained-native-geometry.mjs'),str(request.relative_to(ROOT)),str(export.relative_to(ROOT))],cwd=ROOT,check=True)
    retained=read(export)
    for path,sha in retained['inputHashes'].items():assert ref(ROOT/path)['sha256']==sha
    actual=read(DIR/'local'/PREVIOUS.name/'runtime-geometry.json.gz')['rows'][0]
    bodies=[np.asarray(actual['position']).reshape(-1,3)[np.asarray(actual['index']).reshape(-1,3)]]
    bodies.extend(np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)] for r in retained['rows'])
    projection=shapely.union_all([shapely.MultiPoint(face[:,[0,2]]).convex_hull for body in bodies for face in body])
    inputs=read(PREVIOUS/'neighbour-inputs.json.gz')
    by_uid={r['building']['uid']:r for r in inputs['rows']};protect=[];excluded=[]
    for reason in prior['reasons']:
        uid=reason.split(':',1)[1];neighbor=by_uid[uid];assert not neighbor['existingNative']
        b=neighbor['building'];foot=Polygon(b['rings'][0],b['rings'][1:]).buffer(.01,join_style='mitre')
        part=foot.difference(projection.buffer(.01,join_style='mitre'))
        if part.area>1e-8:protect.append((uid,part))
        if foot.intersection(projection).area>1e-8:excluded.append({'uid':uid,'overlappingAreaM2':float(foot.intersection(projection).area),'preservedAreaM2':float(part.area)})
    assert protect
    protected=shapely.union_all([part for _,part in protect]);assert protected.intersection(projection).area<1e-8
    parent_path=ROOT/'3d-viewer/city/data/terrain.json';parent=read(parent_path)
    second=module('alto_parent_decoder','xl-second-pass.py')
    patches=module('alto_parent_patches','native_patch_resolution.py')
    sampler=second.resolution.terrain.fine.DemSampler(parent,rendered=True)
    # geo.js clamps the root height field at 1.2 m. Existing _floor_faces
    # splits original parent planes at that contour; original TIN/model
    # heights and the retained child's own height field remain unchanged.
    sampler.parent_height_floor=1.2
    old=read(old_path)
    existing=RenderedPatchSampler(old,sampler,second.resolution.terrain.fine.DemSampler(old,rendered=True))
    patch=read(ROOT/original['path']);bounds=original['bounds']
    proof=patches.preserve_parent_under_projection(patch,bounds,protected,existing,edge_sampler=sampler)
    proof.update(protectedUids=[uid for uid,_ in protect],overlappingPortionsExcluded=excluded,sourceProjectionIntersectionM2=0,rootRuntimeHeightFloorM=1.2,rootRuntimeFloorSource=ref(ROOT/'3d-viewer/city/geo.js'),parentFloorImplementation=ref(DIR/'native_patch_resolution.py'),minimumDistanceFromSourceM=float(protected.distance(projection)),originalSurface=ref(old_path),retainedGeometry=ref(export),retainedGeometryInputs=retained['inputHashes'],qualification='Exact deployed terrain planes under one proven-disjoint basic footprint. New and both retained original meshes still require complete checks.')
    patches.fill_parent_only_holes(patch,parent,bounds,projection,sampler)
    patch['nativeMesh']['source']['finalBoundarySnap']=patches.snap_boundary_to_parent(patch,bounds,sampler)
    path=local/Path(original['path']).name;save(path,patch)
    terrain=read(PREVIOUS/'terrain.json')
    if patches.projected_context(patch,bounds)[3]>1e-8:
        patches.approve_original_overlap(patch,path,doc/'protected-overlap.json',terrain['sourceFiles'])
        patches.finalize_overlap_evidence(patch,doc/'protected-overlap.json')
    else:patch['nativeMesh'].pop('sourceOverlap',None)
    second.resolution.validate_patch(patch,parent);save(path,patch)
    candidate={**original,**ref(path),'triangles':len(patch['nativeMesh']['index'])//3}
    save(doc/'terrain-candidates.json',[candidate]);save(doc/'terrain.json',{**terrain,'patch':candidate})
    inputs['patches']=[candidate];save(doc/'neighbour-inputs.json.gz',inputs)
    save(doc/'selection.json.gz',selection)
    for name in ('catalogue.json','catalogue-index.json','source-forms.json'):save(local/name,read(DIR/'local'/PREVIOUS.name/name))
    save(doc/'parent-preservation.json',{'proof':proof,'previousPatch':original,'candidatePatch':candidate,'previousEvidenceRefs':[ref(PREVIOUS/'result.json'),ref(PREVIOUS/'neon-sync.json')],'runner':ref(Path(__file__)),'modelGeometryChanges':0,'scriptExternalAICalls':0,'publication':False})
    assert reservations.owns(lease)
    print(json.dumps({'prepared':args.batch,'protected':[uid for uid,_ in protect],'overlapping':excluded,'distanceFromSourceM':proof['minimumDistanceFromSourceM']}),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--owned',action='store_true');p.add_argument('--uid',required=True);p.add_argument('--previous',required=True);p.add_argument('--base',required=True);a=p.parse_args()
    global UID,PREVIOUS,BASE
    UID=a.uid;PREVIOUS=(ROOT/a.previous).resolve();BASE=(ROOT/a.base).resolve()
    assert PREVIOUS.is_relative_to(ROOT/'docs/astra-city/government-import') and BASE.is_relative_to(ROOT/'docs/astra-city/government-import')
    assert a.batch.startswith('government-xl-') and Path(a.batch).name==a.batch
    doc=ROOT/'docs/astra-city/government-import'/(a.batch+'-prepared');local=DIR/'local'/doc.name
    if a.owned:owned(a,doc,local);return
    assert not doc.exists()
    inputs=read(PREVIOUS/'neighbour-inputs.json.gz');uids={UID,*(r['building']['uid'] for r in inputs['rows'])}
    claim=reservations.claim('codex-alto-common-preserve-'+str(uuid.uuid4()),[('building:' if u.startswith('landsd/') else 'source-form:')+u for u in sorted(uids)]+['terrain-surface:'+read(PREVIOUS/'terrain-candidates.json')[0]['replaces']['url']],batch=a.batch)
    assert claim['ok'];save(local/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)))
    subprocess.run([sys.executable,str(DIR.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(local/'reservation.json'),'--',sys.executable,__file__,'--batch',a.batch,'--uid',UID,'--previous',a.previous,'--base',a.base,'--owned'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(DIR/'xl-cell-installation-recheck.py'),'--previous',str(doc.relative_to(ROOT)),'--batch',a.batch,'--base',str(BASE.relative_to(ROOT))],cwd=ROOT,check=True)

if __name__=='__main__':main()
