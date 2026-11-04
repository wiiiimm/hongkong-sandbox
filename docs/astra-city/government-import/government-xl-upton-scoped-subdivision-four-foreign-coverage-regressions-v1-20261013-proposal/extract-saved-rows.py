"""Saved-row extraction only. No coverage, finite, source decode or DB calls."""
from pathlib import Path
import sys,json
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_scoped_subdivision_saved_actual_union_delta_draft_v1_20261013 as a
P=Path(__file__).parent
out=a.read(a.DOC/'complete-actual-union-finite-delta.json.gz')
attrs=a.read(a.baseline.CAP/'whole-domain-current-actors.json.gz')
original={r['uid']:r for r in a.read(a.baseline.ORIGINAL)['rows']}
refs=[a.ref(Path(__file__)),a.ref(a.DOC/'result.json'),a.ref(a.DOC/'complete-actual-union-finite-delta.json.gz'),a.ref(a.baseline.CAP/'whole-domain-current-actors.json.gz'),a.ref(a.baseline.ORIGINAL)]
rows=[]
for uid,ids in [(a.baseline.SECONDARY,[87,205,228]),('landsd/79883:0',[17])]:
 actor=next((r for r in out['actors']if r['uid']==uid),None)or next(r['findings']for r in out['completeBasicRows']if r['uid']==uid)
 if uid==a.baseline.SECONDARY:
  r=next(r for r in attrs['rows']if r['uid']==uid);ix=np.asarray(r['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
  worlds={m:np.asarray(r[k],dtype='<f8').reshape(-1,3)[ix]for m,k in zip(a.baseline.MODES[1:],a.baseline.FIELDS)}
  worlds['original']=np.asarray(original[uid]['completeOriginalBinary64WorldTriangles'],dtype='<f8')
 else:
  r=next(r for r in attrs['basicContextRows']if r['uid']==uid)
  worlds={'capturedConstructorFloat32World':np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index'],dtype=np.int64).reshape(-1,3)]}
 for w in actor['worlds']:
  world=worlds[w['mode']];assert a.sha(world)==w['wholeWorldSHA256']
  found=[]
  for q in w['findings']['chunks']:
   data=a.read(a.check(q))
   for row in data['rows']:
    if row['face']not in ids:continue
    refs.append(q);face=row['face'];assert a.sha(world[face])==row['currentBaselineVerbatim']['sourceFaceSHA256']
    final=row['findings'].get('oldKernelRecordVerbatim',row['findings']);coverage=final['coarse']['completeOriginalProjectionCoverage']
    assert row['currentBaselineVerbatim']['ordinaryBoundProved']and not final['projectionCovered']and not final['ordinaryBoundProved']
    rows.append(dict(uid=uid,mode=w['mode'],face=face,sourceFaceSHA256=a.sha(world[face]),sourceTriangleXYZ=world[face].tolist(),sourceTriangleBinary64Hex=world[face].tobytes().hex(),wholeWorldSHA256=w['wholeWorldSHA256'],sourceAttributeRecord=r['sourceSHA256']if uid==a.baseline.SECONDARY else 'captured-production-BASIC-constructor',chunk=q,completeSavedDeltaRowVerbatim=row,exactSavedAreaCoverage=coverage,noCoverageOrFiniteReplay=True));found.append(face)
  assert sorted(found)==ids
assert len(rows)==13
for q in refs:a.check(q)
path=P/'saved-four-foreign-full-facet-regression-rows.json.gz';assert not path.exists()
a.save(path,dict(rows=rows,evidenceRefs=list({(q['path'],q['sha256']):q for q in refs}.values()),completeRows=13,uniqueForeignFacets=4,currentManifestSHA256=a.baseline.CURRENT,newGroundSHA256=out['newGroundSHA256'],currentClearVsCandidateCoverageFailuresOnly=True,noRoleAcceptanceOrGeometryChange=True))
print(json.dumps(dict(passed=True,output=a.ref(path),rows=13,uniqueFacets=4),sort_keys=True))
