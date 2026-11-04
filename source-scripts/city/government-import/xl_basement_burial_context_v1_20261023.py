"""Classify immutable original source faces against explicit recorded base height.

Diagnostic only: no underground-geometry exception or physical approval.
"""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';N='government-xl-official-basement-context-v1-20261023';T='government-xl-all-200-original-terrain-batch-v2-20261022';B='government-xl-basement-burial-context-v1-20261023';D=BASE/B
assert not D.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
for n in [N,T]:
 _,pins[n]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
def take(n,p):
 assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
context=take(N,BASE/N/'summary.json');assets={sha:ROOT/path for path,sha in pins[T].items()if path.endswith('.glb.gz')};rows=[]
for r in context['rows']:
 if not r['belowGradeGeometryNominated']:continue
 asset=assets[r['sourceSHA256']];blob=asset.read_bytes();assert digest(blob)==r['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(blob);base=r['officialBaseHeightHKPD'];assert len(tri)==r['nativeModel']['triangles']
 old=take(T,BASE/T/(r['uid'].split('/')[1]+'.json'));assert old['sourceSHA256']==r['sourceSHA256']and old['originalSourceTriangles']==len(tri)
 assert digest(tri.astype('<f8').tobytes())==old['originalWorldSHA256']
 below=tri[:,:,1].max(1)<=base;above=tri[:,:,1].min(1)>=base;crossing=~below&~above;foundation=old.get('originalTerrainFoundation');details=None
 if foundation is not None:
  components=foundation['components'];accounted=sum(c['triangles']for c in components);assert accounted==foundation['fullyBuriedTriangles']
  low=[c for c in components if c['yRange'][1]<=base]
  details=dict(rawWholeBuriedFaces=foundation['fullyBuriedTriangles'],rawWholeBuriedUpwardFaces=foundation['fullyBuriedUpwardTriangles'],belowRecordedBaseBuriedFaces=sum(c['triangles']for c in low),belowRecordedBaseBuriedUpwardFaces=sum(c['upwardTriangles']for c in low),allOriginalTINBurialComponentsBelowRecordedBase=bool(accounted and sum(c['triangles']for c in low)==accounted),rawBurialComponents=components,sourceTerrainPaths=old['sourceTerrainPaths'])
 report=dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],sourceWorldSHA256=old['originalWorldSHA256'],officialPrimaryRecord=r['officialPrimaryRecord'],officialStructureRecords=r['officialStructureRecords'],officialBaseHeightHKPD=base,originalFaces=len(tri),indexedOriginalMinimumY=float(tri[:,:,1].min()),whollyAtOrBelowRecordedBaseFaces=int(below.sum()),whollyAtOrAboveRecordedBaseFaces=int(above.sum()),crossingRecordedBaseFaces=int(crossing.sum()),originalTINBurialContext=details,physicalAcceptance=False,installationApproved=False)
 rows.append(report);save(D/(r['uid'].split('/')[1]+'.json'),report)
 save(D/(r['uid'].split('/')[1]+'-face-classes.json.gz'),dict(sourceSHA256=r['sourceSHA256'],sourceWorldSHA256=old['originalWorldSHA256'],recordedBaseHeight=base,belowOrAt=np.flatnonzero(below).tolist(),aboveOrAt=np.flatnonzero(above).tolist(),crossing=np.flatnonzero(crossing).tolist(),note='Analysis classifications only; no source index/position edits or renderer filtering. Coplanar-at-base faces can belong to both closed halfspaces.'))
summary=dict(uids=[r['uid']for r in rows],rows=rows,counts=dict(sources=len(rows),withOriginalTINFoundation=sum(r['originalTINBurialContext']is not None for r in rows),allBuriedComponentsBelowRecordedBase=sum(bool(r['originalTINBurialContext']and r['originalTINBurialContext']['allOriginalTINBurialComponentsBelowRecordedBase'])for r in rows)),sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0,qualification='Exact indexed original faces classified by a fresh official recorded base and basement metadata. Historical original-TIN component accounting is source context only, not current-scene approval. No role/function inference for individual faces, no below-grade exemption or guard/tolerance change. Any legitimate-basement interpretation still needs full source/current/four-world/support/neighbour/collision/visual proof under applicable acceptance requirements.')
save(D/'summary.json',summary);module('basement_burial_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'exact-original-basement-burial-context',refs,summary)
print(summary['counts'],flush=True)
print([(r['uid'],r['originalTINBurialContext'])for r in rows if r['originalTINBurialContext']and r['originalTINBurialContext']['allOriginalTINBurialComponentsBelowRecordedBase']],flush=True)
