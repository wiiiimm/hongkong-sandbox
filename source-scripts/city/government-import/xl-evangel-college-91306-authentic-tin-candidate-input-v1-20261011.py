"""Fresh 17-actor terrain-candidate input, no terrain or model mutation.

Run only after the distinct post-Elements raw/typed identity captures complete.
The old four-world POSITION streams are reused only for unchanged source bounds;
their historical drawn terrain is never used as current candidate ground.
"""
import importlib.util,json,sys,subprocess,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011 import verify_files,RAW,UID,SOURCE_SHA
BASE=ROOT/'docs/astra-city/government-import'
IDENTITY=BASE/'government-xl-evangel-college-91306-post-elements-current-wing-extension-identity-v2-20261011'
POSITION=BASE/'government-xl-evangel-college-91306-current-actual-ground-capture-v1-20261011'
BATCH='government-xl-evangel-college-91306-authentic-tin-candidate-input-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
EXPECTED_FORMS={'way/134495631:0','landsd/88878:0','landsd/88881:0','landsd/89810:0','landsd/91306:0','landsd/91572:0','landsd/103726:0','landsd/103730:0','landsd/114173:0','landsd/212952:0','landsd/266451:0','landsd/268000:0','landsd/290878:0','landsd/290879:0','landsd/339808:0','landsd/340033:0','landsd/342177:0'}
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def nominated_region(row):
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');second=module('evangel_candidate_extent','xl-second-pass.py')
 bounds=np.asarray(row['native']['model']['worldBounds'],dtype='<f8');assert bounds.shape==(2,3)
 data=read(POSITION/'complete-current-actual-source-and-ground.json.gz');assert data['sourceSHA256']==SOURCE_SHA
 all_bounds=np.asarray([data['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],*data['completeWholeUnusedVertexBounds']],dtype='<f8');assert all_bounds.shape==(4,2,3)and np.isfinite(all_bounds).all()
 assert data['completeOriginalPOSITIONProof']['originalWholeSourceBounds']==bounds.tolist()
 cells=second.resolution.rectangle_for(bounds.tolist(),parent);region=second.resolution.extent(cells,parent)
 assert all(region[0]<=b[0,0]and b[1,0]<=region[2]and region[1]<=b[0,2]and b[1,2]<=region[3]for b in all_bounds)
 return cells,region,all_bounds.tolist()
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 receipt=read(IDENTITY/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for pin in receipt['evidenceRefs']:assert ref(ROOT/pin['path'])==pin
 selected=read(IDENTITY/'selection.json.gz');row=selected['rows'][0];assert len(selected['rows'])==1 and row['uid']==UID and row['sourceSHA256']==SOURCE_SHA and row['currentReview']is None
 context=read(IDENTITY/'context.json.gz')['rows'];assert len(context)==1
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==selected['manifestSHA256']
 catalogue_refs=[ref(ROOT/'3d-viewer'/u)for u in json.loads(before)['officialModelCatalogues']]
 cells,bounds,all_position_bounds=nominated_region(row);forms=module('evangel_candidate_complete_current_forms','xl-final-script-pass.py').load_forms(bounds)
 assert len(forms)==17 and {b['uid']for b,_,_ in forms}==EXPECTED_FORMS
 tile_hashes={p:digest((ROOT/'3d-viewer'/p).read_bytes())for _,_,p in forms}
 registry=[m for p in catalogue_refs for m in read(ROOT/p['path'])['models']];assert len(registry)==len({m['uid']for m in registry})and UID not in {m['uid']for m in registry}
 identity=verify_files(row,context[0],LOCAL/'identity');assert identity==read(IDENTITY/'identity.json')and identity['passed']and identity['reasons']==[]
 save(DOC/'check-selection.json.gz',selected);save(DOC/'context.json.gz',dict(rows=context));save(DOC/'owned-source-identity.json',identity)
 save(DOC/'complete-protected-current-forms.json.gz',dict(rows=[dict(building=b,existingNative=b['uid']in {m['uid']for m in registry},tile=p)for b,_,p in forms],completeNativeUIDs=sorted(m['uid']for m in registry),inputHashes={'3d-viewer/'+p:h for p,h in tile_hashes.items()}))
 save(DOC/'proposal-input.json',dict(uids=[UID],sourceSHA256=SOURCE_SHA,currentManifest=ref(manifest),completeCurrentCatalogueRefs=catalogue_refs,coarseCells=cells,proposedRegion=bounds,completeFourWorldUnusedPOSITIONBounds=all_position_bounds,completeProtectedCurrentForms=17,historicalGroundNotUsed=True,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,publication=False))
 (DOC/'captured-manifest.json').write_bytes(before)
 assert reservations.owns(lease)and manifest.read_bytes()==before
 for pin in catalogue_refs:assert ref(ROOT/pin['path'])==pin
 for p,h in tile_hashes.items():assert digest((ROOT/'3d-viewer'/p).read_bytes())==h
 refs=[Path(__file__),HERE/'evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',IDENTITY/'result.json',IDENTITY/'identity.json',IDENTITY/'selection.json.gz',IDENTITY/'context.json.gz',POSITION/'result.json',POSITION/'complete-current-actual-source-and-ground.json.gz',ROOT/row['candidate']['path'],manifest,ROOT/'3d-viewer/city/data/terrain.json',*[ROOT/p['path']for p in catalogue_refs],*[ROOT/'3d-viewer'/p for p in tile_hashes],*[p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json'],*[p for p in DOC.rglob('*')if p.is_file()]]
 module('evangel_candidate_input_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-17-current-actor-authentic-tin-candidate-input-no-terrain-or-physical-credit',refs,dict(uids=[UID],completeProtectedCurrentForms=17,currentAcceptance=False,newlyInstalled=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();row=read(IDENTITY/'selection.json.gz')['rows'][0];_,bounds,_=nominated_region(row)
 forms=module('evangel_candidate_lease_forms','xl-final-script-pass.py').load_forms(bounds);assert {b['uid']for b,_,_ in forms}==EXPECTED_FORMS
 claim=reservations.claim('evangel-authentic-candidate-input-'+str(uuid.uuid4()),[('building:'if b['uid'].startswith('landsd/')else'foreign-form:')+b['uid']for b,_,_ in forms]+['terrain-patch:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
