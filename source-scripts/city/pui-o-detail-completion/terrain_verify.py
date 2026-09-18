"""Exact footprint and seam audit for staged Pui O terrain and all four models."""
from terrain import *
def main():
 baseline=ROOT/'3d-viewer/city/data/terrain-pui-o.json';parent=load(baseline);old=fine.DemSampler(parent,rendered=True);bundle=load(HERE/'terrain-refinements.json');children=[];seams=0;maxerror=0
 for p in bundle['patches']:
  g=p['meta']['georef'];x0=g['bE']-834500;z0=816500-g['bN'];x1=x0+p['w']-1;z1=z0+p['h']-1;rect=box(x0,z0,x1,z1);sampler=fine.DemSampler(p,rendered=True);children.append((rect,sampler))
  for x,z in [(x0+i*.5,z) for i in range((p['w']-1)*2+1) for z in [z0,z1]]+[(x,z0+i*.5) for i in range((p['h']-1)*2+1) for x in [x0,x1]]:
   error=abs(sampler.ground(x,z)-old.ground(x,z));maxerror=max(maxerror,error);assert error<1e-5;seams+=1
 union=unary_union([rect for rect,_ in children]);assert sum(r.area for r,s in children)==union.area
 def extrema(poly):
  values=[]
  for rect,sampler in children:
   for piece in shared_audit.polygons(poly.intersection(rect)):values.append(sampler.extrema(piece))
  for piece in shared_audit.polygons(poly.difference(union)):values.append(old.extrema(piece))
  return {'min':min(r['min'] for r in values),'max':max(r['max'] for r in values)}
 catalogues=[load(BASE/'compact/catalogue.json'),load(HERE/'compact/catalogue.json')];models={m['uid']:m for c in catalogues for m in c['models']};new={m['uid'] for m in catalogues[1]['models']};manifest=load(ROOT/'3d-viewer/city/data/manifest.json');buildingrows=[];estimate_updates=[]
 # Read all live tiles intersecting the correction union, not just 919 selected forms.
 for path in (ROOT/'3d-viewer/city/data/tiles').glob('*.json'):
  # Small broad-phase tile bounds from 2km integer tile names.
  try:x,z=map(int,path.stem.split('_'))
  except ValueError:continue
  if not union.intersects(box(x*2000,z*2000,(x+1)*2000,(z+1)*2000)):continue
  for b in load(path)['buildings']:
   poly=Polygon(b['rings'][0],b['rings'][1:])
   if not union.intersects(poly) and b['uid'] not in new:continue
   before=old.extrema(poly);after=extrema(poly);model=models.get(b['uid']) or b.get('modelGeometry');bounds=model.get('worldBounds') if model else None;top=bounds[1][1] if bounds else b['base']+b['height'];bottom=bounds[0][1] if bounds else b['base'];previous_top=(b.get('modelGeometry') or {}).get('worldBounds',[[0,b['base']],[0,b['base']+b['height']]])[1][1]
   before_flags={'roofWhollyBelowTerrain':top<before['min']-.1,'roofPartlyBelowTerrain':top<before['max']-.1,'baseWhollyAboveTerrain':bottom>before['max']+.5};after_flags={'roofWhollyBelowTerrain':top<after['min']-.1,'roofPartlyBelowTerrain':top<after['max']-.1,'baseWhollyAboveTerrain':bottom>after['max']+.5}
   terrain_only_flags=dict(after_flags);derived_base=None
   if after_flags['baseWhollyAboveTerrain'] and not before_flags['baseWhollyAboveTerrain']:
    assert b['uid']=='landsd/182182:0' and not model and b.get('baseHeightHKPD') is None and b.get('topHeightHKPD') is None and b['baseSource']=='terrain-estimated' and b['heightSource']=='estimated'
    derived_base=after['min'];new_top=derived_base+b['height'];after_flags={'roofWhollyBelowTerrain':new_top<after['min']-.1,'roofPartlyBelowTerrain':new_top<after['max']-.1,'baseWhollyAboveTerrain':derived_base>after['max']+.5}
    estimate_updates.append({'uid':b['uid'],'objectId':b['objectId'],'buildingCSUID':b['buildingCSUID'],'tile':path.stem,'previousBase':b['base'],'base':derived_base,'height':b['height'],'baseSource':b['baseSource'],'heightSource':b['heightSource'],'sourceBaseHeightHKPD':None,'sourceTopHeightHKPD':None,'reason':'Update only an existing terrain-estimated base to the corrected ground minimum. Preserve null official elevations, original footprint, identity and3m estimated height.'})
   buildingrows.append({'terrainOnlyFlags':terrain_only_flags,'dependentEstimatedBase':derived_base,'uid':b['uid'],'tile':path.stem,'newModel':b['uid'] in new,'detailed':bool(model),'roof':top,'base':bottom,'recordedBase':b.get('baseHeightHKPD'),'recordedTop':b.get('topHeightHKPD'),'baseSource':b.get('baseSource'),'before':before,'after':after,'beforeFlags':before_flags,'afterFlags':after_flags,'sourceFieldsChanged':False})
 assert new<={r['uid'] for r in buildingrows},'Audit includes every new model footprint';regressions=[{'uid':r['uid'],'flags':[k for k in r['afterFlags'] if r['afterFlags'][k] and not r['beforeFlags'][k]]} for r in buildingrows];regressions=[r for r in regressions if r['flags']]
 save(HERE/'building-estimate-updates.json',{'stagedOnly':True,'parentSha256':bundle['parentSha256'],'refinementSha256':sha(HERE/'terrain-refinements.json'),'buildings':estimate_updates,'policy':'Apply only with these terrain patches, after guarding previous base, source nulls, unchanged estimated height and absent detailed model.'})
 save(HERE/'diagnostic-updates.json',{'stagedOnly':True,'byBuildingUid':{r['uid']:r['afterFlags'] for r in buildingrows},'policy':'Derived terrain flags after staged models, terrain and dependent estimate are applied together.'})
 report={'dependentEstimatedBaseUpdates':estimate_updates,'staged':True,'parentUnchanged':sha(baseline)==bundle['parentSha256'],'parentSha256':sha(baseline),'terrainRefinementsSha256':sha(HERE/'terrain-refinements.json'),'seamSamples':seams,'maxSeamErrorMetres':maxerror,'auditedForms':len(buildingrows),'allFourNewModelsClear':all(not r['afterFlags']['roofPartlyBelowTerrain'] for r in buildingrows if r['newModel']),'newRegressions':regressions,'rows':buildingrows,'scope':'Exact full-footprint/terrain triangle intersections, all four new source models and every live neighbouring building intersecting child grids. No source height changes.'};(DOC/'terrain-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2));assert report['parentUnchanged'];assert report['allFourNewModelsClear'];assert not regressions
if __name__=='__main__':main()
