"""HKS-208 read-only native terrain and structural support context.
Fixed 1x EPSG:2326/HKPD geometry, existing terrain, no publication or DB edits.
"""
import hashlib,importlib.util,json,pathlib,sqlite3,sys
import numpy as np
from shapely.geometry import Polygon
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2]
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
sys.path.insert(0,str(R/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry
sys.path.insert(0,str(H.parent/'landmark-pass'))
from audit_existing import triangle_evidence
shared=module('architecture_terrain_helpers',H.parent/'pui-o-detail-completion/terrain.py')
def footprint(b):
 rings=json.loads(b['rings_json']);return Polygon(rings[0],rings[1:])
def main():
 catpath=H/'compact/catalogue.json';cat={m['uid']:m for m in read(catpath)['models']};proofs={r['uid']:r['proof'] for r in read(H/'report.json')['results'] if r.get('proof')};validationpath=H/'compact/validation.json';validation={r['uid']:r for r in read(validationpath)['results']}
 con=sqlite3.connect('file:'+str(H.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
 buildings={r['uid']:dict(r) for r in con.execute('select * from buildings where active=1 and x between -1500 and 850 and z between -400 and 1550')};con.close()
 terrainpath=R/'3d-viewer/city/data/terrain-central.json';terrain=read(terrainpath);assert not terrain.get('patches'),'Review nested sampling if Central terrain gains children';sampler=shared.fine.DemSampler(terrain,rendered=True)
 sourcecache={};vertexcache={}
 def native(uid):
  if uid not in vertexcache:
   folder=(R/proofs[uid]['sourceManifest']).parent;manifest=read(folder/'manifest.json');spec=next(m for m in manifest['models'] if m['id']==cat[uid]['modelId']);path=folder/spec['sourceEntry'];positions,_=model_geometry(read(path),lambda u:(path.parent/u).read_bytes());vertexcache[uid]=(path,positions)
  return vertexcache[uid]
 def terrain_source(uid):
  folder=(R/proofs[uid]['sourceManifest']).parent
  if folder not in sourcecache:
   manifest,spec,tri,valid,usable,tree=shared.terrain_index(folder);sourcecache[folder]=(manifest,spec,usable,tree)
  return sourcecache[folder]
 rows=[];skipped=[]
 for uid,m in cat.items():
  if uid not in buildings:
   skipped.append({'uid':uid,'label':m['label'],'reason':'Outside bounded Central terrain/source-context scope; separate placement review required.'});continue
  b=buildings[uid];poly=footprint(b);path,positions=native(uid);vertices=np.unique(positions,axis=0);ground=np.array([sampler.ground(x,z) for x,y,z in vertices]);delta=vertices[:,1]-ground;bottom=float(vertices[:,1].min());roof=float(vertices[:,1].max());near=vertices[:,1]<=bottom+.5;nearRoof=vertices[:,1]>=roof-.5
  sm,ss,usable,tree=terrain_source(uid);nativevalues,_=shared.shared_refine.source_samples(vertices[:,[0,2]],[{'usable':usable,'tree':tree}]);covered=np.isfinite(nativevalues);nativeDelta=vertices[:,1]-nativevalues;nativeAudit,_,_=shared.shared_audit.source_piece_audit(poly,roof,(usable,tree))
  neighbours=[]
  for nid,n in buildings.items():
   if nid==uid:continue
   npoly=footprint(n)
   if poly.distance(npoly)<.2:
    intersection=poly.intersection(npoly).area
    neighbours.append({'uid':nid,'name':n['name'],'structureType':n['structure_type'],'sourceBaseTop':[n['source_base'],n['source_top']],'renderBaseTop':[n['base'],n['base']+n['height']],'intersectionArea':round(intersection,4),'targetCoverageFraction':round(intersection/poly.area,6),'inCandidateBatch':nid in cat})
  row={'uid':uid,'label':m['label'],'sourceTile':m['sourceTile'],'sourceBaseTop':[b['source_base'],b['source_top']],'nativeBaseTop':[bottom,roof],'sourceFootprintArea':poly.area,'nativeRoofShape':{'heightQuantiles':np.quantile(vertices[:,1],[0,.5,.9,.95,.99,1]).tolist(),'verticesWithin05mOfTop':int(nearRoof.sum()),'topVertexBoundsXZ':[[float(vertices[nearRoof,0].min()),float(vertices[nearRoof,2].min())],[float(vertices[nearRoof,0].max()),float(vertices[nearRoof,2].max())]],'verticesAboveRecordedTop':int((vertices[:,1]>b['source_top']+.1).sum()) if b['source_top'] is not None else None},'screeningConcerns':validation.get(uid,{}).get('concerns',[]),'nativeVertexTerrain':{'uniqueVertices':len(vertices),'belowCurrentTerrainBy05m':int((delta<-.5).sum()),'belowNativeTerrainBy05m':int((covered&(nativeDelta<-.5)).sum()),'highestRoofVerticesBelowCurrentTerrain':int((nearRoof&(delta<-.1)).sum()),'highestRoofVerticesBelowNativeTerrain':int((nearRoof&covered&(nativeDelta<-.1)).sum()),'nearBottomVertices':int(near.sum()),'nearBottomCurrentGroundRange':[float(ground[near].min()),float(ground[near].max())],'nearBottomCurrentClearanceQuantiles':np.quantile(delta[near],[0,.25,.5,.75,1]).tolist(),'nativeTerrainCoveredVertices':int(covered.sum()),'currentMinusNativeTerrainQuantiles':np.quantile((ground-nativevalues)[covered],[0,.25,.5,.75,1]).tolist(),'nearBottomNativeClearanceQuantiles':np.quantile(nativeDelta[near&covered],[0,.25,.5,.75,1]).tolist() if (near&covered).any() else None},'nativeFootprintTerrain':nativeAudit,'nearbyParts':neighbours,'structuralSupport':[]}
  # Actual source triangles, not convex hulls, for overlapping lower components.
  for n in neighbours:
   nid=n['uid'];srcbase=b['source_base']
   if nid not in cat or n['targetCoverageFraction']<.1 or n['sourceBaseTop'][0] is None or n['sourceBaseTop'][0]>=bottom-1:continue
   pp,pv=native(nid);ev=triangle_evidence(pp,pv,poly,srcbase,bottom,1);diff=[min(abs(y-bottom) for y in ray['surfaceHeightsHKPD']) for ray in ev['rays'] if ray['surfaceHeightsHKPD']]
   row['structuralSupport'].append({'uid':nid,'label':cat[nid]['label'],'sourceBaseTop':n['sourceBaseTop'],'samples':ev['interiorSamples'],'samplesWithActualTriangle':len(diff),'samplesWithin05mOfModelBottom':sum(d<=.5 for d in diff),'samplesWithin1mOfModelBottom':sum(d<=1 for d in diff),'minimumSurfaceDifference':min(diff) if diff else None,'maximumSurfaceDifference':max(diff) if diff else None,'actualTriangleProjectedCoverage':ev['projectedTriangleCoverageFraction'],'surfaceHeightsRange':ev['maximumSurfaceHeightRangeHKPD'],'method':ev['method']})
  row['sourceModelProof']=proofs[uid]
  row['recommendation']='candidate-for-browser-approval'
  row['interpretation']='Native source geometry has no highest-roof burial; assess local base contact in browser before approval. Source base/top attributes and detailed mesh bounds describe different parts of the structure and are preserved separately.'
  if uid in ('landsd/170204:0','landsd/170207:0'):
   row['interpretation']='Elevated tower is supported by separate Lippo podium 234787, whose original indexed triangles cover essentially the entire tower footprint and include surfaces at tower-bottom elevation. Approve only as the three-part assembly; do not lower either tower to terrain.'
   row['requiredCompanionUids']=['landsd/234787:0']
  elif uid=='landsd/234787:0':row['interpretation']='Original podium includes structure from 6.079 m to 50.040 m, substantially more than its 5.8–16.5 m tabular range. Preserve this geometry to support the two native tower components.'
  elif uid=='landsd/223348:0':
   row['recommendation']='hold-unexplained-elevated-component';row['interpretation']='All lowest vertices are 7.12–7.46 m above current ground and 7.17–7.34 m above original TIN. No neighbouring building footprint intersects it. Native ten-triangle mesh starts at 56.027 m versus surveyed base 49.2 m and could be an upper component with missing support. Keep current full-height fallback until actual supporting geometry or visual/source evidence explains the gap. Do not lower this native roof piece.'
  elif uid=='landsd/330467:0':
   row['recommendation']='hold-rendered-terrain-refinement-required';row['interpretation']='Two lowest JC Cube vertices sit 3.30–4.24 m above current 5 m ground but only 0.31–0.50 m above original TIN. This is a local terrain sampling/support concern, not a reason to translate the model. Check the lowest corner for an exposed foundation gap.'
  elif uid in ('landsd/114964:0','landsd/105155:0','landsd/263599:0','landsd/16901:0','landsd/262589:0'):
   row['recommendation']='browser-foundation-check-required';row['interpretation']='Lowest source vertices closely follow the original TIN; coarser 5 m display samples bury some foundation vertices on the slope. Highest roof remains clear. Inspect ground-floor exposure and neighbouring retaining steps before acceptance; preserve native elevations.'
  elif uid in ('landsd/244346:0','landsd/251755:0'):
   row['interpretation']='Several lowest vertices are already below the original native terrain (JC Contemporary 1.04–2.57 m; Central Magistracy one extreme vertex about 7 m). Such source substructure is not evidence of a placement offset. Highest roof and main shell clear native/current terrain; review visible walls rather than reject by global minimum bounds.'
  elif uid in ('landsd/61477:0','landsd/181520:0','landsd/223783:0'):
   row['recommendation']='browser-foundation-check-required';row['interpretation']='Ground elevation changes across the hillside; lowest-vertex native terrain clearances show source contact at some corners and elevated/stepped edges elsewhere. Global bbox ground gaps are not uniform floating. Review entry terraces and downhill corners in browser without moving native elevations.'
  elif uid=='landsd/184076:0':
   row['interpretation']='CFA ground-contact vertices agree with source/current ground. 2,592 native vertices lie above tabular top 23 m; the 99th percentile height is 38.8 m; the 44.589 m maximum comprises 24 vertices over a narrow 0.307 × 0.312 m central feature. This is consistent with detailed dome and finial geometry rather than an isolated outlier, pending browser silhouette confirmation. Keep the native dome/finial height; no vertical scaling.'
  if uid in ('landsd/330467:0','landsd/114964:0'):
   row['recommendation']='hold-rendered-terrain-refinement-required'
   row['terrainFollowUp']={'candidate':'source-scripts/city/architecture-batch/taikwun-terrain-refinements.json','review':'source-scripts/city/architecture-batch/taikwun-terrain-review.json','disposition':'Staged experiment only; excluded from this bounded publication batch.','reason':'The 0.25 m source grid adds 58,081 vertices/about 116,000 triangles for two foundation corrections while JC Cube retains about 1 m clearance and E Hall retains a 0.61 m worst corner burial. Investigate a smaller retaining-edge representation; preserve 1x native building elevations and existing live terrain.'}
  rows.append(row)
 result={'issue':'HKS-208','stagedOnly':True,'verticalScale':1,'nativeElevationDatum':'HKPD','catalogueSha256':sha(catpath),'validationSha256':sha(validationpath),'currentTerrainSha256':sha(terrainpath),'models':len(rows),'catalogueModels':len(cat),'skipped':skipped,'holds':[r['uid'] for r in rows if r['recommendation'].startswith('hold-')],'browserFoundationChecks':[r['uid'] for r in rows if r['recommendation']=='browser-foundation-check-required'],'sourceTerrain':[{'tile':m['tile'],'revision':m['tileRevision'],'sourceHashes':s['sourceHashes']}for m,s,u,t in sourcecache.values()],'rows':rows,'limits':['Contextual source audit does not replace browser architecture acceptance.','Bottom geometry may be below grade or supported on separately modelled podiums; bare terrain gap alone does not justify rejecting or translating it.','Roof checks concern highest roof and sampled vertices; not every small roof face.','No source geometry, live terrain, database or model elevations changed.']}
 (H/'placement-context.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 for row in rows:print(json.dumps({k:row[k] for k in ['uid','label','sourceBaseTop','nativeBaseTop','screeningConcerns','nativeVertexTerrain','nativeFootprintTerrain','structuralSupport']}))
if __name__=='__main__':main()
