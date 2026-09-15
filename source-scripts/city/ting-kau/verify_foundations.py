"""Whole-foundation source/triangle audit, independent of the mask selector."""
import json, math, pathlib, hashlib, sys
import numpy as np
from shapely import intersects_xy
from shapely.geometry import Polygon, Point, shape, box
from shapely.ops import unary_union
from foundation_stage import HERE, ROOT, OUT, DOC, source_grid
sys.path.insert(0,str(HERE.parent/'tai-o-completion'))
from hydro_terrain import height
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def at(values, g, x, z):
    c=(x+834500-g['bE'])/5; r=(816500-z-g['bN'])/-5
    i=min(values.shape[1]-2,max(0,math.floor(c))); j=min(values.shape[0]-2,max(0,math.floor(r)))
    u,v=c-i,r-j; a,b,d,e=values[j,i],values[j,i+1],values[j+1,i],values[j+1,i+1]
    assert np.isfinite([a,b,d,e]).all()
    return float(a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v))


def triangle_audit(poly, patch, src, old):
    """Clip EVERY 5 m triangle to the whole target polygon, not sparse centres."""
    g=patch['meta']['georef']; x0=g['bE']-834500; z0=816500-g['bN']
    new=np.array(patch['elev']).reshape(src.shape)
    loX,loZ,hiX,hiZ=poly.bounds
    ranges=lambda a,b,o,n:range(max(0,math.floor((a-o)/5)),min(n-1,math.ceil((b-o)/5)))
    area=0; count=0; vertices=0; errors=[]; heights=[[],[],[]]
    for r in ranges(loZ,hiZ,z0,patch['h']):
        for c in ranges(loX,hiX,x0,patch['w']):
            x,z=x0+c*5,z0+r*5
            for pts in [[(x,z),(x,z+5),(x+5,z)],[(x+5,z),(x,z+5),(x+5,z+5)]]:
                clipped=Polygon(pts).intersection(poly)
                if clipped.area<1e-9: continue
                area+=clipped.area; count+=1
                parts=list(clipped.geoms) if hasattr(clipped,'geoms') else [clipped]
                for p in parts:
                    if not isinstance(p,Polygon):continue
                    for ring in [p.exterior,*p.interiors]:
                        for xx,zz in list(ring.coords)[:-1]:
                            a,b,d=at(src,g,xx,zz),height(patch,xx,zz),height(old,xx,zz)
                            errors.append(abs(a-b)); vertices+=1
                            for values,value in zip(heights,[a,b,d]):values.append(value)
    assert abs(area-poly.area)<.0001, (area,poly.area)
    assert max(errors)<.005001, {'maxError':max(errors),'bounds':poly.bounds}
    return {'mappedAreaM2':poly.area,'auditedTriangleAreaM2':area,'triangles':count,'clippedVertices':vertices,'sourceRangeHKPD':[min(heights[0]),max(heights[0])],'candidateRenderedRangeHKPD':[min(heights[1]),max(heights[1])],'previousRenderedRangeHKPD':[min(heights[2]),max(heights[2])],'maxSourceDifferenceMetres':max(errors)}


