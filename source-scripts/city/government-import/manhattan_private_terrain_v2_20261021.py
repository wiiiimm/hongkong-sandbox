"""Use singular replacement metadata for one retained parent; geometry unchanged."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-private-terrain-v2-20261021';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-manhattan-private-terrain-v1-20261021'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 refs=[Path(__file__),PRIOR/'result.json']
 for e in receipt['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 descriptors=read(PRIOR/'terrain-candidates.json');assert len(descriptors)==1
 d=descriptors[0];assert len(d['replacesMany'])==1;d['replaces']=d.pop('replacesMany')[0]
 assert digest((ROOT/d['path']).read_bytes())==d['sha256'];save(DOC/'terrain-candidates.json',descriptors)
 summary=read(PRIOR/'summary.json');assert summary['terrainValidationPassed'];summary['replacementSchema']='single-parent';save(DOC/'summary.json',summary)
 module('manhattan_descriptor_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-validated-terrain-single-parent-descriptor',refs,summary)
if __name__=='__main__':main()
