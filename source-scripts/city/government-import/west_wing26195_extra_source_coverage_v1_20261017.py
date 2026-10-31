"""Check actual source facets for every new bounding-box nominee; no approval."""
from pathlib import Path
import shapely
from shapely.geometry import shape,mapping
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing26195-extra-source-coverage-v1-20261017';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-west-wing26195-missing-sheet-candidates-v2-20261017';COVER=BASE/'government-xl-west-wing26195-missing-coverage-v1-20261017';ASSEMBLY=BASE/'government-xl-west-wing26195-original-assembly-projection-v2-20261015';UID='landsd/26195:0'
def main():
 assert not DOC.exists();receipt=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 known={r['sourceSHA256']for r in read(ASSEMBLY/'projection.json')['rows']};nominees=read(PRIOR/'candidates.json.gz')['rows'];new=[r for r in nominees if r['model']['asset']['sha256']not in known];assert len(new)==1
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=digest(manifest.read_bytes());entries={};refs=[Path(__file__),PRIOR/'result.json',PRIOR/'candidates.json.gz',COVER/'missing-components.geojson',ASSEMBLY/'projection.json',manifest]
 for url in read(manifest)['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if any(e['sha256']==r['model']['asset']['sha256']for r in new):entries[e['sha256']]=(p,e)
 regions=read(COVER/'missing-components.geojson')['features'];missing=shapely.union_all([shape(r['geometry'])for r in regions]);remaining=missing;rows=[]
 for r in new:
  m=r['model'];h=m['asset']['sha256'];cat,e=entries[h];p=cat.parent/e['asset'];raw=p.read_bytes();assert digest(raw)==h;tri=decode_original_world_triangles(raw);assert len(tri)==m['triangles'];polys=shapely.polygons(tri[:,:,[0,2]]);proj=shapely.union_all(polys[shapely.area(polys)>0]);coverage=remaining.intersection(proj);remaining=remaining.difference(proj);refs.extend([cat,p]);rows.append(dict(uid=e['uid'],label=e.get('label'),sourceSHA256=h,sourceModelId=m['modelId'],completeOriginalFaces=len(tri),nominatedBoundingOverlapM2=r['missingBoundingOverlapM2'],actualNewCoverageM2=coverage.area,componentCoverage=[dict(component=f['properties']['component'],actualCoverageM2=proj.intersection(shape(f['geometry'])).area)for f in regions if proj.intersection(shape(f['geometry'])).area>0]))
 assert digest(manifest.read_bytes())==start;assert abs(missing.area-sum(r['actualNewCoverageM2']for r in rows)-remaining.area)<1e-6
 save(DOC/'remaining.geojson',mapping(remaining));summary=dict(uid=UID,allSheetSources=66,boundingNominees=4,previouslyComparedSourceHashes=3,actualNewSources=len(new),priorNominationCountCorrection='The West Wing source has no viewerMatches entry; classify previously compared sources by immutable SHA, not viewer UID presence. V2 newCandidateCount=2 includes that already-tested original; there is one actual new source.',rows=rows,missingBeforeM2=missing.area,remainingM2=remaining.area,identityAccepted=False,sourceGeometryChanges=0,adjacentSheetsExcluded=False)
 save(DOC/'summary.json',summary);refs.append(HERE/'exact_packed_world_geometry_20261009.py')
 out=module('west_extra_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-new-sheet-source-actual-footprint-coverage-v1',refs,dict(uids=[UID],summary=summary,nextStep='Resolve remaining exact footprint regions against architectural/primary source evidence or adjoining original sheets; do not repeat this sheet bounds/mesh check unchanged.'))
 print(dict(jobId=out['jobId'],newCoverageM2=sum(r['actualNewCoverageM2']for r in rows),remainingM2=remaining.area),flush=True)
if __name__=='__main__':main()
