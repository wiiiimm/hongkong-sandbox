"""Whole-domain BASIC and nine touching-native before/after regression checks."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-fuying181489-five-member-neighbours-v1-20261029';SCOPE='government-xl-fuying181489-five-member-full-scope-v1-20261029';RUNTIME='government-xl-fuying181489-five-member-runtime-v2-20261029'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 for n in [SCOPE,RUNTIME]:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
 def take(n,p):assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 scope=take(SCOPE,BASE/SCOPE/'scope.json');forms=take(SCOPE,BASE/SCOPE/'form-obligations.json.gz');patches=take(RUNTIME,BASE/RUNTIME/'terrain-candidates.json');assert len(patches)==5 and scope['currentNativeActors']==7021 and scope['unreviewedPositiveAreaTerrainOverlaps']==0
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=take(SCOPE,manifestpath);tiles={r['id']:r['url']for r in manifest['tiles']};currentNative={m['uid']for u in manifest['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/u)['models']};hashes={str(manifestpath.relative_to(ROOT)):digest(manifestpath.read_bytes())};rows=[]
 for form in forms:
  tile=ROOT/'3d-viewer'/tiles[form['tile']];assert digest(tile.read_bytes())==pins[SCOPE][str(tile.relative_to(ROOT))];assert [b for b in read(tile)['buildings']if b['uid']==form['uid']]==[form];refs.append(tile);hashes[str(tile.relative_to(ROOT))]=digest(tile.read_bytes());rows.append(dict(building=form,existingNative=form['uid']in currentNative,patchIndexes=list(range(5))))
 save(out/'neighbour-inputs.json.gz',dict(inputHashes=hashes,candidateIds=scope['uids'],patches=patches,rows=rows,requiredNativeUids=scope['touchingNativeUids']))
 for toolname in ['check-neighbours-multi-retained.mjs','check-native-neighbours-multi-retained-scoped-v4.mjs']:
  tool=HERE/toolname;refs.append(tool)
  with(out/(toolname+'.log')).open('w')as log:subprocess.run(['node',str(tool),str(out.relative_to(ROOT))+'/'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 ordinary=read(out/'neighbour-checks.json');native=read(out/'native-neighbour-checks.json');assert len(ordinary['rows'])==len(forms)and set(scope['touchingNativeUids'])<=set(native['blocked']);assert {r['uid']for r in native['rows']}==set(native['blocked'])
 flagged=[r for r in ordinary['rows']if r['reasons']];unresolved=[r for r in flagged if not r['existingNative']or r['uid']not in native['resolved']]
 for report in [ordinary,native]:
  for p,h in report['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=dict(uids=scope['uids'],forms=len(forms),requiredNativeUids=scope['touchingNativeUids'],allNativeRows=native['rows'],flaggedForms=flagged,unresolved=unresolved,allNativeResolved=set(native['blocked'])==set(native['resolved']),allNeighbourRegressionsResolved=not unresolved and set(native['blocked'])==set(native['resolved']),sourceGeometryChanges=0,sourcePoseChanges=0,physicalAcceptance=False,installationApproved=False,publication=False)
 save(out/'summary.json',result);module('fuying_full_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-whole-domain-basic-and-touching-original-native-regression',list(dict.fromkeys(refs)),result);print(dict(forms=len(forms),native=len(native['rows']),unresolved=len(unresolved),allNativeResolved=result['allNativeResolved']),flush=True)
if __name__=='__main__':main()
