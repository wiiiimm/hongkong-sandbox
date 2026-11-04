"""Preserve ROOT's observed source roles without granting placement acceptance."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-remaining-three-source-views-v2-20261019';BATCH='government-xl-remaining-three-source-review-v1-20261019';DOC=BASE/BATCH
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256'];refs.append(ROOT/q['path'])
 views=read(SRC/'render.json')['views'];assert len(views)==6 and len({v['image']['path']for v in views})==6
 for v in views:assert digest((ROOT/v['image']['path']).read_bytes())==v['image']['sha256']
 observations=[dict(uid='landsd/263423:0',sourceRole='Long cruise-terminal building/platform with rooftop openings and long narrow end extension.',nextAction='Build original-terrain candidate while retaining the existing installed landsd/299814:0 source and terrain; examine full-source component overlaps and low contact faces.'),dict(uid='landsd/210032:0',sourceRole='Two ferry-pier arms with landward connecting roof, canopies and long access extension beyond the principal footprint.',nextAction='Attribute complete covered access structures to the original source; construct local terrain without disturbing Hullett House or the newly installed Ocean Terminal child.'),dict(uid='landsd/281463:0',sourceRole='Large landscaped/stepped platform or podium surface; footprint name alone does not establish that it represents the entire sports-centre building.',nextAction='Attribute the 2,591 fully buried source faces, including 1,598 upward faces, against complete original government terrain; investigate source role and layer overlap before considering installation.')]
 save(DOC/'ROOT-SOURCE-VIEW-REVIEW.json',dict(reviewer='Codex ROOT',imagesActuallyViewed=[v['image']for v in views],observations=observations,identityApproval=False,placementApproval=False,publicationApproval=False,sourceGeometryChanges=0,aiGeometryModelling=False,diagnosticV1Limitation='V1 whole/reverse captures shared filenames and overwrote earlier views. V2 uses six unique paths and validates each saved image hash. No V1 images used for this review.'))
 module('three_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unfinished-xl-source-role-investigation',list(dict.fromkeys(refs)),dict(uids=[o['uid']for o in observations],reviewedImages=6,installationApproved=False))
if __name__=='__main__':main()
