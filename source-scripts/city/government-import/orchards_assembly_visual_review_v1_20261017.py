"""Freeze ROOT's actual exported-image review, without installation credit."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-orchards-assembly-visual-review-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();pins={};reports={};dirs={}
 for v in [4,5]:
  d=BASE/f'government-xl-orchards-assembly-private-browser-v{v}-20261017';dirs[v]=d;r=read(d/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
  pins[str((d/'result.json').relative_to(ROOT))]=digest((d/'result.json').read_bytes());reports[v]=read(d/'staged-browser.json');assert reports[v]['passed'] and not reports[v]['errors']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 reviewed=[];superseded=[]
 for row in reports[4]['views']+reports[4]['retainedNativeOwnViews']:
  if 'time' not in row:continue
  entry={**ref(dirs[4]/row['file']), 'uid':row['uid'],'width':row['width'],'time':row['time']}
  (superseded if row['uid']=='landsd/256434:0' and row['width']==390 else reviewed).append(entry)
 for row in reports[5]['views']:
  if 'time' in row:reviewed.append({**ref(dirs[5]/row['file']),'uid':row['uid'],'width':row['width'],'time':row['time']})
 assert len(reviewed)==18 and len(superseded)==2
 assert any(r.get('phase')=='failed-download' and r['fallbackRetained'] for r in reports[4]['views'])
 review=dict(reviewer='Codex ROOT',sourceGeometryAppearanceAccepted=True,reviewedImages=reviewed,supersededImages=superseded,notes=['Reviewed all16 v4 day/night desktop/mobile exports and four v5 community exports.','Two v4 community mobile views were obscured by foreground buildings; v5 overhead exports resolve visibility.','Podium overhead view complements original oblique source-role inspection. Existing Tower1 remains solid and unchanged.','Night originals remain untextured/dark with proceduralWindows disabled; no invented window skin.','Local statistics API unavailable in static test server; this is not a production statistics acceptance.'],sourceGeometryChanges=0,aiGeometryModelling=False,publicationApproved=False,nextStep='Qualified atomic original-model stage, exact community identity companion, native terrain replacement review, guarded installation and live verification.')
 save(DOC/'ROOT-IMAGE-INSPECTION.json',review)
 r=module('orchards_visual_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-assembly-exported-image-review-v1',[Path(__file__),*[ROOT/p for p in pins]],dict(uids=['landsd/254629:0','landsd/233002:0','landsd/256434:0','landsd/254621:0'],sourceGeometryAppearanceAccepted=True,publicationApproved=False));print(r['jobId'],flush=True)
if __name__=='__main__':main()
