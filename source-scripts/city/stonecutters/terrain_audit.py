"""Audit inherited ridge, complete mapped port land and retained source coverage."""
import hashlib,json,pathlib,sys,numpy as np
from shapely import intersects_xy
from shapely.geometry import Polygon,box,Point
from shapely.ops import unary_union
from fetch import HERE,ROOT
sys.path.insert(0,str(HERE.parent/'tai-o-completion'));from hydro_terrain import height

def audit():
    patch=json.loads((HERE/'terrain-stonecutters.json').read_text());hydro=json.loads((HERE/'hydro-stonecutters.json').read_text());coarse=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());g=patch['meta']['georef'];src=np.full((patch['h'],patch['w']),np.nan);sources=[]
    for file in sorted((HERE/'terrain/clipped-grids').glob('*.json')):
        d=json.loads(file.read_text());sg=d['meta']['georef'];dc=round((sg['bE']-g['bE'])/5);dr=round((g['bN']-sg['bN'])/5);a=np.array(d['elev'],dtype=float).reshape(d['h'],d['w']);dest=src[dr:dr+d['h'],dc:dc+d['w']];valid=np.isfinite(a);assert not(np.isfinite(dest)&valid).any();dest[valid]=a[valid];sources.append({'path':str(file.relative_to(ROOT)),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
    xx,zz=np.meshgrid(g['bE']+np.arange(patch['w'])*5-834500,816500-g['bN']+np.arange(patch['h'])*5);water=unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in hydro['water']]);land=box(*hydro['bounds']).difference(water);mask=intersects_xy(land,xx,zz);valid=mask&np.isfinite(src);raw=np.array(patch['elev']).reshape(src.shape);bad=valid&(abs(raw-src)>.006)
    foundations=[]
    for name,x,z in [('Tsing Yi',-4634.028,-4573.747),('Stonecutters Island',-3849.81,-3924.645)]:
        keep=intersects_xy(Point(x,z).buffer(40).intersection(land),xx,zz);known=keep&np.isfinite(src);error=abs(raw[known]-src[known]);foundations.append({'name':name,'centre':[x,z],'mappedLand':land.covers(Point(x,z)),'renderedCentreHKPD':height(patch,x,z),'mappedLandNodesWithin40m':int(keep.sum()),'sourceCoveredNodes':int(known.sum()),'sourceRangeHKPD':[float(src[known].min()),float(src[known].max())],'candidateRangeHKPD':[float(raw[known].min()),float(raw[known].max())],'verticesDifferingBeyondRounding':int((error>.006).sum()),'maximumDifferenceMetres':float(error.max())})
    points=[]
    for f in np.linspace(.1,.9,11):
        x=-4634.028+f*(784.218);z=-4573.747+f*(649.102);points.append({'world':[x,z],'mappedWater':water.covers(Point(x,z)),'coarseRenderedHKPD':height(coarse,x,z),'candidateBeforeWaterCutHKPD':height(patch,x,z),'afterSourceMappedWaterCutHKPD':-4 if water.covers(Point(x,z)) else height(patch,x,z)})
    order=np.argsort(abs(raw[bad]-src[bad]))[-10:][::-1];coords=np.argwhere(bad);worst=[]
    for i in order:
        r,c=coords[i];worst.append({'world':[float(xx[r,c]),float(zz[r,c])],'sourceHKPD':float(src[r,c]),'candidateRawHKPD':float(raw[r,c])})
    report={'status':'audit-complete','sourceGrids':sources,'completeMappedPortLand':{'areaM2':land.area,'gridNodes':int(mask.sum()),'sourceCoveredNodes':int(valid.sum()),'missingSourceNodes':int((mask&~np.isfinite(src)).sum()),'verticesDifferingBeyondRounding':int(bad.sum()),'worstDifferences':worst},'foundations':foundations,'channelSamples':points,'interpretation':'Mapped water resolves the inherited elevated channel surface. Full port-land comparisons expose any original mosaic archival-mask/edge blend discrepancy before publication; differences are not silently treated as surveyed repairs.','livePublished':False}
    report['portLandHeightReviewPending']=bool(bad.any())
    (ROOT/'docs/astra-city/stonecutters/terrain-source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='sourceGrids'},indent=2));return report
if __name__=='__main__':audit()
