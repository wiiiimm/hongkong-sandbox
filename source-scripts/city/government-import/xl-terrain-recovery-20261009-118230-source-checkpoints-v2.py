"""Durable exact source inventory and preserved failed narrower graph evidence."""
import importlib.util
from pathlib import Path
from run import ROOT,HERE,read
BASE=ROOT/'docs/astra-city/government-import'
def main():
 s=importlib.util.spec_from_file_location('harbourfront_immutable_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 b='xl-terrain-recovery-20261009-118230-provider-source-inventory-v2';d=BASE/b;r=read(d/'original-source-provenance.json');role=read(d/'expected-role.json')
 m.freeze(b,'complete-original-provider-exterior-stream-inventory-v2',[Path(__file__),HERE/'xl-terrain-recovery-20261009-118230-provider-source-inventory-v2.py',*[ROOT/x['path'] for x in r['evidenceRefs']]],dict(uids=['landsd/118230:0'],sourceSHA256=role['sourceSHA256'],allOriginalAttributesPreserved=True,completeOriginalFaces=19438,rawWallOnlyContractAccepted=False,scriptFullAcceptancePassed=False,nextStep='Complete current all-face terrain and original structural support; separate strictly clear cap bridges and complete low ancillary exterior interpretation. Provenance alone grants no physical credit.'))
 b='xl-terrain-recovery-20261009-118230-exact-wall-graph';d=BASE/b;r=read(d/'diagnostic.json.gz');unresolved=[p['sourceFace'] for p in r['paths'] if not p['hasExactPositiveDimensionPathToClearRoof']]
 m.freeze(b,'preserved-narrow-original-wall-only-contact-graph-v1',[Path(__file__),*[ROOT/x['path'] for x in r['evidenceRefs']]],dict(uids=['landsd/118230:0'],sourceSHA256=r['sourceSHA256'],rawNarrowGraphAccepted=False,unresolvedOriginalFaces=unresolved,scriptFullAcceptancePassed=False,newerClearOriginalCapMethod= 'docs/astra-city/government-import/government-xl-two-harbourfront-complete-original-roof-paths-20261009/result.json',nextStep='Retain failed wall-only graph. Reviewed newer original strictly clear cap bridge graph must be recomputed against complete current contexts; no precision-repair or Float32 cause is asserted.'))
if __name__=='__main__':main()
