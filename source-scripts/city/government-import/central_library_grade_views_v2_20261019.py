"""Side views of exact flagged original source faces; no source edits."""
from pathlib import Path
import subprocess,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-library-grade-views-v2-20261019';DOC=BASE/BATCH;SRC=BASE/'government-xl-central-library-original-grade-comparison-v1-20261019'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 old=read(SRC/'input.json');view=old['models'][1];details=read(SRC/'original.json.gz')['details'];tri=[d['triangle']for d in details];models=[]
 for name,direction in [('grade-side',[1,.15,-.7]),('grade-reverse',[-1,.15,.7])]:models.append(dict(view,uid='review/'+name,viewDirection=direction,failedSamples=[],flaggedTriangles=tri))
 save(DOC/'input.json',dict(models=models,inputHashes=old['inputHashes']));tool=HERE/'central_library_grade_views_v2_20261019.mjs';subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True);report=read(DOC/'render.json');assert len(report['views'])==2 and not report['errors'];refs=[Path(__file__),tool,SRC/'result.json']
 for p,h in {**pins,**report['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('library_grade_views_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'central-library-exact-flagged-vertical-faces-views',list(dict.fromkeys(refs)),dict(uids=['landsd/232240:0'],views=2,installationApproved=False))
if __name__=='__main__':main()
