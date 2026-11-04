"""Fresh immutable source selection for the current apron review; no runtime approval."""
from pathlib import Path
import copy
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-disneyland-eastern75643-apron-selection-v1-20261030';UID='landsd/75643:0';SHA='4c8e577256875f9ecc67fe5728e262113d852748ac743798b804f9b090f0dbc2'
def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();old=base/'government-xl-disneyland-eastern75643-after-western-current-ground-v1-20261030';_,pins=authenticate(old);selectionpath=old/'selection.json.gz';assert digest(selectionpath.read_bytes())==pins[str(selectionpath.relative_to(ROOT))];refs=[Path(__file__),old/'result.json',selectionpath]
 row=copy.deepcopy(next(r for r in read(selectionpath)['rows']if r['uid']==UID));assert row['sourceSHA256']==SHA
 tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']and next(b for b in read(tile)['buildings']if b['uid']==UID)==row['source']['building'];refs.append(tile)
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset);native=row['native']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');record=db.execute('SELECT r.result_sha,r.result,i.sheet FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) WHERE r.cache_key=%s',(native['cacheKey'],)).fetchone();assert record and record[0]==native['resultSha']and next(m for m in record[1]['models']if m['modelId']==row['modelId'])==native['model'];sheet=record[2]
 assert not row['candidate']['entry'].get('supportDependencies')and not row['candidate']['entry'].get('suppressesBuildingUids');row['candidate']['entry'].update(sourceTile=sheet,proceduralWindows=False)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url;assert UID not in {m['uid']for m in read(p)['models']};refs.append(p)
 save(out/'selection.json.gz',dict(rows=[row],manifestSHA256=digest(manifest.read_bytes())))
 result=dict(uids=[UID],sourceSHA256=SHA,currentManifestSHA256=digest(manifest.read_bytes()),sourceGeometryChanges=0,sourcePoseChanges=0,oldRuntimeApprovalTransferred=False,installationApproved=False,publication=False,qualification='Only immutable exact source/native/form identity is rebound. Current sourceTile is read from pinned native input. No old renderer, bounds, source physical or publication approval is reused; new current capture follows.')
 save(out/'summary.json',result);module('eastern_apron_selection_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-exact-source-selection-no-old-runtime-transfer',refs,result)
if __name__=='__main__':main()
