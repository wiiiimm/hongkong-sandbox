"""Current exact original Garden Terrace identities and indexed terrain route, no acceptance."""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from routed_original_cell_identity import verify_files
from terrain_source_preflight import preflight,SourceSheetIndex
BATCH='xl-terrain-recovery-20261009-222781-current-inputs-v2'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
LOCAL=HERE/'local'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-222781-source-inputs/source-inputs.json'
LEASE='/tmp/xl-terrain-recovery-20261009-222781-lease.json'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    assert not DOC.exists();lease=read(LEASE);assert reservations.heartbeat(lease)['ok']
    final=module('rooftop_current_forms','xl-final-script-pass.py');decoder=module('rooftop_current_decoder','xl-second-pass.py');decoder.LOCAL=LOCAL
    manifest=ROOT/'3d-viewer/city/data/manifest.json';index=ROOT/'source-scripts/city/landmark-acquisition/index.json'
    current_sha=digest(manifest.read_bytes());assert current_sha=='58ea0aefb25293dfc14fd2cf27a6bcc29b5f8fd427d1a8eb5ad893b18e6bdbb4'
    installed={m['uid'] for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT/'3d-viewer'/url)['models']}
    rows=[];contexts=[];results=[];refs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [Path(__file__),INPUT,manifest,index,HERE/'government_georef_cell_identity.py',HERE/'routed_original_cell_identity.py',HERE/'component_type_resolution.py',HERE/'xl-final-script-pass.py',HERE/'xl-second-pass.py',HERE/'terrain_source_preflight.py']]
    for original in read(INPUT)['sources']:
        row=dict(original);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256']
        destination=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
        tri=decoder.glb_triangles(row);low=tri.min(axis=(0,1));high=tri.max(axis=(0,1));forms=final.load_forms([low[0]-2,low[2]-2,high[0]+2,high[2]+2]);form,_,tile=next(f for f in forms if f[0]['uid']==row['uid']);assert form['buildingCSUID']==row['source']['building']['buildingCSUID']
        row.update(source={'building':form,'tile':tile,'tileSHA256':digest((ROOT/'3d-viewer'/tile).read_bytes())},candidate={**row['candidate'],'path':str(destination.relative_to(ROOT))})
        context={'uid':row['uid'],'sourceSHA256':row['sourceSHA256'],'identity':final.identity_context(row,tri,forms),'neighbourTileHashes':{t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in forms}}
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');actual=c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone();assert actual and actual[0]==row['native']['resultSha']
        assert row['uid'] not in installed
        identity=verify_files(row,context,LOCAL/('identity-'+row['uid'].split('/')[1].replace(':','-')))
        routing=preflight(row,context,SourceSheetIndex(read(index)));routing.update(legacyProjectionIdentity=routing['identity'],identity=identity,canStartTerrainWork=identity['passed'] and routing['primarySheetIntersects'],uid=row['uid'],currentForms=len(forms))
        rows.append(row);contexts.append(context);results.append(routing);refs.append({'path':str(asset.relative_to(ROOT)),'sha256':digest(raw)})
        print(json.dumps({'uid':row['uid'],'identityPassed':identity['passed'],'identityReasons':identity['reasons'],'currentForms':len(forms),'canStartTerrainWork':routing['canStartTerrainWork']}),flush=True)
    assert digest(manifest.read_bytes())==current_sha and reservations.owns(lease)
    save(DOC/'check-selection.json.gz',{'batch':BATCH,'rows':rows,'manifestSHA256':current_sha});save(DOC/'context.json.gz',{'rows':contexts});save(DOC/'indexed-preflight.json',{'rows':results,'manifestSHA256':current_sha,'evidenceRefs':refs,'installationApproved':False,'publication':False,'sourceGeometryChanges':0})
if __name__=='__main__':main()
