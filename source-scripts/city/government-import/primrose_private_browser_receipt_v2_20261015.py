"""Recover completed preview receipt after caller variable shadowing; no rerender."""
from pathlib import Path
import shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import BASE,SOURCE,module
BATCH='government-xl-primrose-private-browser-receipt-v2-20261015';DOC=BASE/BATCH;OLD=BASE/'government-xl-primrose-private-podium-browser-v1-20261015';STAGE=HERE/'local'/OLD.name

def main():
 assert not DOC.exists();report=read(OLD/'staged-browser.json');command=read(OLD/'command.json')
 assert command['exitCode']==0 and report['passed']and not report['errors'];assert len(report['views'])==5
 refs={}
 for folder in [SOURCE,BASE/'government-xl-primrose-private-terrain-floor-v5-20261015',BASE/'government-xl-primrose-podium-role-review-v2-20261015']:
  r=read(folder/'result.json')
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for q in r['evidenceRefs']:
   assert q['path']not in refs or refs[q['path']]==q['sha256'];refs[q['path']]=q['sha256']
  refs[str((folder/'result.json').relative_to(ROOT))]=digest((folder/'result.json').read_bytes())
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
 catalogue=read(STAGE/'catalogue.json');assert len(catalogue['models'])==4
 for e in catalogue['models']:assert digest((STAGE/e['asset']).read_bytes())==e['sha256']and e['publicationApproved']is False and not e['suppressesBuildingUids']
 DOC.mkdir();shutil.copyfile('/tmp/primrose-private-podium-browser-v1-20261015.log',DOC/'failed-wrapper.log')
 assert "AttributeError: 'str' object has no attribute 'returncode'"in (DOC/'failed-wrapper.log').read_text()
 save(DOC/'recovery.json',dict(originalBrowserExitCode=0,browserPassed=True,originalWrapperFailed=True,reason='Loop variable p shadowed completed subprocess object after successful browser and input verification. No renderer or model failure.',renderReplayed=False,fullAcceptance=False))
 images=[OLD/('staged-landsd-74573-0-'+n+'.png')for n in ['1280-1500','1280-2200','390-1500','390-2200']]
 save(DOC/'ROOT-IMAGE-INSPECTION.json',dict(reviewer='Codex ROOT',imagesActuallyViewed=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in images],observation='Original assembly visibly renders with podium and lower tower portions. Tower tops deliberately outside podium close-up framing. Shelter detail is not sufficiently isolated to approve duplicate suppression. Mobile UI occupies lower viewport; no whole-tower visual acceptance claimed.',fullAcceptance=False,duplicateSuppressionApproved=False,reviewUsedAI=True,aiGeometryModelling=False))
 paths=[ROOT/p for p in refs]+[Path(__file__),HERE/'primrose_private_podium_browser_v1_20261015.py',HERE/'esplanade_joint_browser_v2_20261015.mjs',HERE/'primrose_compound_foundation_v2_20261015.py']+[p for folder in [OLD,STAGE]for p in folder.rglob('*')if p.is_file()]
 module('receipt_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'recovered-complete-private-four-original-browser-receipt-v2',paths,dict(uids=[e['uid']for e in catalogue['models']],browserPassed=True,renderReplayed=False,fullAcceptance=False))
if __name__=='__main__':main()
