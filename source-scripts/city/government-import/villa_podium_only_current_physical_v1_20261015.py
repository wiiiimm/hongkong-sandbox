"""Diagnose unchanged Villa podium alone with all current basic neighbours retained."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest, connect, reservations, NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-villa-podium-only-current-physical-v1-20261015'
DOC=BASE/BATCH
LOCAL=HERE/'local'/BATCH
PLATFORM='landsd/89917:0'
TOWERS=[]
UIDS={PLATFORM}|{'landsd/'+str(n)+':0' for n in TOWERS}
PRIOR=BASE/'government-xl-villa-complete-original-current-physical-v1-20261010'
TERRAIN_SHA=read(BASE/'government-xl-villa-five-float32-bounded-terrain-gap-infill-proposal-v1-20261010/terrain-candidates.json')[0]['sha256']

def module(name,filename):
    s=importlib.util.spec_from_file_location(name,HERE/filename)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))

def main():
    assert not DOC.exists() and not LOCAL.exists()
    manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest)
    terrain=read(BASE/'government-xl-villa-five-float32-bounded-terrain-gap-infill-proposal-v1-20261010'/'terrain-candidates.json');assert len(terrain)==1
    patch=terrain[0];assert patch['sha256']==TERRAIN_SHA
    assert ref(ROOT/patch['path'])['sha256']==TERRAIN_SHA
    current=read(manifest);assert not patch.get('replaces');assert start['sha256']=='9fa4035f31a218cec04f418b83e7545148f70e4fa966287e7b4eb67d61007c56'
    final=module('villa_five_current_forms','xl-final-script-pass.py')
    forms=final.load_forms(patch['bounds']);by_uid={f['uid']:(f,t) for f,_,t in forms}
    assert UIDS<=set(by_uid) and len(by_uid)==len(forms)
    installed={m['uid'] for u in current['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/u)['models']}
    assert not UIDS&installed
    census=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v6-20261015'
    receipt=read(census/'result.json')
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
    inventory=read(census/'inventory.json.gz');assert ref(census/'inventory.json.gz') in receipt['evidenceRefs']
    assert inventory['successfullyCapturedActors']==6662 and not inventory['errors']
    for p,h in inventory['inputHashes'].items():assert ref(ROOT/p)['sha256']==h,p
    census_input=read(census/'input.json.gz');assert census_input['currentManifest']==start
    # Patch replaces these whole parent cells. The declared extent must include them exactly.
    base=read(ROOT/'3d-viewer/city/data/terrain.json');g=base['meta']['georef'];origin=base['meta']['origin'];i0,j0,i1,j1=read(ROOT/patch['path'])['coarseCells']
    coarse=[g['bE']+i0*g['aE']-origin[0],origin[1]-(g['bN']+j0*g['aN']),g['bE']+i1*g['aE']-origin[0],origin[1]-(g['bN']+j1*g['aN'])]
    assert coarse==patch['bounds'],(coarse,patch['bounds'])
    nominated=[]
    for actor in inventory['rows']:
        bounds=[actor[k] for k in ['completeLiteralBounds','completeLeftAssociatedF32Bounds','completeBalancedF32Bounds']]
        touches=any(not(b[1][0]<coarse[0] or b[0][0]>coarse[2] or b[1][2]<coarse[1] or b[0][2]>coarse[3]) for b in bounds)
        if touches:nominated.append(actor['uid'])
    allforms=census_input['currentAllNativeSourceForms']
    for uid in nominated:
        if uid not in by_uid:
            f=allforms[uid];matches=[t for t in census_input['currentNativeViewerTileHashes'] if any(b['uid']==uid for b in read(ROOT/t)['buildings'])];assert len(matches)==1
            t=matches[0].removeprefix('3d-viewer/');forms.append((f,final.form_polygon(f),t));by_uid[uid]=(f,t)
    resource_scope=set(by_uid)|UIDS
    keys=[('building:' if u.startswith('landsd/') else 'foreign-form:')+u for u in sorted(resource_scope)]
    keys+=['terrain-patch:'+PLATFORM]
    claim=reservations.claim('villa-five-original-diagnostic-'+str(uuid.uuid4()),keys,batch=BATCH,ttl=3600)
    assert claim['ok'],claim
    lease=json.loads(json.dumps(claim['reservation'],default=str));save(LOCAL/'reservation.json',lease)
    try:
        rows=[read(PRIOR/'selection.json.gz')['rows'][0]]
        for n in TOWERS:
            old=BASE/f'government-xl-villa-four-current-identity-{n}-v1-20261010'
            rows.append(read(old/'selection.json.gz')['rows'][0])
        assert {r['uid'] for r in rows}==UIDS
        entries=[];source_forms={};originals={};source_refs=[]
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY')
            for r in rows:
                assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()==(r['native']['resultSha'],)
                oldpath=ROOT/r['candidate']['path'];raw=oldpath.read_bytes()
                assert digest(raw)==r['sourceSHA256']==r['candidate']['entry']['sha256']
                tri=decode_original_world_triangles(raw);assert len(tri)==r['triangles']==r['native']['model']['triangles']
                originals[r['uid']]=tri;source_refs.append(ref(oldpath))
                f,t=by_uid[r['uid']];assert r['source']['building']==f,'Current source form differs; fresh identity required'
                e=dict(r['candidate']['entry'])
                assert not e.get('suppressesBuildingUids') and not e.get('footprintScope') and not e.get('supportDependencies')
                assert e['recordedBaseHeight']==f['baseHeightHKPD'] and e['recordedTopHeight']==f['topHeightHKPD']
                # Display metadata only; no source bytes, vertices or pose edits.
                e['proceduralWindows']=False
                dst=LOCAL/e['asset'];dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
                assert ref(dst)['sha256']==r['sourceSHA256']
                r['candidate']={**r['candidate'],'entry':e,'path':str(dst.relative_to(ROOT))}
                r['source']=dict(building=f,tile=t,tileSHA256=digest((ROOT/'3d-viewer'/t).read_bytes()))
                entries.append(e);source_forms[r['uid']]=r['source']
        catalogue=read(HERE/'local'/PRIOR.name/'catalogue.json')
        catalogue.update(models=entries,counts={'packedModels':1},area='Unchanged Villa Premiere podium only; four existing basic towers retained')
        save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']))
        save(LOCAL/'source-forms.json',source_forms)
        save(DOC/'selection.json.gz',dict(rows=rows,batch=BATCH,manifestSHA256=start['sha256']))
        save(DOC/'terrain-candidates.json',terrain)
        save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,patchIndexes=[0],existingNative=f['uid'] in installed or bool(f.get('modelGeometry'))) for f,_,_ in forms],inputHashes={str((ROOT/'3d-viewer'/t).relative_to(ROOT)):digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms},candidateIds=sorted(UIDS),patches=terrain))
        neighbour_inputs=read(DOC/'neighbour-inputs.json.gz');neighbour_inputs.update(explicitNativeUIDs=sorted(nominated),globalNativeFormCensus=str((census/'input.json.gz').relative_to(ROOT)),globalNativeFormCensusSHA256=ref(census/'input.json.gz')['sha256']);save(DOC/'neighbour-inputs.json.gz',neighbour_inputs)
        save(DOC/'full-current-scope.json',dict(currentActors=6662,wholeParentBounds=coarse,nominatedNativeUIDs=sorted(nominated),ordinaryAndNativeForms=len(forms),wholeUnusedPositionsAndThreeModes=True))
        def call(args,allowed=(0,)):
            assert reservations.owns(lease) and ref(manifest)==start
            assert subprocess.run(args,cwd=ROOT,env={**os.environ,'CHROME_PATH':'/opt/google/chrome/chrome'}).returncode in allowed
            assert reservations.owns(lease) and ref(manifest)==start
        rel=lambda p:str(p.relative_to(ROOT))
        call(['node',str(HERE/'acceptance-metrics.mjs'),'--selection',rel(DOC/'selection.json.gz'),'--candidates',rel(LOCAL),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'metrics.json'),'--geometry-out',rel(LOCAL/'runtime-geometry.json.gz')])
        call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',rel(LOCAL),'--source-forms',rel(LOCAL/'source-forms.json'),'--terrain-candidates',rel(DOC/'terrain-candidates.json'),'--out',rel(DOC/'validation.json')],(0,1))
        call(['node',str(HERE/'check-neighbours.mjs'),rel(DOC)+'/'])
        call(['node',str(HERE/'villa_full_native_neighbours_v4_20261015.mjs'),rel(DOC)+'/'])
        runtime=read(LOCAL/'runtime-geometry.json.gz');assert len(runtime['rows'])==1
        foundations=[]
        for g in runtime['rows']:
            a=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
            assert a.shape==originals[g['uid']].shape and np.max(np.abs(a-originals[g['uid']]))<=1e-9
            ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3)
            f=by_uid[g['uid']][0];ctx=final.foundation_context(a,ground,Polygon(f['rings'][0],f['rings'][1:]))
            foundations.append(dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],foundation=ctx,strictFoundationAccepted=ctx['completeTerrainTriangles']==ctx['triangles'] and not ctx['fullyBuriedUpwardTriangles'] and ctx['fullyBuriedAreaFraction']==0))
        save(DOC/'foundation.json',dict(rows=foundations,sourceGeometryChanges=0,publication=False))
        neighbours=read(DOC/'neighbour-checks.json');native=read(DOC/'native-neighbour-checks.json')
        validation=read(DOC/'validation.json');metrics=read(DOC/'metrics.json')
        result=dict(uids=sorted(UIDS),manifestSHA256=start['sha256'],completeOriginalFaces=sum(len(x) for x in originals.values()),sourceSHA256s={r['uid']:r['sourceSHA256'] for r in rows},wholeFoundations=[dict(uid=f['uid'],passed=f['strictFoundationAccepted']) for f in foundations],currentNeighbourForms=len(forms),remainingBasicNeighbourReasons=[dict(uid=r['uid'],reasons=r['reasons']) for r in neighbours['rows'] if r['reasons']],retainedNativeBlocked=native['blocked'],retainedNativeResolved=native['resolved'],rawRuntimeValidation=validation,rawMetrics=metrics,identityAcceptanceRequired=True,completeCoupledComponentSupportRequired=False,wholeContinuousFacetClearanceRequired=True,publication=False,currentAcceptancePassed=False,newlyInstalled=0,aiGeometryModellingRequired=False,humanDecisionRequired=False,humanStatus='held-for-compute',qualification='One complete unchanged government podium diagnosed with all four existing basic towers retained as ordinary neighbours on the conservative source-bound terrain ceiling with two literal prior-ground canopy preservation regions. Raw runtime/basic/native/foundation outcomes retained; complete fresh identities, continuous facets and all-component original/literal support still required. No actor is removed or exempted.')
        save(DOC/'diagnostic.json',result)
        refs=[Path(__file__),census/'result.json',census/'inventory.json.gz',census/'input.json.gz',HERE/'villa_full_native_neighbours_v4_20261015.mjs',ROOT/'3d-viewer/city/procedural-footprint-corrections.js',BASE/'government-xl-villa-five-float32-bounded-terrain-gap-infill-proposal-v1-20261010'/'result.json',manifest,ROOT/patch['path'],LOCAL/'runtime-geometry.json.gz',LOCAL/'catalogue.json',LOCAL/'source-forms.json']+[ROOT/r['path'] for r in source_refs]
        refs.extend(LOCAL/e['asset'] for e in entries)
        refs.extend(HERE/n for n in ['acceptance-metrics.mjs','check-neighbours.mjs','check-native-neighbours.mjs','xl-final-script-pass.py','exact_packed_world_geometry_20261009.py'])
        refs.append(HERE.parent/'building-batch/validate_candidates.mjs')
        for p,h in runtime['inputHashes'].items():assert ref(ROOT/p)['sha256']==h;refs.append(ROOT/p)
        assert ref(manifest)==start and reservations.owns(lease)
        module('villa_five_diagnostic_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-podium-only-and-retained-basic-towers-v1',sorted(set(refs)),result)
        print(json.dumps(dict(completeOriginalFaces=result['completeOriginalFaces'],basicNeighbourHolds=len(result['remainingBasicNeighbourReasons']),failedWholeFoundations=[r['uid'] for r in result['wholeFoundations'] if not r['passed']],publication=False)),flush=True)
    finally:
        assert reservations.release(lease)['ok']

if __name__=='__main__':main()
