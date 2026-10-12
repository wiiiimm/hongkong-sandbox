from pathlib import Path
from fractions import Fraction as F
import json,hashlib,sys
import numpy as np
R=Path(__file__).resolve().parents[4];H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H))
import upton_v6_saved_actual_union_finite_regression_draft_v3_20261013 as c

def forbidden(*a,**k):raise AssertionError('No finite, DB, reservation or worker permitted in interface smoke')
c.finite_record=forbidden;c.connect=forbidden;c.reservations.claim=forbidden
pins,replay,ground,prior_ground,old,attrs,scope,actors=c.inputs()
uid,worlds,saved,source=actors[0];mode='original';w=worlds[mode];baseline=next(v for v in saved['worlds']if v['mode']==mode);i=baseline['selectedFaceIDs'][0];face=w[i];before=c.sha(w);face_before=face.tobytes();exact=[[F(x)for x in p]for p in face.tolist()]
assert all(float(q)==x and q==F(float(x))for p,e in zip(face,exact)for x,q in zip(p,e))
rows=[]
for name,g in [('new',ground),('old',prior_ground)]:
 complete=c.CompleteGround(g);ids,binding=complete.select(exact);complete.verify_binding()
 lo=face[:,[0,2]].min(0);hi=face[:,[0,2]].max(0)
 direct=np.flatnonzero(~np.any((g[:,:,[0,2]].max(1)<lo)|(g[:,:,[0,2]].min(1)>hi),axis=1))
 assert np.array_equal(ids,direct)
 prior=next(v for v in baseline['findings']['rows']if v['face']==i)['candidate'];coarse=prior['coarse'];old_ids=None
 if name=='old'and coarse is not None:
  old_ids=coarse['allProjectedBoundingCandidateOriginalGroundFacets'];assert ids.tolist()==old_ids
 rows.append(dict(name=name,completeGroundSHA256=c.sha(g),completeFaces=len(g),selectedGroundFaceIDs=ids.tolist(),directClosedAABBFaceIDs=direct.tolist(),completeSelection=binding,priorCoarseCandidateIDs=old_ids,priorIDsCompared=bool(name=='old'and coarse is not None),exactSelectorEqualsIndependentClosedAABB=True))
assert c.sha(w)==before and face.tobytes()==face_before
print(json.dumps(dict(passed=True,uid=uid,mode=mode,originalFaceID=i,sourceSHA256=source,wholeWorldSHA256=before,sourceFaceSHA256=c.sha(face),sourceArrayUnchanged=True,exactBinary64Ratios=[[str(q)for q in p]for p in exact],originalFaceBinary64=face.tolist(),rows=rows,noFiniteKernelDBLeaseOrClaim=True),sort_keys=True))
