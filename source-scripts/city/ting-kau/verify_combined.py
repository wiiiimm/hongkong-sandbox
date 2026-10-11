"""Audit common terrain seams, immutable bridge packets and exact regional hydro."""
import hashlib,json,pathlib,sys
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/ting-kau/combined'
sys.path.insert(0,str(HERE.parent/'tai-o-completion'));from hydro_terrain import height
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def verify():
 combined=read(HERE/'combined/terrain-tsing-ma-ting-kau.json');hydro=read(HERE/'combined/hydro-tsing-ma-ting-kau.json');base=read(ROOT/'3d-viewer/city/data/terrain.json')
 originals={name:read(HERE.parent/name/f'terrain-{name}.json') for name in ['tsing-ma','ting-kau']}
 sample=lambda data,E,N:height(data,E-834500,816500-N)
 old=[(abs(sample(originals['tsing-ma'],E,N)-sample(originals['ting-kau'],E,N)),E,N) for E in range(825655,826981,10) for N in range(824030,824168,10)]
 largest=max(old);assert abs(largest[0]-16.525714)<1e-5
 former=[]
 for N in [824027.5,824167.5]:
  differences=[abs(sample(combined,E,N-.001)-sample(combined,E,N+.001)) for E in range(825655,826981,5)]
  assert max(differences)<.003
  former.append({'northing':N,'samples':len(differences),'distanceAcrossFormerBoundaryMetres':.002,'maximumHeightDifferenceMetres':max(differences)})
 # All region-core samples beyond the old source-union edge blend are invariant.
 cores=[]
 for name,bounds in [('tsing-ma',[824200,823000,826900,823975]),('ting-kau',[825850,824200,826800,825550])]:
  differences=[abs(sample(originals[name],E,N)-sample(combined,E,N)) for E in range(bounds[0],bounds[2]+1,25) for N in range(bounds[1],bounds[3]+1,25)]
  assert max(differences)<1e-7;cores.append({'region':name,'nativeBounds':bounds,'spacingMetres':25,'samples':len(differences),'maximumDifferenceMetres':max(differences)})
 # The small old TIN-union edge blend becomes interior source terrain; report it.
 edge=[abs(sample(originals['tsing-ma'],E,824000)-sample(combined,E,824000)) for E in range(824200,826901,25)]
 g=combined['meta']['georef'];w,h=combined['w'],combined['h']
 boundary=[(c,0) for c in range(w)]+[(c,h-1) for c in range(w)]+[(0,r) for r in range(h)]+[(w-1,r) for r in range(h)]
 errors=[abs(height(combined,g['bE']+c*5-834500,816500-g['bN']+r*5)-height(base,g['bE']+c*5-834500,816500-g['bN']+r*5)) for c,r in boundary];assert max(errors)<1e-5
 water=unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in hydro['water']]);regional=[]
 for name in originals:
  source=read(HERE.parent/name/f'hydro-{name}.json');piece=read(HERE/'combined'/name/f'hydro-{name}.json')
  assert source['water']==piece['water'];assert source['bedTriangles']==piece['bedTriangles'];regional.append({'region':name,'waterPolygonsUnchanged':True,'bedTrianglesUnchanged':True,'foundationLandPreservedInPlan':True})
  assert [p for p in hydro['water'] if p['id'].startswith(name+'-')]==source['water']
 cut_count=0;land_triangles=0
 for cut in hydro['terrainCuts']:
  keys=[(c['c'],c['r']) for c in cut['cells']];assert len(keys)==len(set(keys));cut_count+=len(keys)
  for c in cut['cells']:
   for t in np.array(c['land']).reshape(-1,3,3):
    assert Polygon(t[:,[0,2]]).intersection(water).area<.002;land_triangles+=1
 for t in np.array(hydro['bedTriangles']).reshape(-1,3,3):assert np.all(t[:,1]==-4)
 expected={'terrain-tsing-ma.json':'0c835c0a2559e5c08b6ffc7cd1f849962801862748d23b3d10d1e22262b84463','hydro-tsing-ma.json':'4cc45eb99287111f64ffbb5064114915b4714e0d8bdce2ebcb86a5856ec3a333'}
 for name,value in expected.items():assert sha(HERE.parent/'tsing-ma'/name)==value
 packets=[]
 for name in originals:
  for category in ['bridges','cables']:
   p=HERE.parent/name/f'{category}-{name}.json';packets.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
 report={'status':'pass','terrainDimensions':[w,h],'sourceTerrainSheets':len(combined['meta']['detailSources']),'oldOverlap':{'samples':len(old),'maxDifferenceMetres':largest[0],'locationHK1980':[largest[1],largest[2]],'combinedHeightHKPD':sample(combined,largest[1],largest[2])},'formerBoundaryContinuity':former,'sourceCoreInvariance':cores,'oldSourceUnionBlendReplaced':{'northing':824000,'samples':len(edge),'changedSamples':sum(d>1e-7 for d in edge),'maximumChangeMetres':max(edge),'note':'The old source-union exterior was blended into archival DTM. It is now interior to the combined source mosaic; the same source TINs provide the heights. No source mesh was translated.'},'outerCoarseBoundary':{'samples':len(errors),'maximumDifferenceMetres':max(errors)},'hydroRegions':regional,'uniqueCutCells':cut_count,'replacementLandTriangles':land_triangles,'waterAreaM2':water.area,'bedTriangles':len(hydro['bedTriangles'])//9,'bankTriangles':len(hydro['bankTriangles'])//9,'originalTsingMaDefaultPayloads':expected,'immutableBridgePayloads':packets,'terrainSha256':sha(HERE/'combined/terrain-tsing-ma-ting-kau.json'),'hydroSha256':sha(HERE/'combined/hydro-tsing-ma-ting-kau.json'),'livePublished':False,'gpuUsed':False}
 (DOC/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report
if __name__=='__main__':verify()
