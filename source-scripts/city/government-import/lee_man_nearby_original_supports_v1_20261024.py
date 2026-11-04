"""Find prepared original lower structures overlapping Lee & Man's native footing."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import';batch='government-xl-next-repairs-lee-man-nearby-original-supports-v1-20261024';out=base/batch;assert not out.exists();prior='government-xl-next-repairs-sung-fung-lee-man-original-family-discovery-v1-20261024';_,pins=authenticate(base/prior);path=base/prior/'source-families.json.gz';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];tower=next(r for r in read(path)['rows']if r['uid']=='landsd/47160:0');lo,hi=np.asarray(tower['model']['worldBounds']);bottom=float(lo[1]);refs=[Path(__file__),base/prior/'result.json',path]
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');record=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(tower['cacheKey'],)).fetchone();assert record and record[0]==tower['resultSHA256']
    rows=[]
    for m in record[1]['models']:
        if m['modelId']==tower['model']['modelId']or not m.get('worldBounds'):continue
        low,high=np.asarray(m['worldBounds']);xz_overlap=np.minimum(high[[0,2]],hi[[0,2]])-np.maximum(low[[0,2]],lo[[0,2]])
        if np.any(xz_overlap<=0)or low[1]>=bottom-.5 or high[1]<bottom-.5 or high[1]>bottom+5:continue
        rows.append(dict(model=m,completeBoundsOverlapAreaM2=float(np.prod(xz_overlap)),sourceTopMinusTowerBottomM=float(high[1]-bottom),rawCandidateUid=(m.get('candidate')or{}).get('uid'),installationApproved=False))
    result=dict(uids=['landsd/47160:0'],cacheKey=tower['cacheKey'],nativeResultSHA256=tower['resultSHA256'],originalTowerBounds=tower['model']['worldBounds'],candidateLowerStructures=len(rows),rows=rows,installationApproved=False,publication=False,sourceGeometryChanges=0,qualification='Exact same prepared government sheet revision; 3D bound/height nomination only. No same-name, footprint, support, identity or component approval. Source bytes and full finite interfaces still required.')
    save(out/'summary.json',result);module('lee_man_lower_sources_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'prepared-original-nearby-lower-source-support-nomination',refs,result);print([dict(modelId=r['model']['modelId'],uid=r['rawCandidateUid'],faces=r['model']['triangles'],bounds=r['model']['worldBounds'])for r in rows],flush=True)


if __name__=='__main__':main()
