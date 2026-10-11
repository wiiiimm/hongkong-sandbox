"""Freeze fresh full-cell identity and terrain routing before physical work."""
import importlib.util
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from government_georef_cell_identity import verify_files
from terrain_source_preflight import preflight,SourceSheetIndex

BATCH='government-xl-terrain-recovery-block37-current-inputs-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
BASE=ROOT/'docs/astra-city/government-import/government-xl-sustained-131-inputs-20261006'
LEASE='/tmp/xl-terrain-recovery-20261009-block37-authored-role-lease.json'

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    assert not DOC.exists()
    lease=read(LEASE);assert reservations.heartbeat(lease)['ok']
    selected=read(BASE/'check-selection.json.gz');row=next(r for r in selected['rows'] if r['uid']=='landsd/228547:0')
    final=module('block37_current_forms','xl-final-script-pass.py')
    decoder=module('block37_current_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL
    asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']
    destination=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
    tri=decoder.glb_triangles(row);low=tri.min(axis=(0,1));high=tri.max(axis=(0,1))
    forms=final.load_forms([low[0]-2,low[2]-2,high[0]+2,high[2]+2])
    form,polygon,tile=next(f for f in forms if f[0]['uid']==row['uid'])
    assert form['objectId']==228547 and form['buildingCSUID']=='3406534885P20050804'
    row={**row,'source':{'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())},
         'candidate':{**row['candidate'],'path':str(destination.relative_to(ROOT))}}
    context={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),
             'neighbourTileHashes':{t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms}}
    with connect() as c:
        c.execute('SET TRANSACTION READ ONLY')
        assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(row['uid'],)).fetchall()
        actual=c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()
        assert actual and actual[0]==row['native']['resultSha']
    manifest=ROOT/'3d-viewer/city/data/manifest.json'
    assert not any(model['uid']==row['uid'] for url in read(manifest)['officialModelCatalogues'] for model in read(ROOT/'3d-viewer'/url)['models'])
    identity=verify_files(row,context,LOCAL/'identity-precheck')
    index=ROOT/'source-scripts/city/landmark-acquisition/index.json'
    routing=preflight(row,context,SourceSheetIndex(read(index)))
    routing.update(legacyProjectionIdentity=routing['identity'],identity=identity,
                   canStartTerrainWork=identity['passed'] and routing['primarySheetIntersects'])
    refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [Path(__file__),asset,manifest,index,
          BASE/'check-selection.json.gz',HERE/'government_georef_cell_identity.py',HERE/'xl-final-script-pass.py',
          HERE/'xl-second-pass.py',HERE/'terrain_source_preflight.py']]
    save(DOC/'check-selection.json.gz',{**selected,'batch':BATCH,'rows':[row],
        'previousManifestSHA256':selected['manifestSHA256'],'manifestSHA256':digest(manifest.read_bytes())})
    save(DOC/'context.json.gz',{'rows':[context]})
    save(DOC/'indexed-preflight.json',{**routing,'currentForms':len(forms),'evidenceRefs':refs,
        'installationApproved':False,'publication':False,'sourceGeometryChanges':0})
    print(json.dumps({'uid':row['uid'],'identityPassed':identity['passed'],'identityReasons':identity['reasons'],
        'currentForms':len(forms),'canStartTerrainWork':routing['canStartTerrainWork'],
        'primarySheet':routing['primarySheet'],'indexedSheets':routing['indexedSheets']}),flush=True)

if __name__=='__main__':main()
