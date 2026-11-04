"""Private bounded source-floor return in an existing native patch; no model edits.

Use the existing1m core/3m return/0.05m clearance kernel. Its1.2m minimum
for newly derived terrain stays unchanged; previously installed seabed outside
that lower-only domain remains in place. Current full acceptance is separate.
"""
import argparse,copy,sys,uuid
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_floor_return_with_existing_seabed_v1_20261102 import inset
BASE=ROOT/'docs/astra-city/government-import'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for key in ['batch','runtime','buried','scope','source-terrain','uid','terrain-url','retained-scope']:ap.add_argument('--'+key,required=True)
    ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    assert all(n.startswith('government-xl-')and '/'not in n for n in [a.batch,a.runtime,a.buried,a.scope,a.source_terrain])
    assert a.terrain_url.startswith('city/data/')and '..'not in a.terrain_url
    out=BASE/a.batch;local=HERE/'local'/a.batch;control=HERE/'local'/(a.batch+'-control')/'reservation.json'
    assert not out.exists()and not local.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(a.runtime,BASE/a.runtime/'selection.json.gz');source=next(r for r in selection['rows']if r['uid']==a.uid)
    scope=take(a.scope,BASE/a.scope/'summary.json');obligations={}
    for row in scope['rows']:
        for item in take(a.scope,BASE/a.scope/(row['uid'].split('/')[1]+'-forms.json.gz')):obligations[item['building']['uid']]=item['building']
    for form in take(a.retained_scope,BASE/a.retained_scope/'form-obligations.json.gz'):
        obligations[form['uid']]=form
    oldpath=ROOT/'3d-viewer'/a.terrain_url;before=take(a.runtime,oldpath);oldsha=digest(oldpath.read_bytes());retained=before['meta']['targetUids'];assert retained and a.uid not in retained
    resources={('building:'if u.startswith('landsd/')else'source-form:')+u for u in obligations};resources.update('building:'+u for u in retained);resources.update(['terrain:city/data/terrain.json','terrain:'+a.terrain_url])
    if not a.owned:
        assert not control.parent.exists();c=reservations.claim('retained-native-floor-'+str(uuid.uuid4()),sorted(resources),batch=a.batch,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],control,[sys.executable,__file__,*sys.argv[1:],'--owned'])
    lease=read(control);assert reservations.owns(lease)and set(lease['resources'])==resources
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256']==scope['currentManifestSHA256'];refs.append(manifest)
    assert a.terrain_url in {r['url']for r in read(manifest)['terrainPatches']}
    models={m['uid']:m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']};assert a.uid not in models and set(retained)<=set(models)
    for uid in retained:
        assert uid in obligations and not models[uid].get('verticalPlacementOffsetHKPD',0)
    cached=take(a.source_terrain,BASE/a.source_terrain/'summary.json');assert cached['sourceSHA256ByUid'][a.uid]==source['sourceSHA256']and cached['networkDownloadBytes']==0
    for record in before['meta']['source']['nativeSources']:
        for f in record['sourceFiles']:
            p=ROOT/f['path'];assert digest(p.read_bytes())==f['sha256'];refs.append(p)
    body=take(a.buried,BASE/a.buried/(a.uid.split('/')[1]+'.json'));assert body['sourceSHA256']==source['sourceSHA256']
    original=ROOT/source['candidate']['path'];assert digest(original.read_bytes())==source['sourceSHA256'];refs.append(original);tri=decode_original_world_triangles(original.read_bytes());assert len(tri)==source['triangles']
    captured=next(r for r in take(a.runtime,HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']if r['uid']==a.uid);literal=np.asarray(captured['position']).reshape(-1,3)[np.asarray(captured['index']).reshape(-1,3)]
    rows=[r for r in body['buriedFaces']if r['upward']];assert rows
    ids=[r['faceIndex']for r in rows];assert len(ids)==len(set(ids))
    assert all(np.array_equal(literal[r['faceIndex']],np.asarray(r['vertices']))for r in rows)
    floors=tri[ids];assert np.all(np.cross(floors[:,1]-floors[:,0],floors[:,2]-floors[:,0])[:,1]>0)
    assert np.all(np.abs(floors[:,:,[0,2]]-literal[ids][:,:,[0,2]])<.002)
    builder=module('retained_floor_validator',HERE/'resolve_pass_indexed_parent_clipping_v2.py');parentpath=ROOT/'3d-viewer/city/data/terrain.json';parent=take(a.runtime,parentpath);bounds=builder.extent(before['coarseCells'],parent)
    assert tri[:,:,0].min()>=bounds[0]and tri[:,:,0].max()<=bounds[2]and tri[:,:,2].min()>=bounds[1]and tri[:,:,2].max()<=bounds[3]
    positions=np.asarray(before['nativeMesh']['position'],dtype='<f4');index=np.asarray(before['nativeMesh']['index']).reshape(-1,3);terrain=positions.astype('<f8').reshape(-1,3)[index]
    after,proof=inset(terrain,floors);assert len(after)<=25000 and proof['sourceClearanceM']==.05 and proof['coreMarginM']==1. and proof['returnWidthM']==3.
    changed=set(proof['changedTerrainFaceIndices']);assert changed
    lineage=proof['outputLineage'];assert len(lineage)==len(after)
    unchanged={r['parentFace']:i for i,r in enumerate(lineage)if r['kind']=='unchanged'}
    assert set(unchanged)==set(range(len(terrain)))-changed
    assert all(np.array_equal(after[i],terrain[parent])for parent,i in unchanged.items())
    assert all(after[i,:,1].min()>=1.2 for i,r in enumerate(lineage)if r['kind']in ['ramp-plane-core','ramp-derived-return'])
    assert {i for i,t in enumerate(terrain)if t[:,1].max()<1.2}<=set(unchanged)
    patch=copy.deepcopy(before);patch['nativeMesh']['position']=after.reshape(-1).tolist();patch['nativeMesh']['index']=list(range(after.size//3));patch['meta']['targetUids']=sorted(set(retained)|{a.uid})
    binding=dict(uid=a.uid,sha256=source['sourceSHA256'],sourceFaceIndices=ids,sourceFaceSHA256=digest(floors.astype('<f8').tobytes()),previousNativeTerrain=dict(url=a.terrain_url,sha256=oldsha),policy=proof['policy'])
    for metadata in [patch['nativeMesh']['source'],patch['meta']['source']]:metadata['authoredSourceFloorReturn']=binding
    out.mkdir();local.mkdir();save(out/'inset-proof.json.gz',proof);save(out/'source-floor-facets.json',dict(uid=a.uid,sourceSHA256=source['sourceSHA256'],faces=[dict(face=i,vertices=tri[i].tolist())for i in ids],sourceGeometryChanges=0,architectureReview=False))
    save(out/'input-rendered-equivalence.json',dict(oldTerrainSHA256=oldsha,oldRenderedPositionSHA256=digest(positions.tobytes()),completeOldIndexedFaces=len(terrain),unchangedOriginalFaces=len(unchanged),unchangedBelowMinimumOriginalFaces=int(sum(t[:,1].max()<1.2 for t in terrain)),onlyBoundedSourceFloorReturn=True,sourceGeometryChanges=0,qualification='Original installed mesh interpreted with the same Float32 position attribute as production. Every uncut indexed source triangle is numerically identical; original below-floor seabed remains. New derived land obeys existing1.2m floor; no global water clamp or source model edit.'))
    from native_patch_resolution import projected_context
    from float32_coverage import approve_roundoff
    _,polygons,_,_=projected_context(patch,bounds)
    if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:save(out/'numerical-coverage.json',approve_roundoff(patch,bounds))
    overlap=module('retained_floor_current_overlap',HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=out;overlap.overlap_proof(patch,refs)
    candidate=local/'candidate-terrain.json';save(candidate,patch);refs.append(candidate)
    status='private-terrain-validator-passed';failure=None
    try:builder.validate_patch(patch,parent)
    except AssertionError as exc:status='private-terrain-validator-failed';failure=str(exc);save(out/'validation-failure.json',dict(error=failure,acceptanceGranted=False))
    replacements=[dict(url=a.terrain_url,path=str(oldpath.relative_to(ROOT)),sha256=oldsha,targetUids=retained)]
    result=dict(uids=[a.uid],sourceSHA256ByUid={a.uid:source['sourceSHA256']},status=status,validationFailure=failure,candidate=dict(path=str(candidate.relative_to(ROOT)),sha256=digest(candidate.read_bytes())),terrainTriangles=len(after),changedTerrainFaces=len(changed),sourceFloorFaces=len(ids),sourceGeometryChanges=0,sourcePoseChanges=0,terrainChanges=True,replacedNativeTerrain=replacements,retainedNativeTerrainTargets=retained,currentManifestSHA256=mh,physicalAcceptance=False,neighboursChecked=False,installationApproved=False,publication=False,qualification='Private derived terrain only: existing fixed-clearance lower-only source-floor kernel, unchanged source model and retained original terrain outside its bounded return. Existing Float32 overlap/coverage audit and canonical native validator applied without threshold changes. Full current/retained-native regression and actual source/browser/publication acceptance remain required.')
    save(out/'summary.json',result);save(out/'terrain-source-context.json',dict(previousNativeTerrain=replacements[0],originalSourceTerrainReceipt=str((BASE/a.source_terrain/'result.json').relative_to(ROOT)),sourceGeometryChanges=0))
    refs.extend(HERE/n for n in ['source_floor_return_with_existing_seabed_v1_20261102.py','test_source_floor_return_with_existing_seabed_v1_20261102.py','bounded_original_upward_floor_domains_v4_20261102.py','bounded_original_upward_floor_domains_v3_20261102.py','bounded_original_upward_floor_return_v3_20261102.py','exact_affine_halfplane_clip_v2_20261102.py','exact_affine_halfplane_clip_v1_20261024.py','resolve_pass_indexed_parent_clipping_v2.py','sham_shui_po_pool_shared_terrain_v2_20261016.py','native_patch_resolution.py','float32_coverage.py','exact_packed_world_geometry_20261009.py'])
    assert reservations.owns(lease)and digest(manifest.read_bytes())==mh and digest(oldpath.read_bytes())==oldsha
    module('retained_native_floor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'existing-source-floor-kernel-in-retained-native-terrain-private-trial',list(dict.fromkeys(refs)),result);print(dict(status=status,terrainFaces=len(after),changedFaces=len(changed),validationFailure=failure),flush=True)
if __name__=='__main__':main()