def verify():
    oldpath=HERE/'combined/terrain-tsing-ma-ting-kau.json'; old=read(oldpath)
    patch=read(OUT/'terrain-tsing-ma-ting-kau.json');hydro=read(OUT/'hydro-tsing-ma-ting-kau.json');baselinehydro=read(HERE/'combined/hydro-tsing-ma-ting-kau.json')
    stage=read(DOC/'staging.json'); assert sha(oldpath)==stage['originalCombined']['sha256']
    assert sha(OUT/'terrain-tsing-ma-ting-kau.json')==stage['candidateTerrain']['sha256']
    source,owners,sources=source_grid(old);g=patch['meta']['georef']
    assert patch['renderedElev']==old['renderedElev']
    features=read(OUT/'foundation-scope.geojson')['features'];scope=shape(features[0]['geometry'])
    xx,zz=np.meshgrid(g['bE']+np.arange(patch['w'])*5-834500,816500-g['bN']+np.arange(patch['h'])*5)
    mask=intersects_xy(scope,xx,zz);original=np.array(old['elev']).reshape(source.shape);candidate=np.array(patch['elev']).reshape(source.shape)
    assert np.array_equal(original[~mask],candidate[~mask]);assert np.max(abs(source[mask]-candidate[mask]))<.005001
    assert np.isfinite(source[mask]).all()
    water=unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in hydro['water']]);land=unary_union([box(*r['bounds']) for r in hydro['regions']]).difference(water)
    islands=[(f['properties']['name'],shape(f['geometry'])) for f in features if f['properties']['role']=='mapped-foundation-island']
    audits=[{'name':name,**triangle_audit(p,patch,source,old)} for name,p in islands]
    core=shape(next(f['geometry'] for f in features if f['properties']['role']=='source-restoration-core'))
    southern=core.intersection(land).difference(unary_union([p for _,p in islands]))
    audits.append({'name':'Southern Ting Kau footing: connected corrupted coastal land strips',**triangle_audit(southern,patch,source,old)})
    assert audits[0]['candidateRenderedRangeHKPD'][1]<11.3
    assert audits[1]['candidateRenderedRangeHKPD'][1]<10.7
    # The mask's dry-land transition must already agree with the original TIN.
    neighbours=np.zeros(source.shape,dtype=bool)
    for dr in [-1,0,1]:
        for dc in [-1,0,1]:neighbours|=np.roll(mask,(dr,dc),(0,1))
    edge=neighbours&~mask&intersects_xy(land,xx,zz)
    assert np.isfinite(source[edge]).all();assert np.max(abs(candidate[edge]-source[edge]))<.005001
    # Genuine north-shore slopes were already correct: do not flatten them.
    north=intersects_xy(Point(-8427.765,-8887.478).buffer(40).intersection(land),xx,zz)
    assert np.array_equal(candidate[north],original[north]);assert candidate[north].max()>27
    east=intersects_xy(Point(-8169,-7274).buffer(40).intersection(land),xx,zz)
    assert np.array_equal(candidate[east],original[east])
    assert hydro['water']==baselinehydro['water'];assert hydro['bedTriangles']==baselinehydro['bedTriangles']
    cutcount=0; tested=0
    for cut in hydro['terrainCuts']:
        ids=[(cell['c'],cell['r']) for cell in cut['cells']];assert len(ids)==len(set(ids));cutcount+=len(ids)
        for cell in cut['cells']:
            for tri in np.array(cell['land']).reshape(-1,3,3):
                footprint=Polygon(tri[:,[0,2]])
                assert footprint.intersection(water).area<.002
                if not footprint.intersects(core):continue
                for x,y,z in tri:
                    assert abs(y-height(patch,x,z))<.0001
                    assert abs(y-at(source,g,x,z))<.0051
                    tested+=1
    # Full exterior and both former seams remain the accepted common mosaic.
    border=np.zeros(source.shape,dtype=bool);border[[0,-1],:]=True;border[:,[0,-1]]=True
    assert np.array_equal(candidate[border],original[border])
    seam=[]
    for N in [824027.5,824167.5]:
        points=[(E-834500,816500-N) for E in range(825655,826981,5)]
        assert all(height(patch,x,z)==height(old,x,z) for x,z in points)
        seam.append({'northing':N,'samples':len(points),'maximumChangeMetres':0})
    originalpackets=read(ROOT/'docs/astra-city/ting-kau/combined/verification.json')['immutableBridgePayloads']
    for record in originalpackets:assert sha(ROOT/record['path'])==record['sha256']
    centres=[[-9500,-6860],[-8427.765,-8887.478],[-8229.83,-8485.528],[-8019.633,-8059.256]]
    report={'status':'pass','method':'Every clipped 5 m grid triangle across both complete mapped islands and the connected southern coastal repair is compared with the retained original source-TIN grid. This checks the 5 m resampling, not unsampled engineering detail.','wholeFoundationAudits':audits,'guardVertices':int(mask.sum()),'guardSourceErrorMetres':float(abs(source[mask]-candidate[mask]).max()),'changedGridVertices':int((original!=candidate).sum()),'outsideGuardUnchangedVertices':int((~mask).sum()),'dryTransitionNeighbourVertices':int(edge.sum()),'dryTransitionSourceErrorMetres':float(abs(candidate[edge]-source[edge]).max()),'genuineNorthShoreRangeHKPD':[float(candidate[north].min()),float(candidate[north].max())],'northAndEastShoreUnchanged':True,'replacementCutVerticesChecked':tested,'uniqueCutCells':cutcount,'mappedWaterAndBedUnchanged':True,'outerTransitionUnchanged':True,'formerSeams':seam,'originalBridgePayloadsUnchanged':originalpackets,'sourceGridHashes':sources,'sampleFoundations':[{'world':p,'candidateHeightHKPD':height(patch,*p)} for p in centres],'terrainSha256':sha(OUT/'terrain-tsing-ma-ting-kau.json'),'hydroSha256':sha(OUT/'hydro-tsing-ma-ting-kau.json'),'livePublished':False,'gpuUsed':False}
    (DOC/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['originalBridgePayloadsUnchanged','sourceGridHashes']},indent=2));return report

if __name__=='__main__':verify()
