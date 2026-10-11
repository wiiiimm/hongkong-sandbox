"""Fresh complete original/current/provider input capture; identity only."""
import shutil,uuid,numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files as raw_verify
from man_hei_current_bound_mandatory_platform_identity_20261010 import DOC,UID,PLATFORM,MODELS,native_rows,verify_native_rows,module,stream_pin,WHERE
from man_hei_dependent_platform_current_identity_20261010 import DOC as DEPENDENCY
LOCAL=HERE/'local'/DOC.name;BASE=DOC.parent
INPUTS=[BASE/'government-xl-man-fuk-nine-current-identity-75694-0-20261010/selection.json.gz',DEPENDENCY/'selection.json.gz']
PRIMARY=BASE/'government-xl-man-hei-man-fuk-primary-platform-context-20261010'

def main():
    assert not DOC.exists()
    claim=reservations.claim('manhei-current-mandatory-platform-'+str(uuid.uuid4()),['building:'+u for u in MODELS],batch=DOC.name,ttl=3600);assert claim['ok'],claim;lease=claim['reservation']
    try:
        manifest=ROOT/'3d-viewer/city/data/manifest.json';mraw=manifest.read_bytes();msha=digest(mraw)
        assert msha==read(DEPENDENCY/'current-inputs.json.gz')['manifestSHA256']
        rows=[r for p in INPUTS for r in read(p)['rows'] if r['uid'] in MODELS];assert len(rows)==2 and {r['uid'] for r in rows}==set(MODELS)
        worlds={};pins={}
        for r in rows:
            mid,sha,count=MODELS[r['uid']];raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==sha and r['modelId']==mid
            worlds[r['uid']]=decode_original_world_triangles(raw);pins[r['uid']]=stream_pin(raw,mid,count)
        final=module('manhei_fresh_complete_actual_forms','xl-final-script-pass.py');tri=np.concatenate(list(worlds.values()));lo,hi=tri.min((0,1)),tri.max((0,1))
        loaded=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);forms=[b for b,_,_ in loaded];hashes={u:digest((ROOT/'3d-viewer'/u).read_bytes()) for _,_,u in loaded}
        contexts=[];raw_proofs={}
        for r in rows:
            own=[v for v in loaded if v[0]['uid']==r['uid']];assert len(own)==1;b,_,tile=own[0]
            assert b['buildingCSUID']==r['source']['building']['buildingCSUID'];r['source']={'building':b,'tile':tile,'tileSHA256':hashes[tile]}
            ctx={'uid':r['uid'],'sourceSHA256':r['sourceSHA256'],'identity':final.identity_context(r,worlds[r['uid']],loaded),'neighbourTileHashes':hashes};contexts.append(ctx)
            raw_proofs[r['uid']]=raw_verify(r,ctx,LOCAL/r['uid'].split('/')[1])
        p=next(r for r in rows if r['uid']==PLATFORM);pc=next(c for c in contexts if c['uid']==PLATFORM)
        assert p==read(DEPENDENCY/'selection.json.gz')['rows'][0] and pc==read(DEPENDENCY/'context.json.gz')['rows'][0]
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');native=native_rows(c);verify_native_rows(native)
            for r in rows:
                n=next(n for n in native if n['model']['modelId']==r['modelId'])
                assert r['native']['model']==n['model'] and r['native']['resultSha']==n['resultSHA256'] and r['native']['cacheKey']==n['sourceKey'].rsplit('/',1)[0]
                assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()==(r['native']['resultSha'],)
        DOC.mkdir(parents=True);query=module('manhei_fresh_exact_provider','xl-aqua-marine-fresh-overhead-source-context-v3-20261010.py');query.DOC=DOC
        primary=query.query(0,WHERE,'exact-current-primary',True);relations=query.query(1002,WHERE,'exact-current-structure-relations');assert len(primary)==2 and not relations
        for name in ['ha-man-hei-block-h.pdf','ha-man-hei-block-h.pdf.request.json','ha-man-hei-block-h.pdf.text.json','ha-man-hei-block-h.pdf.page-1.png']:shutil.copyfile(PRIMARY/name,DOC/name)
        save(DOC/'source-lookup.json.gz',{'rows':native});save(DOC/'complete-original-stream-pins.json.gz',pins)
        save(DOC/'current-inputs.json.gz',{'manifestSHA256':msha,'forms':forms,'tileHashes':hashes})
        save(DOC/'selection.json.gz',{'rows':rows,'manifestSHA256':msha});save(DOC/'context.json.gz',{'rows':contexts});save(DOC/'raw-independent-original-identities.json.gz',raw_proofs);(DOC/'captured-manifest.json').write_bytes(mraw)
        (DOC/'README.md').write_text('Fresh identity input only. Complete2286-face/six-part ManHeiTower and10661-face/93-part originalManFukplatform. Raw standalone94.8074% held; genuine partialfloor gaps retained. Independent platform identity must freshly replay the reviewed named ManOi relationship and actualuniqueinstalled2160-faceoriginal. Completecurrentforms/tiles, source-nativeversions and BOTH memberships, allroot/BIN/attribute/world streams and exactprimaryActiveTower/Podium records are bound. NoOP/sourceownershiplegal/support/collision/terrain exemption or standaloneimport.\n')
        refs=INPUTS+[Path(__file__),HERE/'man_hei_current_bound_mandatory_platform_identity_20261010.py',HERE/'man_hei_named_mandatory_original_platform_identity_20261010.py',HERE/'test_man_hei_named_mandatory_original_platform_identity_20261010.py',HERE/'man_hei_dependent_platform_current_identity_20261010.py',HERE/'tung_sing_current_bound_identity_20261010.py',HERE/'xl-aqua-marine-fresh-overhead-source-context-v3-20261010.py',BASE/'government-xl-man-hei-dependent-platform-current-proof-v1-20261010/result.json',BASE/'government-xl-man-hei-mandatory-original-platform-source-proposal-20261010/result.json']
        refs += [ROOT/r['candidate']['path'] for r in rows]+[ROOT/'3d-viewer'/u for u in hashes]+[p for p in LOCAL.rglob('*') if p.is_file()]
        assert manifest.read_bytes()==mraw and reservations.owns(lease)
        result=module('manhei_complete_input_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'complete-man-hei-mandatory-original-platform-current-inputs-v1',refs,dict(uids=[UID,PLATFORM],identityAccepted=False,physicalAccepted=False,manifestSHA256=msha,completeOriginalFaces=[2286,10661],completeOriginalParts=[6,93],mandatoryOriginalRuntimeUIDs=[UID,PLATFORM],standaloneOriginalImportAccepted=False,bothNativeRunMembershipsVerified=True,rawIndependentOriginalReasons={u:p['reasons'] for u,p in raw_proofs.items()},currentBindingRequired=True))
        print({'jobId':result['jobId'],'manifestSHA256':msha,'forms':len(forms)},flush=True)
    finally:assert reservations.release(lease)['ok']

if __name__=='__main__':main()
