"""Final exact patch/model screen; retain native minor discrepancies explicitly."""
import collections,math,shutil
import numpy as np
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.strtree import STRtree
from run import HERE,ROOT,DOC,load,dump,sha
from placement import fine,grid_triangles,upper_envelope,surface_contacts,projected,source_piece_audit,plane_values,polygons,clipped_plane
from bake_model_geometry import bake

def main():
 parentPath=ROOT/'3d-viewer/city/data/terrain-mui-wo.json';parent=load(parentPath);sampler=fine.DemSampler(parent,rendered=True);bundle=load(HERE/'terrain-refinements.json');assert sha(parentPath.read_bytes())==bundle['parentSha256'];children=[]
 for p in bundle['patches']:
  g=p['meta']['georef'];x=g['bE']-834500;z=816500-g['bN'];children.append((box(x,z,x+p['w']-1,z+p['h']-1),fine.DemSampler(p,rendered=True),p))
 def height(x,z):
  from shapely.geometry import Point
  for rect,s,_ in children:
   if rect.covers(Point(x,z)):return s.ground(x,z)
  return sampler.ground(x,z)
 def triangles(area):
  t=grid_triangles(sampler,area);keep=[]
  from shapely.geometry import Point
  for tri in t:
   centre=tri[:,[0,2]].mean(axis=0)
   if not any(rect.contains(Point(centre)) for rect,_,_ in children):keep.append(tri)
  for rect,s,_ in children:
   if rect.intersects(area):keep.extend(grid_triangles(s,rect.intersection(area)))
  return np.asarray(keep)
 catalogue=load(HERE/'compact/catalogue.json');entries={e['uid']:e for e in catalogue['models']};evidence={e['uid']:e for e in load(DOC/'compact-assets.json')['assets']};prior={r['uid']:r for r in load(DOC/'placement-audit.json')['rows']};package=load(ROOT/'3d-viewer/city/data/mui-wo-buildings.json');tileids={b['tile'] for b in package['buildings']};live={b['uid']:b for t in tileids for b in load(ROOT/'3d-viewer/city/data/tiles'/(t+'.json'))['buildings']};poly={u:Polygon(b['rings'][0],b['rings'][1:]) for u,b in live.items()};rows=[];safe=[];held=[]
 def envelope(uid):
  e=evidence[uid];path=ROOT/e['sourceEntry'];folder=path.parents[2];m=load(folder/'manifest.json');s=next(s for s in m['models'] if s['id']==entries[uid]['modelId']);pos=np.asarray(bake(s,folder)['position']).reshape(-1,3);faces=upper_envelope(pos.reshape(-1,3,3));roofs=[(t,p) for t,p in faces if abs(np.cross(t[1]-t[0],t[2]-t[0])[1])/np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))>=.25]
  return pos,roofs,unary_union([p for _,p in faces])
 for uid,e in entries.items():
  b=live[uid];pos,roofs,hull=envelope(uid);area=poly[uid].union(hull);tt=triangles(area);contact=surface_contacts(roofs,tt);valid,shapes=projected(tt);metrics,_,_=source_piece_audit(poly[uid],e['worldBounds'][1][1],(valid,STRtree(shapes)))
  bottom=e['worldBounds'][0][1];baseVertices=np.unique(pos[pos[:,1]<=bottom+.1],axis=0);baseClearance=[v[1]-height(v[0],v[2]) for v in baseVertices];grounded=bottom<=metrics['maximum']+.5 or min(baseClearance)<=.5
  foundation=b.get('foundationBase');foundationTop=min(b['base'],bottom);foundationGap=bottom-foundationTop if foundation is not None else None
  foundationSupports=foundation is not None and foundationGap<=.5 and foundation<=metrics['maximum']+.1
  podiums=[]
  for other,p in poly.items():
   if other==uid or live[other].get('structureType')!='Podium':continue
   fraction=p.intersection(poly[uid]).area/max(poly[uid].area,1e-9)
   if fraction<.95:continue
   model=entries.get(other);top=model['worldBounds'][1][1] if model else live[other].get('modelGeometry',{}).get('worldBounds',[[0,0,0],[0,live[other]['base']+live[other]['height'],0]])[1][1]
   support=[];levels=[]
   if other in entries:
    _,supportRoofs,_=envelope(other)
    for tri,roofArea in supportRoofs:
     for piece in polygons(roofArea.intersection(poly[uid])):
      coords=list(piece.exterior.coords)[:-1];heights=plane_values(tri,coords);levels.extend(float(v) for v in heights)
      # Quantify the actual podium deck under this tower, not a parapet's maximum.
      triPoly=Polygon(tri[:,[0,2]]);tc=list(triPoly.exterior.coords)[:-1];delta=plane_values(tri,tc)-bottom
      lower=clipped_plane(triPoly,delta,-.75);upper=clipped_plane(triPoly,-delta,-.75);support.append(piece.intersection(lower).intersection(upper))
    supportFraction=unary_union(support).area/max(poly[uid].area,1e-9)
   else:supportFraction=fraction if abs(top-bottom)<=.75 else 0
   if supportFraction>=.95:podiums.append({'uid':other,'footprintCoverage':fraction,'sourceRoofSupportCoverage':supportFraction,'sourceRoofMinimumUnderTower':min(levels) if levels else top,'sourceRoofMaximumUnderTower':max(levels) if levels else top,'sourceModelTop':top,'towerModelBottom':bottom,'dependsOnNewModel':other in entries,'fallbackPodiumTop':live[other]['base']+live[other]['height'],'fallbackVerticalDifference':bottom-(live[other]['base']+live[other]['height'])})
  floating=not grounded and not foundationSupports and not podiums
  # Minor local native/5m roof-edge discrepancies stay visible in the ledger.
  minor=contact['maximumTerrainMinusRoof'] is not None and contact['maximumTerrainMinusRoof']<=.5 and contact['terrainAboveRoofArea']<=1 and contact['terrainAboveRoofArea']/max(contact['topEnvelopeArea'],1e-9)<=.01
  roofClear=contact['terrainAboveRoofArea']<1e-5
  reasons=[]
  if not roofClear and not minor:reasons.append('material-roof-terrain-conflict')
  if floating:reasons.append('unsupported-native-elevated-base')
  if contact['coveredArea']<contact['topEnvelopeArea']-.01:reasons.append('terrain-coverage-gap')
  record={'uid':uid,'modelId':e['modelId'],'accepted':not reasons,'heldReasons':reasons,'roof':contact,'previousRoof':prior[uid]['surface'],'footprintTerrain':metrics,'baseVertices':len(baseVertices),'baseClearance':{'min':float(min(baseClearance)),'max':float(max(baseClearance))},'nativeMinimumBase':bottom,'grounded':bool(grounded),'existingIllustrativeFoundation':{'base':foundation,'top':foundationTop,'gapToNativeModel':foundationGap,'supports':bool(foundationSupports)},'mappedPodiumSupports':podiums,'minorRoofEdgeContactRetained':not roofClear and minor,'nativeSourceChecks':prior[uid]['nativeSourceChecks']};rows.append(record)
  (safe if not reasons else held).append(uid)
 # Dependency check: a new tower cannot be released assuming a held detailed podium.
 for r in rows:
  if not r['accepted']:continue
  dependencies=[p['uid'] for p in r['mappedPodiumSupports'] if p['dependsOnNewModel']]
  if dependencies and all(u not in safe for u in dependencies):r['accepted']=False;r['heldReasons'].append('supporting-podium-not-approved');safe.remove(r['uid']);held.append(r['uid'])
 # Check every changed neighbourhood using current model/fallback roof and foundation.
 union=unary_union([r for r,_,_ in children]);neighbours=[];updates={b['uid']:b for b in load(HERE.parent/'mui-wo-final-review/building-estimate-updates.json')['buildings']};edgeChecks=0;maxEdgeError=0
 for rect,s,p in children:
  x0,z0,x1,z1=rect.bounds
  for x,z in [(x0+i*.5,z) for i in range(round((x1-x0)*2)+1) for z in (z0,z1)]+[(x,z0+i*.5) for i in range(round((z1-z0)*2)+1) for x in (x0,x1)]:
   error=abs(s.ground(x,z)-sampler.ground(x,z));assert error<1e-5;maxEdgeError=max(maxEdgeError,error);edgeChecks+=1
 for uid,p in poly.items():
  if not p.intersects(union):continue
  b=live[uid];before=sampler.extrema(p);tt=triangles(p);valid,shapes=projected(tt);top=b.get('modelGeometry',{}).get('worldBounds',[[0,0,0],[0,b['base']+b['height'],0]])[1][1];after,_,_=source_piece_audit(p,top,(valid,STRtree(shapes)));newBase=updates.get(uid,{}).get('base',b['base']);newTop=top if uid not in updates else newBase+b['height'];neighbours.append({'uid':uid,'before':before,'after':{'min':after['minimum'],'max':after['maximum']},'previousTop':top,'topAfterGuardedEstimateUpdate':newTop,'newWholeRoofConflict':newTop<after['minimum']-.1 and not top<before['min']-.1,'newPartialRoofConflict':newTop<after['maximum']-.1 and not top<before['max']-.1,'estimatedBaseUpdateRequired':uid in updates,'previousBase':b.get('modelGeometry',{}).get('worldBounds',[[0,b['base'],0]])[0][1],'baseAfterGuardedEstimateUpdate':b.get('modelGeometry',{}).get('worldBounds',[[0,newBase,0]])[0][1],'previousDiagnostic':b.get('terrainAudit')})
 for n in neighbours:
  n['newFloatingBaseFlag']=n['baseAfterGuardedEstimateUpdate']>n['after']['max']+.5 and not n['previousBase']>n['before']['max']+.5
  n['proposedDiagnostic']={'roofWhollyBelowTerrain':n['topAfterGuardedEstimateUpdate']<n['after']['min']-.1,'roofPartlyBelowTerrain':n['topAfterGuardedEstimateUpdate']<n['after']['max']-.1,'baseWhollyAboveTerrain':n['baseAfterGuardedEstimateUpdate']>n['after']['max']+.5}
 diagnostics={'stagedOnly':True,'parentSha256':bundle['parentSha256'],'refinementSha256':sha((HERE/'terrain-refinements.json').read_bytes()),'byBuildingUid':{n['uid']:n['proposedDiagnostic'] for n in neighbours if n['previousDiagnostic']!=n['proposedDiagnostic']},'policy':'Derived flags for only these three child-patch neighbourhoods, evaluated with existing source geometries and the two guarded estimate updates. No source attribute changes.'}
 dump(HERE/'diagnostic-updates.json',diagnostics)
 catalogue['models']=[{**entries[u],'placementScreened':True,'placementReviewed':False} for u in safe];catalogue['counts']={'packedModels':len(safe),'catalogueModels':len(safe),'compressedBytes':sum(entries[u]['bytes'] for u in safe),'packedTriangles':sum(entries[u]['triangles'] for u in safe),'heldModels':len(held)};catalogue['loadingPolicy']='Placement-screened subset; requires the companion source terrain patches and existing guarded estimated-base updates. Preserve fallback until loaded. Browser integration acceptance remains pending.'
 out=HERE/'publication';(out/'models').mkdir(parents=True,exist_ok=True)
 for u in safe:shutil.copyfile(HERE/'compact'/entries[u]['asset'],out/entries[u]['asset'])
 dump(out/'catalogue.json',catalogue)
 report={'stagedOnly':True,'parentSha256':bundle['parentSha256'],'terrainRefinementsSha256':sha((HERE/'terrain-refinements.json').read_bytes()),'catalogueSha256':sha((out/'catalogue.json').read_bytes()),'models':len(entries),'acceptedModels':len(safe),'heldModels':len(held),'acceptedUids':safe,'heldUids':held,'rows':rows,'neighbours':neighbours,'seamChecks':edgeChecks,'maximumBoundaryError':maxEdgeError,'newFloatingNeighbourFlags':[n['uid'] for n in neighbours if n['newFloatingBaseFlag']],'diagnosticUpdates':len(diagnostics['byBuildingUid']),'newWholeNeighbourConflicts':[r['uid'] for r in neighbours if r['newWholeRoofConflict']],'newPartialNeighbourConflicts':[r['uid'] for r in neighbours if r['newPartialRoofConflict']],'criteria':'Exact visible roofing planes inclining up to75.5degrees, all model vertices and full footprints measured. Minor roof-edge contacts retained only if <=0.5m penetration, <=1m2 area and <=1percent roofing area; source discrepancy stays explicit. Grounding tolerance0.5m; existing illustrative foundation support or >=95percent mapped podium coverage within0.75m native vertical join accepted. Unsupported raised native forms held, never moved. Source identity match thresholds unchanged.'};dump(DOC/'publication-screen.json',report);print({k:v for k,v in report.items() if k not in ('rows','neighbours','acceptedUids','heldUids')});print('held',[(r['uid'],r['heldReasons']) for r in rows if not r['accepted']])
if __name__=='__main__':main()
