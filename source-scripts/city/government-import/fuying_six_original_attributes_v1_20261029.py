"""Fresh immutable source attributes for one private candidate and five installed peers."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-five-member-attributes-v1-20261029';CAP='government-xl-fuying181489-five-member-runtime-v2-20261029'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 doc=BASE/BATCH;assert not doc.exists();receipt,pins=authenticate(BASE/CAP);selectionpath=BASE/CAP/'selection.json.gz';assert ref(selectionpath)['sha256']==pins[str(selectionpath.relative_to(ROOT))];selection=read(selectionpath);assert receipt['allSixOriginalsCaptured']and len(selection['rows'])==6
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifestpath)['sha256']==selection['manifestSHA256'];manifest=read(manifestpath);catalogues=[ROOT/'3d-viewer'/u for u in manifest['officialModelCatalogues']];current={m['uid']:m for path in catalogues for m in read(path)['models']};expected={};rows=[]
 for row in selection['rows']:
  uid=row['uid'];entry=row['candidate']['entry'];assert uid==entry['uid']and row['sourceSHA256']==entry['sha256'];assert digest((ROOT/row['candidate']['path']).read_bytes())==entry['sha256']
  if uid=='landsd/181489:0':assert uid not in current
  else:assert current[uid]==entry
  expected[uid]=[entry['sha256'],entry['triangles']];rows.append(dict(uid=uid,entry=entry,building=row['source']['building'],path=row['candidate']['path']))
 save(doc/'input.json.gz',dict(currentManifest=ref(manifestpath),currentCatalogueRefs=[ref(p)for p in catalogues],evidenceRefs=[ref(selectionpath)],expectedSourceByUid=expected,rows=rows))
 tool=HERE/'selected_original_render_attributes_v1.mjs'
 with(doc/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str((doc/'input.json.gz').relative_to(ROOT)),str((doc/'attributes.json.gz').relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 attrs=read(doc/'attributes.json.gz');assert attrs['startEndAllInputsVerified']and {r['uid']:r['sourceSHA256']for r in attrs['rows']}=={u:v[0]for u,v in expected.items()};refs=[Path(__file__),tool,BASE/CAP/'result.json',selectionpath]
 for p,h in attrs['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=dict(uids=sorted(expected),sourceSHA256ByUid={u:v[0]for u,v in expected.items()},completeFaces=sum(v[1]for v in expected.values()),startEndAllInputsVerified=True,sourceGeometryChanges=0,sourcePoseChanges=0,currentAcceptance=False,nativeReacceptance=False,installationApproved=False,publication=False)
 module('fuying_six_attributes_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-six-original-four-stream-production-loader-attributes',refs,result)
if __name__=='__main__':main()
