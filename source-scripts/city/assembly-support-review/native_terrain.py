"""Compare audited native lower rims to retained native TIN; stage source-only 5m grids.
No current terrain/model writes. Grid nulls preserve missing source coverage.
"""
import json,hashlib,sys,time,collections,math
from pathlib import Path
import numpy as np
import shapely
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent;OUT=ROOT/'docs/astra-city/assembly-support-review'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry
from bake_model_geometry import decode
read=lambda p:json.loads(p.read_bytes())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def terrain_index(folder):
 manifest=read(folder/'manifest.json');spec=manifest['terrain'];path=folder/spec['url'];data=read(path);positions,count=model_geometry(data,lambda u:(path.parent/u).read_bytes());pieces=[];offset=0
 def visit(i):
  nonlocal offset
  node=data['nodes'][i]
  if 'mesh' in node:
   for primitive in data['meshes'][node['mesh']]['primitives']:
    assert primitive.get('mode',4)==4
    n=data['accessors'][primitive['attributes']['POSITION']]['count'];v=positions[offset:offset+n];offset+=n
    indices=decode(data,primitive['indices'],path.parent).reshape(-1) if 'indices' in primitive else np.arange(n)
    pieces.append(v[indices].reshape(-1,3,3))
  for child in node.get('children',[]):visit(child)
 for i in data['scenes'][data.get('scene',0)]['nodes']:visit(i)
 assert offset==len(positions)
 triangles=np.concatenate(pieces);assert len(triangles)==count;polys=shapely.polygons(triangles[:,:,[0,2]]);valid=shapely.area(polys)>1e-12
 return manifest,spec,triangles,valid,triangles[valid],shapely.STRtree(polys[valid])

def samples(points,usable,tree):
 pi,ti=tree.query(shapely.points(points),predicate='covered_by');abc=usable[ti];ab=abc[:,1,[0,2]]-abc[:,0,[0,2]];ac=abc[:,2,[0,2]]-abc[:,0,[0,2]];ap=points[pi]-abc[:,0,[0,2]]
 det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0];u=(ap[:,0]*ac[:,1]-ap[:,1]*ac[:,0])/det;v=(ab[:,0]*ap[:,1]-ab[:,1]*ap[:,0])/det
 ys=abc[:,0,1]+u*(abc[:,1,1]-abc[:,0,1])+v*(abc[:,2,1]-abc[:,0,1]);out=np.full(len(points),-np.inf);np.maximum.at(out,pi,ys);return out

