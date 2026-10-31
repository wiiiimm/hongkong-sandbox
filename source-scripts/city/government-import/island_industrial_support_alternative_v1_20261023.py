"""Select the sole unacquired original beside the exact known tower source.
Source acquisition nomination only; all broad spatial matches remain explicit.
"""
from pathlib import Path
import copy
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
 batch='government-xl-island-industrial-podium-alternative-v1-20261023';out=BASE/batch;assert not out.exists();prior='government-xl-island-industrial-podium-lookup-v2-20261023';_,pins=authenticate(BASE/prior);p=BASE/prior/'lookup.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];r=read(p);refs=[Path(__file__),BASE/prior/'result.json',p]
 source='government-xl-all-200-original-terrain-batch-v2-20261022';_,sp=authenticate(BASE/source);p=BASE/source/'selection.json.gz';assert digest(p.read_bytes())==sp[str(p.relative_to(ROOT))];owner=next(x for x in read(p)['rows']if x['uid']=='landsd/20270:0');refs.extend([BASE/source/'result.json',p])
 row=r['rows'][0];models=row['matchedOriginalModels'];assert len(models)==2 and len([m for m in models if m['modelId']==owner['modelId']and m['asset']['sha256']==owner['sourceSHA256']])==1
 alternative=[m for m in models if m['modelId']!=owner['modelId']];assert len(alternative)==1 and alternative[0]['modelId'][:11]==owner['modelId'][:11] and alternative[0]['asset']['sha256']!=owner['sourceSHA256']
 result=copy.deepcopy(r);result['rows'][0].update(allRawSpatiallyMatchedModels=models,excludedKnownOwnerModelId=owner['modelId'],matchedOriginalModels=alternative,matchCount=1)
 result['qualification']='Nominate only the sole separate government original at the same GeoRef after excluding the exact already-bound11166face tower ModelId/SHA. Both raw broad spatial matches remain preserved. This is not targetCSUID disambiguation, support identity or installation approval; the537face source still requires complete geometry/identity/placement checks.'
 save(out/'lookup.json',result);module('island_alternative_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'explicit-distinct-original-source-acquisition-nomination',refs,result);print(dict(modelId=alternative[0]['modelId'],triangles=alternative[0]['triangles'],installationApproved=False),flush=True)
if __name__=='__main__':main()
