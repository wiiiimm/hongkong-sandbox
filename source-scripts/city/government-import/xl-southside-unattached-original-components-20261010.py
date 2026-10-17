"""Complete original detached-part inventory; distances do not grant support."""
import importlib.util,numpy as np
from run import ROOT,HERE,read,save,digest
BATCH='government-xl-southside-unattached-original-components-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent/'government-xl-southside-station-original-pair-exact-slab-terrain-20261010'
GRAPH=DOC.parent/'government-xl-southside-station-original-pair-source-anchor-paths-20261010/diagnostic.json.gz'
def main():
 assert not DOC.exists();inp=read(BASE/'complete-original-podium-footing-inputs.json.gz');graph=read(GRAPH);ground=read(BASE/'complete-original-podium-ground-interfaces.json.gz');parts={};complete=[];owners=[]
 for row in inp['rows']:
  for p in row['parts']:
   tri=np.asarray(p['position'],float).reshape(-1,3)[np.asarray(p['index'],int).reshape(-1,3)];parts[(row['uid'],p['component'])]=(p,tri);complete.extend(tri);owners.extend([(row['uid'],p['component'])]*len(tri))
 complete=np.asarray(complete,float);spec=importlib.util.spec_from_file_location('southside_original_surface_distance',HERE/'xl-popcorn-original-panel-distance-20261009.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);rows=[]
 for gid in graph['componentsWithoutPositiveOriginalGroundPath']:
  p=graph['completeOriginalComponents'][gid];part,tri=parts[(p['uid'],p['originalComponent'])];mask=np.asarray([o!=(p['uid'],p['originalComponent']) for o in owners]);other=complete[mask];other_ids=np.flatnonzero(mask);vertices=np.unique(tri.reshape(-1,3),axis=0);near=[]
  for vertex in vertices:
   dist,points=helper.closest(vertex,other);j=int(np.argmin(dist));index=int(other_ids[j]);near.append({'originalVertex':vertex.tolist(),'nearestOriginalGlobalFace':index,'nearestOriginalOwner':owners[index],'nearestOriginalPoint':points[j].tolist(),'distanceM':float(dist[j])})
  normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);ratios=np.divide(normal[:,1],length,out=np.zeros(len(length)),where=length>0);g=next(x for x in ground['rows'] if x['uid']==p['uid']);gpart=next(x for x in g['parts'] if x['component']==p['originalComponent'])
  rows.append({'globalComponent':gid,'uid':p['uid'],'originalComponent':p['originalComponent'],'allOriginalFaceIds':p['originalFaceIds'],'wholeOriginalTriangles':tri.tolist(),'worldBounds':[tri.min((0,1)).tolist(),tri.max((0,1)).tolist()],'wholeOriginalVerticesNearestOtherSource':near,'minimumVertexDistanceM':min(x['distanceM'] for x in near),'maximumVertexDistanceM':max(x['distanceM'] for x in near),'normalYRatioRange':[float(ratios.min()),float(ratios.max())],'sourceGroundInterface':gpart,'exactPositiveGroundPathAbsent':True,'supportAccepted':False})
 save(DOC/'diagnostic.json.gz',{'completePairFaces':len(complete),'completePairComponents':len(parts),'unattachedComponents':rows,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [GRAPH,BASE/'complete-original-podium-footing-inputs.json.gz',BASE/'complete-original-podium-ground-interfaces.json.gz',HERE/'xl-popcorn-original-panel-distance-20261009.py']},'physicalAccepted':False,'qualification':'Every unresolved original part and every original face retained. Closest-surface values are floating diagnostic witnesses, not contact, whole-facet containment, structural or decorative role credit. All exact graph negatives and independent current support/collision/runtime gates remain.'});print([{'uid':x['uid'],'component':x['originalComponent'],'faces':len(x['allOriginalFaceIds']),'y': [x['worldBounds'][0][1],x['worldBounds'][1][1]],'maxVertexGapM':x['maximumVertexDistanceM']} for x in rows],flush=True)
if __name__=='__main__':main()
