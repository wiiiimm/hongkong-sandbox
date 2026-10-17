"""Register completed unchanged diagnostic after producer omitted receipt uids."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';DOC=B/'government-xl-hkust-unresolved-rim-source-context-v1-20261015';OLD=B/'government-xl-hkust-private-compound-foundation-v1-20261015';PACKET=B/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014'
def main():
 assert not (DOC/'result.json').exists()
 p=OLD/'compound.json.gz';pins={r['path']:r['sha256'] for r in read(OLD/'result.json')['evidenceRefs']};assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 rp=PACKET/'two-original-scope-interface-output-v1/result.json';report=read(rp);paths=[Path(__file__),HERE/'hkust_unresolved_rim_source_context_v1_20261015.py',p,OLD/'result.json',rp]
 for r in report['arrayRefs']:
  ap=ROOT/r['path'];assert digest(ap.read_bytes())==r['sha256'];paths.append(ap)
 detail=read(DOC/'source-incidence.json.gz');out=read(DOC/'summary.json');expected=[s for s in read(p)['towerSamples'] if s['combinedGapM']>1]
 assert [r['sample'] for r in detail['rows']]==expected
 assert len(expected)==out['samplesOverExistingOneMetreThreshold']==52
 save(DOC/'producer-failure.json',{'error':'KeyError: uids','phase':'receipt payload before jobs.enqueue','computationCompleted':True,'leaseReleasedByFinally':True,'recovery':'Register saved outputs with explicit original UIDs; no geometry rerun.'})
 module('hkust_rim_recovery_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'hkust-unresolved-rim-original-face-context-v1',paths,{**out,'uids':['landsd/309822:0','landsd/232155:0'],'nextStep':'Check source frontage and support roles for 44 exact incident faces covering all 52 >1m gaps; no contact waiver or identity approval.'})
if __name__=='__main__':main()
