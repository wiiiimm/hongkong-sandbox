"""Exact fresh Vancor authentic-TIN candidate input with retained Pak Shing actor.
No candidate geometry construction, physical acceptance or publication.
"""
import copy,importlib.util,json
from pathlib import Path
import numpy as np
from shapely.geometry import box
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
BATCH='government-xl-vancor-authentic-tin-retained-pak-shing-current-inputs-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
IDENTITY=DOC.parent/'government-xl-lee-kong-independent-147956-0-current-identity-v1-20261011'
UID='landsd/147956:0';RETAINED='landsd/186864:0'
PARENT='city/data/government-native-186864-0.json'
MANIFEST='b61c0bc2d706793c7d436ef3334ccb41e93675d3d50c29818a2dca3b56f8830e'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==MANIFEST
 receipt=read(IDENTITY/'result.json');assert receipt['rawIdentityPassed']and not receipt['rawIdentityReasons']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selection=copy.deepcopy(read(IDENTITY/'selection.json.gz'));assert selection['manifestSHA256']==MANIFEST and len(selection['rows'])==1
 row=selection['rows'][0];assert row['uid']==UID;row.setdefault('currentReview',None);assert row['currentReview']is None
 source=ROOT/row['candidate']['path'];raw=source.read_bytes();assert digest(raw)==row['sourceSHA256'];own_position=packed_world_bounds(raw);assert own_position['originalWholeSourceBounds']==row['native']['model']['worldBounds'];row['completeOriginalPOSITIONProof']=own_position
 contexts=read(IDENTITY/'context.json.gz');assert len(contexts['rows'])==1 and contexts['rows'][0]['uid']==UID
 current=read(manifest);cats=[ref(ROOT/'3d-viewer'/u)for u in current['officialModelCatalogues']];entries=[(p,m)for p in cats for m in read(ROOT/p['path'])['models']];assert len(entries)==len({m['uid']for _,m in entries})
 assert UID not in {m['uid']for _,m in entries};found=[(p,m)for p,m in entries if m['uid']==RETAINED];assert len(found)==1
 cat,entry=found[0];retained_asset=(ROOT/cat['path']).parent/entry['asset'];retained_raw=retained_asset.read_bytes();assert digest(retained_raw)==entry['sha256'];retained_position=packed_world_bounds(retained_raw);assert retained_position['originalWholeSourceBounds']==entry['worldBounds']
 parentpath=ROOT/'3d-viewer'/PARENT;parent=read(parentpath);assert parent.get('nativeMesh')and not parent.get('patches')and parent['meta']['targetUids']==[RETAINED]
 assert len([p for p in current['terrainPatches']if p['url']==PARENT])==1
 second=module('vancor_retained_source_cells','xl-second-pass.py');base=read(ROOT/'3d-viewer/city/data/terrain.json');cells=second.resolution.rectangle_for(own_position['originalWholeSourceBounds'],base);old=parent['coarseCells'];cells=[min(cells[0],old[0]),min(cells[1],old[1]),max(cells[2],old[2]),max(cells[3],old[3])];bounds=second.resolution.extent(cells,base)
 final=module('vancor_retained_complete_forms','xl-final-script-pass.py');forms=final.load_forms(bounds);uids={b['uid']for b,_,_ in forms};assert {UID,RETAINED}<=uids and len(uids)==len(forms)
 own_bounds=own_position['originalWholeSourceBounds'];r_bounds=retained_position['originalWholeSourceBounds'];assert box(own_bounds[0][0],own_bounds[0][2],own_bounds[1][0],own_bounds[1][2]).disjoint(box(r_bounds[0][0],r_bounds[0][2],r_bounds[1][0],r_bounds[1][2]))
 tiles={'3d-viewer/'+tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in forms}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(UID,)).fetchone();assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchone()==(row['native']['resultSha'],)
 selection.update(batch=BATCH,nativeRun=NATIVE_RUN);save(DOC/'check-selection.json.gz',selection);save(DOC/'context.json.gz',contexts);save(DOC/'complete-proposed-region-current-forms.json.gz',dict(rows=[dict(building=b,tile=tile,existingNative=b['uid']in {m['uid']for _,m in entries})for b,_,tile in forms],inputHashes=tiles))
 save(DOC/'proposal-input.json',dict(uid=UID,currentManifest=start,wholeOwnedPOSITIONProof=own_position,proposedCoarseCells=cells,proposedRegionBounds=bounds,retainedNativeUID=RETAINED,retainedParent=ref(parentpath),retainedCatalogue=cat,retainedEntry=entry,retainedAsset=ref(retained_asset),retainedWholeOriginalPOSITIONProof=retained_position,completeCurrentCatalogueRefs=cats,completeCurrentTileHashes=tiles,retainedAndNewWholeOriginalPOSBoundsDisjoint=True,actualRenderF32RetainedCoverageStillRequired=True,currentAcceptance=False,terrainProposalCreated=False,installationApproved=False))
 assert ref(manifest)==start and all(ref(ROOT/p['path'])==p for p in cats)
 for path,sha in tiles.items():assert digest((ROOT/path).read_bytes())==sha
 refs=[Path(__file__),IDENTITY/'result.json',IDENTITY/'selection.json.gz',IDENTITY/'context.json.gz',IDENTITY/'identity.json',source,parentpath,retained_asset,HERE/'exact_packed_world_bounds_v3_20261010.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py',*[ROOT/p['path']for p in cats],*[ROOT/p for p in tiles]]
 freeze=module('vancor_retained_input_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py');freeze.freeze(BATCH,'fresh-vancor-retained-pak-shing-authentic-tin-candidate-input-no-acceptance-v1',refs,dict(uids=[UID,RETAINED],ownedUID=UID,currentManifest=start,proposedRegionBounds=bounds,completeCurrentForms=len(forms),sourceGeometryChanges=0,currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
