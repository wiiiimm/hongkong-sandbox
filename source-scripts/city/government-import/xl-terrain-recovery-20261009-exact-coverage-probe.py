"""Exact source-specific diagnosis of GEOS closed-facet union seam residues."""
import sys,numpy as np,shapely,json
from run import ROOT,HERE,read,save,digest,reservations
from exact_original_projection_coverage_20261009 import exact_coverage
uid=sys.argv[1];context=ROOT/'docs/astra-city/government-import'/('xl-terrain-recovery-20261009-'+uid+'-wall-context/diagnostic.json.gz')
d=read(context);batch={'195849':'government-xl-fourteen-positive-cell-sequence-20261008-195849-0','313033':'government-xl-market-in-retained-cell-partition-20261007'}[uid];geometry=HERE/'local'/batch/'runtime-geometry.json.gz';g=next(r for r in read(geometry)['rows'] if r['uid']==d['uid']);lease=read('/tmp/xl-terrain-recovery-20261009-'+uid+'-role-lease.json');assert reservations.heartbeat(lease)['ok']
tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3);filtered=ground[shapely.area(shapely.polygons(ground[:,:,[0,2]]))>1e-10]
assert len(tri)==d['wholeSourceFaces'] and g['sourceSHA256']==d['sourceSHA256']
rows=[]
for c in d['faces']:
 if c['groundProjectionCovered']:continue
 i=c['sourceFace'];a=exact_coverage(tri[i],filtered);b=exact_coverage(tri[i],ground)
 rows.append({'originalFace':i,'rawPriorCoverageFalseRetained':c,'exactSamePriorFilteredGround':a,'exactCompleteUnfilteredDrawnGround':b});assert reservations.heartbeat(lease)['ok']
result={'uid':d['uid'],'sourceSHA256':d['sourceSHA256'],'completeOriginalSourceFaces':len(tri),'rawPriorUncoveredFaces':d['wholeSourceUncoveredFaces'],'rows':rows,'everyPriorFloatingResidueExactlyCoveredWithSameGround':all(r['exactSamePriorFilteredGround']['exactProjectionCovered'] for r in rows),'wholeGroundTriangleCount':len(ground),'samePriorFilteredGroundTriangleCount':len(filtered),'sourceGeometryChanges':0,'noToleranceCredit':True,'diagnosticOnly':True,'installationApproved':False,'publication':False,'evidenceRefs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())} for p in [context,geometry,HERE/'exact_original_projection_coverage_20261009.py',HERE/'test_exact_original_projection_coverage_20261009.py',__import__('pathlib').Path(__file__)]]}
out=ROOT/'docs/astra-city/government-import'/('xl-terrain-recovery-20261009-'+uid+'-exact-coverage-probe/diagnostic.json.gz');assert not out.exists();save(out,result);print(json.dumps({k:result[k] for k in ['uid','rawPriorUncoveredFaces','everyPriorFloatingResidueExactlyCoveredWithSameGround']}))
