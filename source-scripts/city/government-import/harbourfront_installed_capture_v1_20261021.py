"""Read-only complete current render attributes for the newly installed Harbourfront model."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-harbourfront-installed-capture-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();installation=BASE/'government-xl-harbourfront-tower-original-installed-v5-20261021';rec,pins=authenticate(installation);mp=ROOT/'3d-viewer/city/data/manifest.json';assert digest(mp.read_bytes())==rec['manifest']['sha256'];manifest=read(mp);refs=[Path(__file__),installation/'result.json',mp];rows=[]
sp=BASE/'government-xl-next-twenty-current-terrain-v6-20261021/selection.json.gz';_,ps=authenticate(sp.parent);assert digest(sp.read_bytes())==ps[str(sp.relative_to(ROOT))];by={r['uid']:r for r in read(sp)['rows']};refs.extend([sp,sp.parent/'result.json'])
for url in manifest['officialModelCatalogues']:
 p=ROOT/'3d-viewer'/url;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
 for entry in read(p)['models']:
  if entry['uid'] not in rec['installedUids']:continue
  r=by[entry['uid']];tile=ROOT/'3d-viewer'/r['source']['tile'];building=next(b for b in read(tile)['buildings']if b['uid']==entry['uid']);assert building==r['source']['building'];asset=p.parent/entry['asset'];assert digest(asset.read_bytes())==entry['sha256']==r['sourceSHA256'];refs.extend([tile,asset]);rows.append(dict(uid=entry['uid'],entry=entry,building=building,path=str(asset.relative_to(ROOT))))
rows.sort(key=lambda r:r['uid']);assert [r['uid']for r in rows]==['landsd/118230:0'];ref=lambda p:dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
save(DOC/'input.json.gz',dict(rows=rows,currentManifest=ref(mp),currentCatalogueRefs=[ref(ROOT/'3d-viewer'/u)for u in manifest['officialModelCatalogues']],evidenceRefs=[ref(p)for p in refs]))
tool=HERE/'central_piers_installed_attributes_v1_20261021.mjs';subprocess.run(['node',str(tool),str((DOC/'input.json.gz').relative_to(ROOT)),str((DOC/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,check=True)
capture=read(DOC/'attributes.json.gz');assert capture['startEndAllInputsVerified']and len(capture['rows'])==1 and not capture['rejected']
for p,h in capture['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
summary=dict(uids=[r['uid']for r in rows],loaded=1,installationApproved=False,sourceGeometryChanges=0);save(DOC/'summary.json',summary);refs.append(tool);r=module('pier_installed_capture_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'installed-harbourfront-complete-render-attributes',list(dict.fromkeys(refs)),summary);print(r['jobId'],flush=True)
