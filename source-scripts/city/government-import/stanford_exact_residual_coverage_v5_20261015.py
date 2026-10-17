"""Exact full-region replay of every floating coverage warning; no tolerance credit."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_projected_uncovered_regions_20261010 import diagnose
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-exact-residual-coverage-v5-20261015';DOC=BASE/BATCH
PREV=BASE/'government-xl-stanford-join-source-ground-v5-20261015';CAP=BASE/'government-xl-stanford-join-runtime-capture-v5-20261015'
def main():
 assert not DOC.exists();DOC.mkdir();r=read(PREV/'result.json');refs=[Path(__file__),PREV/'result.json',HERE/'exact_original_projected_uncovered_regions_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py']
 for q in r['evidenceRefs']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p)
 summary=read(PREV/'summary.json');source=next(s for s in read(BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015/recovery.json')['rows']if s['modelId']=='B365201779201063C0');asset=ROOT/source['asset']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());ground=np.asarray(read(CAP/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);rows=[]
 for i in summary['uncoveredFaces']:
  proof=diagnose(tri[i],ground);rows.append({'sourceFace':i,'proof':proof});print(i,proof['exactProjectionCovered'],len(proof['allExactUncoveredRegions']),flush=True)
 save(DOC/'proofs.json.gz',{'rows':rows});result={'checkedFloatingWarnings':len(rows),'exactCoveredWarnings':sum(r['proof']['exactProjectionCovered']for r in rows),'exactUncoveredFaces':[r['sourceFace']for r in rows if not r['proof']['exactProjectionCovered']],'sourceGeometryChanges':0,'fullAcceptance':False,'qualification':'Every floating warning checked with complete closed exact projected facets; other source/runtime/support checks remain independently required.'};save(DOC/'summary.json',result)
 module('freeze_stanford_exact_residual',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'all-floating-source-warnings-exact-coverage-v5',refs,{'uids':['landsd/305584:0','landsd/335875:0'],**result});print(result,flush=True)
if __name__=='__main__':main()
