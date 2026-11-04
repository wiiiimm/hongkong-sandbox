"""Compare five exact retained originals with the immutable Palazzo owner."""
import argparse,copy,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-palazzo76610-after-prosperous-';BATCH=P+'retained-five-original-pairs-sequence-v1-20261101';REC='government-xl-palazzo76610-retained-five-original-recovery-v1-20261101';ATTR=P+'retained-five-original-attributes-v1-20261101';SIX=P+'retained-five-owner-source-context-v1-20261101';PAIRS=P+'retained-five-owner-original-pairs-v1-20261101'
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args();lp=HERE/'local'/BATCH/'reservation.json'
    uids=['landsd/'+k+':0'for k in ['76610','68540','88780','252555','252556','252558']]
    if not a.owned:
        assert not lp.parent.exists();c=reservations.claim('palazzo-original-pairs-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease);out=BASE/BATCH;assert not out.exists();out.mkdir();refs=[Path(__file__)];pins={}
    def take(batch,name):
        if batch not in pins:_,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    def run(script,args,log):
        tool=HERE/script;sha=digest(tool.read_bytes());refs.append(tool)
        with(out/log).open('w')as f:subprocess.run([sys.executable,str(tool),*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
        assert digest(tool.read_bytes())==sha and reservations.owns(lease)
    recovered=take(REC,'selection.json.gz');assert len(recovered['rows'])==5 and not recovered['missing']
    run('selected_original_render_attributes_v1.py',['--batch',ATTR,'--capture',REC],'attributes.log')
    fresh=take(ATTR,'attributes.json.gz');prior=take(P+'fifteen-original-attributes-v1-20261101','attributes.json.gz');selection=take(P+'fifteen-authentic-tin-runtime-v1-20261101','selection.json.gz')
    assert fresh['startEndAllInputsVerified']and prior['startEndAllInputsVerified']and fresh['completeRecursiveProductionModuleClosure']==prior['completeRecursiveProductionModuleClosure']
    rows=[next(r for r in selection['rows']if r['uid']=='landsd/76610:0'),*recovered['rows']];assert set(uids)=={r['uid']for r in rows}
    arrays=copy.deepcopy(fresh);arrays['rows']=[next(r for r in prior['rows']if r['uid']=='landsd/76610:0'),*fresh['rows']]
    for path,sha in prior['inputHashes'].items():
        assert path not in arrays['inputHashes']or arrays['inputHashes'][path]==sha
        arrays['inputHashes'][path]=sha
    for path,sha in arrays['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==recovered['manifestSHA256'];refs.append(manifest)
    for r in rows:
        asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
        tile=ROOT/'3d-viewer'/r['source']['tile'];assert digest(tile.read_bytes())==r['source']['tileSHA256']and next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building'];refs.append(tile)
    save(BASE/SIX/'selection.json.gz',dict(rows=rows,manifestSHA256=selection['manifestSHA256'],sourceGeometryChanges=0,publication=False));save(BASE/SIX/'attributes.json.gz',arrays)
    module('palazzo_six_exact_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(SIX,'six-exact-original-current-source-and-render-context',list(dict.fromkeys(refs)),dict(uids=uids,sourceSHA256ByUid={r['uid']:r['sourceSHA256']for r in rows},sourceGeometryChanges=0,installationApproved=False,publication=False,qualification='Reuses unchanged complete owner arrays; five freshly captured originals. Current source files, production module closure, arrays and map forms pinned. No terrain/runtime/physical approval.'))
    run('original_assembly_four_world_pair_context_v3_20261101.py',['--batch',PAIRS,'--runtime',SIX,'--attributes',SIX,'--lease',str(lp)],'pairs.log')
    take(PAIRS,'summary.json');assert reservations.owns(lease)
    module('palazzo_five_pair_sequence_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'retained-five-original-four-world-pair-sequence',list(dict.fromkeys(refs)),dict(uids=uids,completedPairBatch=PAIRS,sourceGeometryChanges=0,installationApproved=False,publication=False))
if __name__=='__main__':main()
