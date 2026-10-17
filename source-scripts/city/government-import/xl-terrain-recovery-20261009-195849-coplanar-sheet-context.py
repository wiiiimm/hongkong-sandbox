"""Source-only exact coplanar exterior continuation, no acceptance or pose edits."""
import numpy as np,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from original_coplanar_exterior_continuation_20261009 import diagnose
D=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-195849-coplanar-sheet-context';assert not D.exists();lease=read('/tmp/xl-terrain-recovery-20261009-195849-role-lease.json');assert reservations.heartbeat(lease)['ok']
context=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-195849-wall-context/diagnostic.json.gz';geometry=HERE/'local/government-xl-fourteen-positive-cell-sequence-20261008-195849-0/runtime-geometry.json.gz';d=read(context);g=read(geometry)['rows'][0];tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert d['sourceSHA256']==g['sourceSHA256']
r=diagnose(tri,d['faces'],[285,365,413]);r.update(uid=d['uid'],sourceSHA256=d['sourceSHA256'],historicalNotCurrentAcceptance=True,evidenceRefs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [Path(__file__),context,geometry,HERE/'original_coplanar_exterior_continuation_20261009.py',HERE/'test_original_coplanar_exterior_continuation_20261009.py']]);save(D/'diagnostic.json.gz',r);print(json.dumps({'rows':[{'sourceFace':x['sourceFace'],'sheetFaces':len(x['exactConnectedCoplanarSheetFaces']),'exposedFaces':x['exposedOriginalSheetFaces']} for x in r['rows']]}))
