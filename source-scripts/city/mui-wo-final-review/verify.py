"""Bounded neighbour, seam and original-source preservation checks for staging."""
import json,math
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from audit import ROOT,HERE,DOC,OUT,load,sha,fine,polygons

def main():
 bundle=load(HERE/'terrain-refinements.json');parent=load(OUT/'terrain-mui-wo.json');baseline=fine.DemSampler(parent,rendered=True);g=parent['meta']['georef'];children=[];edgeChecks=0;maxEdgeError=0
 for patch in bundle['patches']:
  h=patch['meta']['georef'];x0=h['bE']-834500;z0=816500-h['bN'];x1=x0+patch['w']-1;z1=z0+patch['h']-1;rect=box(x0,z0,x1,z1);sample=fine.DemSampler(patch,rendered=True);children.append((rect,sample,patch))
  for x,z in [(x0+i*.5,z) for i in range((patch['w']-1)*2+1) for z in [z0,z1]]+[(x,z0+i*.5) for i in range((patch['h']-1)*2+1) for x in [x0,x1]]:
   err=abs(sample.ground(x,z)-baseline.ground(x,z));maxEdgeError=max(maxEdgeError,err);assert err<1e-6;edgeChecks+=1
  c0,r0,c1,r1=patch['coarseCells'];assert abs(x0-(g['bE']+c0*5-834500))<1e-9;assert abs(z1-(816500-g['bN']+r1*5))<1e-9
 for i,(a,_,_) in enumerate(children):
  for b,_,_ in children[i+1:]:assert a.intersection(b).area==0
 union=unary_union([p for p,s,g in children])
 def extrema(p):
  values=[]
  for child,sampler,patch in children:
   for q in polygons(child.intersection(p)):values.append(sampler.extrema(q))
  for q in polygons(p.difference(union)):values.append(baseline.extrema(q))
  return {'min':min(t['min'] for t in values),'max':max(t['max'] for t in values)}
 package=load(OUT/'mui-wo-buildings.json');ids={b['tile'] for b in package['buildings']};rows=[];estimateUpdates=[]
 for tid in sorted(ids):
  for b in load(OUT/'tiles'/(tid+'.json'))['buildings']:
   p=Polygon(b['rings'][0],b['rings'][1:])
   if not union.intersects(p):continue
   before=baseline.extrema(p);after=extrema(p);top=b['modelGeometry']['worldBounds'][1][1] if b.get('modelGeometry') else b['base']+b['height'];row={'uid':b['uid'],'modelId':b.get('modelGeometry',{}).get('modelId'),'highestRoof':top,'before':before,'after':after,'wholeBefore':top<before['min']-.1,'wholeAfter':top<after['min']-.1,'partialBefore':top<before['max']-.1,'partialAfter':top<after['max']-.1,'sourceBase':b.get('baseHeightHKPD'),'sourceTop':b.get('topHeightHKPD'),'buildingUnchanged':True};row['previousTerrainAudit']=b.get('terrainAudit');bottom=b['modelGeometry']['worldBounds'][0][1] if b.get('modelGeometry') else b['base'];row['proposedTerrainAudit']={'roofWhollyBelowTerrain':row['wholeAfter'],'roofPartlyBelowTerrain':row['partialAfter'],'baseWhollyAboveTerrain':bottom>after['max']+.5}
   row['renderBaseBefore']=bottom;row['baseClearanceBefore']=round(bottom-before['max'],6);row['baseClearanceAfterTerrainOnly']=round(bottom-after['max'],6)
   row['terrainOnlyAudit']=dict(row['proposedTerrainAudit'])
   if row['proposedTerrainAudit']['baseWhollyAboveTerrain'] and not row['previousTerrainAudit']['baseWhollyAboveTerrain']:
    # These two source outlines have no recorded vertical coordinates or source model.
    # Their derived bases inherited the same faulty outer source-union blend.
    assert b['uid'] in {'landsd/173217:0','landsd/173237:0'}, f'Unexpected new floating foundation: {b["uid"]}'
    assert not b.get('modelGeometry') and b.get('baseHeightHKPD') is None and b.get('topHeightHKPD') is None and b.get('baseSource')=='terrain-estimated' and b.get('heightSource')=='estimated'
    newBase=after['min'];newTop=newBase+b['height'];row['renderBaseAfterEstimateUpdate']=newBase;row['highestRoofAfterEstimateUpdate']=newTop
    row['proposedTerrainAudit']={'roofWhollyBelowTerrain':newTop<after['min']-.1,'roofPartlyBelowTerrain':newTop<after['max']-.1,'baseWhollyAboveTerrain':newBase>after['max']+.5}
    assert not any(row['proposedTerrainAudit'].values())
    estimateUpdates.append({'uid':b['uid'],'objectId':b['objectId'],'buildingCSUID':b['buildingCSUID'],'tile':b['tile'],'previousBase':b['base'],'base':newBase,'height':b['height'],'baseSource':b['baseSource'],'heightSource':b['heightSource'],'sourceBaseHeightHKPD':None,'sourceTopHeightHKPD':None,'reason':'Recompute only the existing estimated base from the corrected source-ground footprint minimum. Both official vertical fields remain null; original footprint/ID/fallback height unchanged.'})
   rows.append(row)
 newWhole=[r['uid'] for r in rows if r['wholeAfter'] and not r['wholeBefore']];newPartial=[r['uid'] for r in rows if r['partialAfter'] and not r['partialBefore']]
 report={'stagedOnly':True,'parentSha256':sha(OUT/'terrain-mui-wo.json'),'expectedParentSha256':bundle['parentSha256'],'parentUnchanged':sha(OUT/'terrain-mui-wo.json')==bundle['parentSha256'],'seamChecks':edgeChecks,'maximumBoundaryErrorMetres':maxEdgeError,'neighbourForms':len(rows),'newWholeConflicts':newWhole,'newPartialConflicts':newPartial,'rows':rows,'policy':'Exact old/new footprint intersections with parent and nested child triangles. Original buildings are read only. Bounds snap to parent 5 m cells; every half-metre boundary sample matches the old parent.'}
 updates={r['uid']:r['proposedTerrainAudit'] for r in rows if r['previousTerrainAudit']!=r['proposedTerrainAudit']};report['diagnosticUpdates']=len(updates);report['dependentEstimatedBaseUpdates']=estimateUpdates;report['newFloatingBasesBeforeEstimateUpdates']=[r['uid'] for r in rows if r['terrainOnlyAudit']['baseWhollyAboveTerrain'] and not r['previousTerrainAudit']['baseWhollyAboveTerrain']];report['newFloatingBasesAfterEstimateUpdates']=[r['uid'] for r in rows if r['proposedTerrainAudit']['baseWhollyAboveTerrain'] and not r['previousTerrainAudit']['baseWhollyAboveTerrain']]
 (HERE/'building-estimate-updates.json').write_text(json.dumps({'stagedOnly':True,'parentSha256':bundle['parentSha256'],'refinementSha256':sha(HERE/'terrain-refinements.json'),'buildings':estimateUpdates,'policy':'Apply with the staged terrain only after validating each UID, previous base, null recorded fields and lack of source model. Change derived base only; preserve every official field, fallback height and footprint.'},indent=2)+'\n')
 (HERE/'diagnostic-updates.json').write_text(json.dumps({'stagedOnly':True,'parentSha256':bundle['parentSha256'],'byBuildingUid':updates,'policy':'Derived terrainAudit flags only after nested terrain publication. Never alter source roofs, base fields or foundation geometry.'},indent=2)+'\n')
 assert report['parentUnchanged'];assert not newWhole;assert not newPartial;assert not report['newFloatingBasesAfterEstimateUpdates']
 (DOC/'neighbour-seam-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
