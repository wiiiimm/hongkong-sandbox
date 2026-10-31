"""Persist exact refreshed Dragon source work and unresolved questions; no approval."""
from datetime import datetime,timezone
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
PREFIX='government-xl-dragon-after-podium323546-'


def main():
    base=ROOT/'docs/astra-city/government-import';batch=PREFIX+'progress-v1-20261026';out=base/batch
    assert not out.exists();refs=[Path(__file__)];completed=[]
    for folder in sorted(base.glob(PREFIX+'*')):
        if folder.name==batch or not(folder/'result.json').exists():continue
        r,_=authenticate(folder);refs.append(folder/'result.json');completed.append(dict(batch=folder.name,jobId=r['jobId']))
    assert len(completed)>=10
    current=read(ROOT/'3d-viewer/city/data/manifest.json');manifest_sha=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes());refs.append(ROOT/'3d-viewer/city/data/manifest.json')
    directory_sha='7fc427a3e914ac1f5a2e3c6ecaa2baa0ca41661b69d21e97eecf0f249c1238ae'
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        exact=db.execute('SELECT model_id,cache_key,viewer_uid,triangles,sheet,source_state FROM astra_modelling.native_model_sizes WHERE run_id=%s AND model_id LIKE %s',(NATIVE_RUN,'B3789415834%')).fetchall()
        companions=db.execute('SELECT viewer_uid,model_id,cache_key,triangles,sheet,source_state FROM astra_modelling.native_model_sizes WHERE run_id=%s AND viewer_uid=ANY(%s)',(NATIVE_RUN,['landsd/95231:0','landsd/97448:0','landsd/97821:0'])).fetchall()
        directories=db.execute("SELECT cache_key,index_sha,result->'models' FROM astra_modelling.city_source_directories WHERE sheet=%s AND result->>'directorySHA256'=%s",('11-SE-6C',directory_sha)).fetchall()
    import json
    directory_results=[dict(directoryCacheKey=k,indexSHA256=h,completeIndexedModels=len(models),exactGeoRefPrefixMentioned='3789415834'in json.dumps(models))for k,h,models in directories]
    assert len(directory_results)==2 and all(r['completeIndexedModels']==237 and not r['exactGeoRefPrefixMentioned']for r in directory_results)and not exact
    lookup=dict(checkedAtUTC=datetime.now(timezone.utc).isoformat(),nativeRun=NATIVE_RUN,exactOpenStructureGeoRefPrefix='B3789415834',exactNativeModelIndexRows=exact,companionNativeRows=[dict(zip(['uid','modelId','cacheKey','triangles','sheet','sourceState'],r))for r in companions],pinnedSheet='11-SE-6C',pinnedDirectorySHA256=directory_sha,pinnedDirectoryChecks=directory_results,qualification='Only the exact pinned prepared native index and historical237-model sheet directories were searched. No current-provider absence, corruption, different-revision absence, source-body containment, common property identity or permission to suppress a BASIC actor is inferred.')
    save(out/'source-lookup.json',lookup)
    foreign=read(base/(PREFIX+'foreign-v1-20261026')/'summary.json');positive=[dict(uid=r['uid'],foreignUid=r['foreignUid'],modes=r['modes'])for r in foreign['rows']if any(m['positiveContactPairs']for m in r['modes'])]
    images=[];folder=base/(PREFIX+'private-diagnostic-v1-20261026')/'1280'
    for uid in ['232428','226794']:
        for time in ['1500','2200']:
            path=folder/('staged-landsd-'+uid+'-0-1280-'+time+'-canvas.png')
            assert path.exists();refs.append(path);images.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    result=dict(uids=['landsd/226794:0','landsd/232428:0'],completed=completed,currentManifestSHA256=manifest_sha,fullXLCounts=dict(total=521,installedVerified=383,remaining=138),currentNativeActors=6962,sourceLookup=lookup,positiveBasicContactRows=positive,desktopDiagnosticImagesActuallyOpenedByROOT=images,desktopVisualAcceptance=False,
      remainingWork=[
       'Podium323546/210501/210742 installation15ff826d2 already PUSHED. Do not reinstall. Fresh6962inventory4379ce1ee60a365779154d41433cccc464aee1700923756c50a153bb18d00f10 and exact138inventory5179d959c2e4b0d433eb7d3325acc5aea31f6ff7f5f7d40b39e998c455602bc2 preserve full521/two nullviewerUID source keys.',
       'Dragon fresh source-ground/attributes/identity/scope/foreign/4mode foundations/pair/root paths complete. Both originals0whole/0upward burial in all4modes. Strict support remainsFALSE59strict/40unresolved; all40 have freshly recomputed finite root paths in every mode,0disconnected/0endpointovershoot. This is not full support/physical acceptance.',
       'Raw tower identity fails isolated whole GeoRefcell coverage; prior exact TWO-source cell proof exists at government-xl-dragon-peak-two-original-identity-context-v1-20261025 and requires current input binding. Podium raw93.197percent coverage and unrelated-overlap failures remain. No global95percent or unrelated-overlap limit change. Tower/podium have distinct BuildingIDs and distinct official BuildingStructureIDs756403/587906; do not infer common ownership from name or contact.',
       'Fresh source scope includes10/13 forms and0 current installed native candidates againstall6962bounds. Podium has positive contacts with FIVEexternalbasics95231/97448/97821/232806/233209 plus current tower226794fallback. Keep every21pair before/4source stream result. No proxy contact is silently dropped or called collision-free.95231original10faces is prepared and may be acquired if needed;97448/97821have no prepared exact viewer match. Exact GeoRef3789415834 is absent from237-model pinned11-SE-6C directory/index only; current provider absence is unproved.',
       'Private proposed tower->originalpodium preview uses selected_original_scoped_model_only_diagnostic_browser_v1_20261026.py and port4177, no terrain edits. Check ACTUAL worker handle73806/PID before polling or restarting. Its lease/bounded runner owns complete current scope. Source flags remainFALSE; no physical/visual/identity approval. ROOT opened all4desktop full frames: tower roof/most balcony facade visible but podium partly hidden by foreground BASIC neighbours. Do NOT accept obscured podium interfaces as inspected. Need alternative/family-height camera context for podium before visual acceptance; use new producer version rather than edit frozen/live V1.',
       'After preview completion preserve raw results, inspect all mobile frames and any actually provided joint exports, resolve bounded source identity/neighbour roles and complete source/podium clearance. No original geometry edits, optimisation, source suppression, shared4176restart or main merge. No human decision or AI geometry modelling requested. Do not mark either source corrupt or permanently rejected from these diagnostics.'
      ],heldForHumanDecision=False,heldForAIProcessing=False,heldForComputeAndCode=True,installationApproved=False,publication=False,newlyInstalled=0,permanentRejection=False,sourceGeometryChanges=0,aiGeometryModelling=False,scriptExternalAICalls=0)
    save(out/'remaining-work.json',result)
    refs.extend([HERE/'selected_original_scoped_model_only_diagnostic_browser_v1_20261026.py',base/'government-xl-after-tvb-next-three-pinned-directories-v1-20261025/result.json'])
    module('dragon_progress_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'exact-original-refreshed-source-progress-and-actionable-review-obligations',refs,result)
    print(dict(completed=len(completed),newlyInstalled=0,XLInstalled=383,XLUnfinished=138),flush=True)

if __name__=='__main__':main()
