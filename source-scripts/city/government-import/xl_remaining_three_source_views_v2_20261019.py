"""Render three unfinished immutable XL sources for component/terrain investigation."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-remaining-three-source-views-v2-20261019';DOC=BASE/BATCH
CAP=BASE/'government-xl-next-five-current-terrain-v1-20261018'
NAMES={'landsd/263423:0':'Kai Tak Cruise Terminal','landsd/210032:0':'Star Ferry Pier','landsd/281463:0':'Lai Chi Kok Park Sports Centre'}
def main():
 assert not DOC.exists();receipt=read(CAP/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 selection=CAP/'selection.json.gz';assert any(e['path']==str(selection.relative_to(ROOT))and e['sha256']==digest(selection.read_bytes())for e in receipt['evidenceRefs'])
 rows=[r for r in read(selection)['rows']if r['uid']in NAMES];assert {r['uid']for r in rows}==set(NAMES)
 refs=[Path(__file__),selection,CAP/'result.json'];models=[];loader=module('three_source_forms',HERE/'xl-final-script-pass.py');refs.append(HERE/'xl-final-script-pass.py')
 for row in rows:
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
  lo,hi=row['candidate']['entry']['worldBounds'];forms=loader.load_forms([lo[0]-20,lo[2]-20,hi[0]+20,hi[2]+20]);refs.extend(ROOT/'3d-viewer'/tile for _,_,tile in forms)
  source=dict(assetPath=row['candidate']['path'],sourceSHA256=row['sourceSHA256'],worldBounds=[lo,hi],triangles=row['triangles'])
  for suffix,direction in [('whole',[.7,.8,1]),('reverse',[-.7,.8,-1])]:models.append(dict(**source,uid='review/'+row['uid'].split('/')[1].replace(':','-')+'-'+suffix,label=NAMES[row['uid']],forms=[b for b,_,_ in forms],viewDirection=direction))
 tool=HERE/'xl_remaining_three_source_views_v2_20261019.mjs';refs.append(tool);refs=list(dict.fromkeys(refs));hashes={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs}
 save(DOC/'input.json',dict(models=models,inputHashes=hashes,historicalSourceOnly=True))
 subprocess.run(['node',str(tool),'--inputs',str((DOC/'input.json').relative_to(ROOT)),'--out',str(DOC.relative_to(ROOT))],cwd=ROOT,check=True)
 report=read(DOC/'render.json');assert len(report['views'])==6 and not report['errors']
 assert len({v['image']['path']for v in report['views']})==6
 for v in report['views']:assert digest((ROOT/v['image']['path']).read_bytes())==v['image']['sha256']
 for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 module('three_source_view_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-unfinished-xl-original-source-views',list(dict.fromkeys(refs)),dict(uids=list(NAMES),views=6,installationApproved=False,sourceGeometryChanges=0))
if __name__=='__main__':main()
