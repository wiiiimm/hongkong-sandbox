"""Exact-source assembly identity review; retain individual and strict-interface diagnostics."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_source_assembly_diagnostic import evaluate
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-assembly-identity-review-v1-20261020';DOC=BASE/BATCH;ID=BASE/'government-xl-folkland-pair-current-identity-v1-20261020';OLD=BASE/'government-xl-coverage-assembly-identity-20261007-264677-0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];receipts={}
 names=[ID,OLD]+[BASE/('government-xl-folkland-'+n+'-20261020')for n in ['original-finite-path-verification-v1','runtime-finite-path-verification-v1','pair-browser-desktop-v2','pair-browser-mobile-v2']]
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY')
  for f in names:
   r=read(f/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(f/'result.json');receipts[f]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def consume(f,p):
  assert digest(p.read_bytes())==receipts[f][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 selection=consume(ID,ID/'selection.json.gz')['rows'];individual={};triangles={};forms=[];final=module('folkland_identity_forms',HERE/'xl-final-script-pass.py')
 for r in selection:
  p=ROOT/r['candidate']['path'];assert digest(p.read_bytes())==r['sourceSHA256'];refs.append(p);triangles[r['uid']]=decode_original_world_triangles(p.read_bytes());individual[r['uid']]=consume(ID,ID/r['uid'].split('/')[1]/'identity.json')
 alltri=np.concatenate(list(triangles.values()));lo,hi=alltri.min((0,1)),alltri.max((0,1))
 for b,_,tile in final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]):
  p=ROOT/'3d-viewer'/tile;assert digest(p.read_bytes())==receipts[ID][str(p.relative_to(ROOT))];refs.append(p);forms.append(b)
 old=consume(OLD,OLD/'assembly-identity.json');proof=evaluate(selection,individual,triangles,old['strictOriginalInterface'],forms,tower='landsd/264677:0',podium='landsd/225387:0');assert proof['reasons']==['exact-original-support-interface'];save(DOC/'raw-current-assembly-diagnostic.json',proof)
 for f in names[2:4]:
  summary=consume(f,f/'summary.json')
  for row in summary['rows']:assert row['targets']==row['finitePaths']==row['boundedHeightPaths']==row['wallOnlyPaths']==31
 images=[]
 for f in names[4:]:
  report=consume(f,f/'staged-browser.json');assert report['passed']and not report['errors']
  for v in report['views']:
   if 'file'in v:p=f/v['file'];assert digest(p.read_bytes())==receipts[f][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 assert len(images)==8
 review=dict(reviewer='Codex ROOT',uids=proof['uids'],sourceSHA256ByUid=proof['sourceSHA256s'],identityOnlyApproved=True,rawDiagnosticPassed=False,rawReasons=proof['reasons'],rawIndividualIdentityReasons={u:p['reasons']for u,p in individual.items()},measures=proof['measures'],imagesActuallyViewed=images,sourceGeometryChanges=0,installationApproved=False,basis='Both unchanged government roots retain unique object IDs, CSUIDs, native transforms and complete geographic cells. The tower alone covers93.53percent of its coarse footprint; the exact same-building tower/podium pair covers the complete compound footprint with zero unrelated overlap and maximum2.84m extent difference. Fresh non-spatial identity checks pass. ROOT inspected all8 exports: the original tower visibly joins the matching podium, retaining its roof recesses and facade ribs. Independent finite steep-wall intersection evidence binds the two original parts in four representations. This supports identity of this exact two-part original assembly; it does not mark the strict interface diagnostic passed. Physical acceptance, complete foundations, neighbours and publication remain separate. No general coverage threshold or support policy is changed.')
 save(DOC/'review.json',review);refs.extend([HERE/'original_source_assembly_diagnostic.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-final-script-pass.py']);module('folkland_assembly_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-exact-assembly-identity-review',list(dict.fromkeys(refs)),review);print('Exact Folkland assembly identity reviewed; raw diagnostics preserved',flush=True)
if __name__=='__main__':main()
