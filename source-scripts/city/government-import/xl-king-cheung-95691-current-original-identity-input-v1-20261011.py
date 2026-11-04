"""Schema-only current source18742 input; exact bytes/entry/current form unchanged.
Adds the existing generic preflight's explicit triangle-count field from the
independently decoded complete original, never geometry or identity credit.
"""
import importlib.util,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-king-cheung-95691-untouched-original-recovery-v1-20261011'
BATCH='government-xl-king-cheung-95691-current-original-identity-input-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();receipt=read(OLD/'result.json')
 with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 p=OLD/'selection.json.gz';assert ref(p)in receipt['evidenceRefs'];selection=read(p);assert not selection['missing']and len(selection['rows'])==1;r=selection['rows'][0];assert r['uid']=='landsd/95691:0'and 'triangles'not in r
 asset=ROOT/r['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==r['sourceSHA256']==r['candidate']['entry']['sha256'];assert len(decode_original_world_triangles(raw))==r['candidate']['entry']['triangles']==18742
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building']
 new=json.loads(json.dumps(selection));new['batch']=BATCH;new['rows'][0]['triangles']=18742;compare=json.loads(json.dumps(new));compare.pop('batch');
 if 'batch'in selection:compare['batch']=selection['batch']
 del compare['rows'][0]['triangles'];assert compare==selection
 save(DOC/'selection.json.gz',new);save(DOC/'schema-adapter.json',dict(uid=r['uid'],soleAddedRowField='triangles',newBatchBookkeepingOnly=BATCH,value=18742,completeOriginalDecodedFaces=18742,sourceGeometryChanges=0,currentAcceptance=False,installationApproved=False))
 spec=importlib.util.spec_from_file_location('king-cheung_exact18742_schema_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'exact-source18742-preflight-selection-schema-only-no-identity-credit',[Path(__file__),OLD/'result.json',p,asset,tile,manifest,HERE/'exact_packed_world_geometry_20261009.py'],dict(uids=[r['uid']],currentAcceptance=False,newlyInstalled=0))
if __name__=='__main__':main()
