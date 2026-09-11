"""Prepare a bounded review packet without AI calls or acceptance changes."""
import importlib.util,json,html
from pathlib import Path
import shapely
from shapely.geometry import Polygon
spec=importlib.util.spec_from_file_location('xxl_second',Path(__file__).with_name('xxl-second-pass.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
uid='landsd/160070:0';row=next(r for r in s.read(s.DOC/'selection.json.gz')['rows'] if r['uid']==uid);diag=next(r for r in s.read(s.DOC/'diagnostics.json')['rows'] if r['uid']==uid);folder=s.DOC/'sol-review-proposal';folder.mkdir(exist_ok=True)
tri=s.glb_triangles(row);polys=shapely.polygons(tri[:,:,[0,2]]);projection=shapely.union_all(polys[shapely.area(polys)>1e-10]);b=row['source']['building'];foot=Polygon(b['rings'][0],b['rings'][1:]);x0,z0,x1,z1=projection.union(foot).bounds;pad=2

def svg_shape(shape,colour):
    paths=[]
    for p in (shape.geoms if hasattr(shape,'geoms') else [shape]):
        if not hasattr(p,'exterior'):continue
        d=' '.join('M '+' L '.join(f'{x-x0:.4f},{z-z0:.4f}' for x,z in ring.coords)+' Z' for ring in [p.exterior,*p.interiors]);paths.append(f'<path d="{d}" fill="{colour}" fill-opacity=".3" stroke="{colour}" stroke-width=".08" fill-rule="evenodd"/>')
    return ''.join(paths)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="1000" viewBox="{-pad} {-pad} {x1-x0+pad*2} {z1-z0+pad*2}"><title>Exact source projection blue; current government footprint red. Metres.</title><rect x="{-pad}" y="{-pad}" width="{x1-x0+pad*2}" height="{z1-z0+pad*2}" fill="white"/>'+svg_shape(projection,'#2166ac')+svg_shape(foot,'#d7191c')+'</svg>'
(folder/'lui-seng-chun-projection.svg').write_text(svg)
packet={'task':'Determine whether this unchanged government mesh has a defensible one-to-one or assembly identity for its current source form. Return evidence, unresolved questions and a reusable acceptance rule if supported. Do not alter geometry, terrain, installed states, manifests or Neon. Do not infer approval merely from name or triangle count.','model':'gpt-5.6-sol','status':'proposed-not-started','aiCalls':0,'uid':uid,'name':b.get('name'),'modelId':row['modelId'],'sourceSHA256':row['sourceSHA256'],'nativeSource':{'cacheKey':row['native']['cacheKey'],'resultSHA256':row['native']['resultSha'],'sheet':row['native']['sheet']},'sourceRecord':b,'diagnostics':diag,'reviewInputs':{'selection':s.rel(s.DOC/'selection.json.gz'),'nativeAsset':s.rel(s.LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')),'projection':s.rel(folder/'lui-seng-chun-projection.svg')},'scope':'One source identity/component review only, no remodelling. Existing numeric checks remain mandatory. If evidence is insufficient, return unresolved and identify missing evidence.','tokenEstimate':{'range':[5000,15000],'unit':'total input and output including reasoning when metered','basis':'One compact source/evidence packet and one overlay, bounded written assessment. Planning estimate, not measured use or a guaranteed hard cap; additional research is excluded.'}}
s.save(folder/'packet.json',packet)
print(json.dumps({'packet':s.rel(folder/'packet.json'),'textBytes':(folder/'packet.json').stat().st_size,'svgBytes':(folder/'lui-seng-chun-projection.svg').stat().st_size,'aiCalls':0}))
