"""ROOT image observations of immutable original extents; not acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-next-three-original-extent-v1-20261019';BATCH='government-xl-next-three-source-observations-v1-20261019';DOC=BASE/BATCH
OBS={
 '64856:0':'Complete source includes two substantial side sections at opposite ends of the long target strip, plus a narrow extension. Source projection is larger than the target footprint. Archived context associates adjoining mall footprints with the same parent, but this alone is not placement or collision acceptance.',
 '232240:0':'Original front and side projections extend outside the recorded target. The projection does not cover all of the target footprint. Existing context includes another Central Library government component227428; full original component coverage and existing placement require checking.',
 '233227:0':'A central source wing and short end projection extend outside the U-shaped target outline. Context includes already installed Harbourfront component31275. Compare complete original components and current neighbour/terrain evidence before deciding installation.'}
def main():
 assert not DOC.exists();receipt=read(SRC/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};refs=[Path(__file__),SRC/'result.json'];rows=[]
 for key,observation in OBS.items():
  files=[SRC/(key+'.png'),SRC/(key+'.json')]
  for p in files:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
  rows.append(dict(uid='landsd/'+key,reviewer='Codex ROOT',imageActuallyViewed=dict(path=str(files[0].relative_to(ROOT)),sha256=digest(files[0].read_bytes())),observation=observation,rawIdentityReasonsPreserved=read(files[1])['rawReasons'],identityApproved=False,placementApproved=False,installationApproved=False))
 save(DOC/'ROOT-OBSERVATIONS.json',dict(rows=rows,aiUsedForEvidenceInterpretation=True,aiGeometryModelling=False,originalGeometryChanges=0))
 result=module('source_observations_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-original-source-observations',refs,dict(uids=[r['uid']for r in rows],rows=rows,installationApproved=False))
 print(result['jobId'])
if __name__=='__main__':main()
