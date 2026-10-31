"""Record exact derived upper-envelope overlap without changing its assertion."""
import sys
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,save,digest

batch=sys.argv[sys.argv.index('--batch')+1]
assert batch.startswith('government-xl-') and '/' not in batch
out=ROOT/'docs/astra-city/government-import'/batch
canonical=HERE/'selected_original_local_inset_v16_20261030.py'

def record(polygons,faces,lineage,planes,original_union):
    total=float(shapely.area(polygons).sum());union=shapely.union_all(polygons)
    if abs(total-union.area)<1e-6:return
    pairs=[];tree=shapely.STRtree(polygons)
    for i,p in enumerate(polygons):
        for j in tree.query(p,predicate='intersects'):
            j=int(j)
            if j<=i:continue
            overlap=p.intersection(polygons[j])
            if overlap.area<=1e-12:continue
            a,b=np.asarray(planes[lineage[i]]),np.asarray(planes[lineage[j]])
            q=overlap.representative_point();difference=a-b
            pairs.append(dict(faces=[i,j],originalTerrainFaces=[int(lineage[i]),int(lineage[j])],areaM2=float(overlap.area),overlapWKB=overlap.wkb_hex,sourcePlanes=[a.tolist(),b.tolist()],representativeHeightDifferenceM=float(difference@[q.x,q.y,1])))
    pairs.sort(key=lambda p:p['areaM2'],reverse=True)
    save(out/'upper-envelope-overlaps.json.gz',dict(pairs=pairs,derivedFaces=faces.tolist(),sourceLineage=list(map(int,lineage))))
    save(out/'upper-envelope-diagnostic.json',dict(totalAreaM2=total,unionAreaM2=float(union.area),overlapExcessM2=total-float(union.area),coverageDifferenceM2=float(union.symmetric_difference(original_union).area),positiveOverlapPairs=len(pairs),largestPairs=pairs[:12],existingAreaToleranceM2=1e-6,tolerancesChanged=False,sourceGeometryChanges=0,installationApproved=False,canonicalSHA256=digest(canonical.read_bytes()),instrumentationPath=str(Path(__file__).relative_to(ROOT)),instrumentationSHA256=digest(Path(__file__).read_bytes())))

text=canonical.read_text();needle='        assert abs(float(shapely.area(polygons).sum()-shapely.union_all(polygons).area)) < 1e-6'
assert text.count(needle)==1
instrumented=text.replace(needle,'        record(polygons,source,upperlineage,planes,union)\n'+needle)
namespace={'__file__':str(canonical),'__name__':'diagnostic_canonical_inset','record':record}
exec(compile(instrumented,str(canonical),'exec'),namespace)
namespace['main']()
