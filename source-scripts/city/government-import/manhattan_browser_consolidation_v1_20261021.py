"""Account for each completed browser witness; preserve failed whole-run reports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-browser-consolidation-v1-20261021';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 for name in ['assembly-capture-v1','private-terrain-v3','private-browser-v3','private-browser-v6']:
  folder=BASE/('government-xl-manhattan-'+name+'-20261021');r=read(folder/'result.json')
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json');pins[name]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def bound(name,p):
  assert digest(p.read_bytes())==pins[name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 cap=BASE/'government-xl-manhattan-assembly-capture-v1-20261021';selection=bound('assembly-capture-v1',cap/'selection.json.gz');sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==8
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 reports=[];views=[];fallback=set();canonical=None
 for version,width in [(3,1280),(3,390),(4,1280),(5,390),(6,1280),(6,390)]:
  name=f'government-xl-manhattan-private-browser-v{version}-20261021';folder=BASE/name;local=HERE/'local'/name
  cat=read(local/'catalogue.json');assert {m['uid']:m['sha256']for m in cat['models']}==sources
  if canonical is None:canonical=cat
  else:assert cat==canonical
  for m in cat['models']:
   p=local/m['asset'];assert digest(p.read_bytes())==m['sha256'];refs.append(p)
  config=read(local/f'browser-config-{width}.json');assert len(config['terrain'])==1
  for t in config['terrain']:
   p=ROOT/t['source'];assert digest(p.read_bytes())==t['sha256'];bound('private-terrain-v3',p)
  validation=read(folder/'validation.json');assert validation['loaderAccepted']==8 and not validation['exceptions']
  for p,h in validation['hashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  reportpath=folder/str(width)/'staged-browser.json';r=read(reportpath)
  if version==5:
   assert not r.get('passed') and len(r['errors'])==1 and "'landsd/266799:0'"in r['errors'][0] and "'landsd/258271:0'"in r['errors'][0]
   assert {v['uid']for v in r['views']if 'time'in v}==set(sources)-{'landsd/120103:0','landsd/266799:0','landsd/213072:0','landsd/258271:0'}
  else:assert r['passed']and not r['errors']
  if version in [3,6]:bound(f'private-browser-v{version}',reportpath)
  for v in r['views']:
   if 'time'not in v:
    if width==390 and v.get('phase')=='failed-download'and v['fallbackRetained']and not(version==5 and v['uid']=='landsd/258271:0'):fallback.add(v['uid'])
    continue
   assert v['fullyFramed']and v['active']and v['visible']and v['solidAppearance']and not v['fallbackFaces']and not v['overflow']
   assert v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
   if version==6:
    probes=v['collisionProbes'];assert probes and probes[-1]['uid']==v['uid']
   image=folder/str(width)/v['file'];assert image.is_file();refs.append(image);views.append(dict(version=version,**v))
  refs.extend([reportpath,folder/'validation.json',local/'catalogue.json',local/f'browser-config-{width}.json',folder/f'browser-{width}.log'])
  reports.append(dict(path=str(reportpath.relative_to(ROOT)),sha256=digest(reportpath.read_bytes()),wholeRunPassed=bool(r.get('passed')),errors=r['errors']))
 assert fallback==set(sources)
 for uid in sources:
  for width in [1280,390]:assert {v['time']for v in views if v['uid']==uid and v['width']==width}=={'15:00','22:00'}
 result=dict(uids=sorted(sources),sourceSHA256ByUid=sources,views=views,reports=reports,allCandidatesHaveDayNightDesktopMobileWitnesses=True,allCandidatesHaveFailedDownloadRecovery=True,failedWholeRunsRetained=True,qualification='V5 is a failed whole run; only its four completed per-model view/retry pairs are used. V6 independently resolves the final component and retains attempted source-face collision probes. This accounts runtime witnesses, not whole-source collision nonintersection or visual approval.',visualAcceptance=False,installationApproved=False)
 save(DOC/'BROWSER-ACCOUNTING.json',result)
 module('manhattan_browser_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'per-source-desktop-mobile-browser-witness-accounting',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