def main():
 start=time.monotonic();r=read(OUT/'report.json');inputs=read(ROOT/'docs/astra-city/landmark-preflight/terrain-inputs.json');sources={s['manifest']:s for s in inputs['nativeSources']};coverage={p['uid']:p['nativeTerrainSourcesCoveringBounds'] for p in inputs['rows']};parts={p['uid']:p for p in r['rows']};by_source=collections.defaultdict(list)
 for p in r['rows']:
  for manifest in coverage.get(p['uid'],[]):by_source[manifest].append(p)
 accumulated={p['uid']:np.full(len(p['rim']),-np.inf) for p in r['rows']};used=[];grids=[];gridfolder=HERE/'source-grids';gridfolder.mkdir(exist_ok=True)
 for manifest,rows in sorted(by_source.items()):
  source=sources[manifest];mp=ROOT/manifest;assert sha(mp)==source['manifestSha256']
  for f in source['files']:assert sha(ROOT/f['path'])==f['sha256']
  m,s,t,valid,usable,tree=terrain_index(mp.parent)
  for p in rows:
   points=np.array([[s['position'][0],s['position'][2]] for s in p['rim']]);values=samples(points,usable,tree);accumulated[p['uid']]=np.maximum(accumulated[p['uid']],values)
  # Source-only grid for retained identities with actual source-vs-rendered disagreement.
  targets=[]
  for p in rows:
   if p['identityProposalGroups'] or p['knownHold']:continue
   vals=accumulated[p['uid']];delta=np.array([s['ground'] for s in p['rim']])-vals;gaps=np.array([s['position'][1] for s in p['rim']])-vals
   if np.any(np.isfinite(vals)&(np.abs(delta)>2)&(np.abs(gaps)<2)):targets.append(p)
  if targets:
   # Separate compact rectangles avoid a large tile-wide crop crossing unrelated areas.
   for p in targets:
    pts=np.array([s['position'] for s in p['rim']]);x0=math.floor((pts[:,0].min()-20)/5)*5;x1=math.ceil((pts[:,0].max()+20)/5)*5;z0=math.floor((pts[:,2].min()-20)/5)*5;z1=math.ceil((pts[:,2].max()+20)/5)*5
    xs=np.arange(x0,x1+1,5);zs=np.arange(z0,z1+1,5);xx,zz=np.meshgrid(xs,zs);values=samples(np.c_[xx.ravel(),zz.ravel()],usable,tree)
    path=gridfolder/(p['uid'].replace('landsd/','').replace(':','-')+'-'+source['sheet']+'.json')
    grid={'w':len(xs),'h':len(zs),'cell':5,'elev':[float(v) if np.isfinite(v) else None for v in values],'meta':{'georef':{'aE':5,'aN':-5,'bE':x0+834500,'bN':816500-z0,'W':len(xs),'H':len(zs)}},'targetUid':p['uid'],'source':source,'policy':'Source-only native triangle samples at 5m spacing, not surveyed accuracy. Null outside native triangle coverage. Not a runtime patch: parent alignment, water mask, transition, adjacent coverage and browser verification required.'}
    path.write_text(json.dumps(grid,separators=(',',':'))+'\n');grids.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'uid':p['uid'],'sheet':source['sheet'],'nodes':len(values),'covered':int(np.isfinite(values).sum())})
  used.append(source);print(json.dumps({'sheet':source['sheet'],'parts':len(rows),'grids':len(grids)}),flush=True)
 results=[]
 for uid,vals in accumulated.items():
  p=parts[uid];n=len(vals);covered=np.isfinite(vals);old=np.array([s['ground'] for s in p['rim']]);bottom=np.array([s['position'][1] for s in p['rim']]);gap=bottom-vals;improved=covered&(np.abs(gap)<=2)&(np.abs(bottom-old)>2)
  results.append({'uid':uid,'name':p['name'],'identityProposalGroups':p['identityProposalGroups'],'currentRimOutcome':p['rimOutcome'],'samples':n,'nativeCovered':int(covered.sum()),'nativeWithin2mOfRim':int((covered&(np.abs(gap)<=2)).sum()),'terrainDiscrepancyResolvedSamples':int(improved.sum()),'nativeStillBelowRim':int((covered&(gap>2)).sum()),'nativeAboveRim':int((covered&(gap< -2)).sum()),'nativeMinusRenderedRange':[float((vals-old)[covered].min()),float((vals-old)[covered].max())] if covered.any() else None,'samplesEvidence':[{'position':s['position'],'renderedGround':s['ground'],'nativeGround':float(v) if np.isfinite(v) else None} for s,v in zip(p['rim'],vals)],'publicationApproved':False})
 result={'issue':'HKS-214','inputReportSha256':sha(OUT/'report.json'),'parts':len(results),'nativeSourceSheets':len(used),'sources':used,'rows':results,'sourceGridProposals':grids,'seconds':time.monotonic()-start,'method':'Shared native glTF decoder; exact projected triangle containment and barycentric Y. Upper source triangle retained for overlaps. No extrapolation.','limits':['Source-only grid proposals cannot be placed in manifest directly.','Native TIN can differ in revision and still leave source building gaps.','No source model or runtime terrain modified; 1x HKPD preserved.']}
 (OUT/'native-terrain.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'parts':len(results),'sheets':len(used),'grids':len(grids),'resolvedSamples':sum(r['terrainDiscrepancyResolvedSamples'] for r in results),'seconds':result['seconds']}))
if __name__=='__main__':main()
