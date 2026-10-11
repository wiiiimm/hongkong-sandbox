"""DRAFT whole original109339 exact3D edge census + existing494-pair context only."""
from pathlib import Path
from collections import defaultdict,Counter
import importlib.util,json,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest,connect
from exact_resumable_projected_inventory_v1_20261011 import decoded,encoded
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot
from exact_original_finite_triangle_contacts_20261010 import dimension,finite_intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from science_museum_original_open_sided_contact_topology_attribution_v1_20261011 import relative_interior
B=ROOT/'docs/astra-city/government-import';NAME='government-xl-mongkok-stadium240332-original14d-whole3d494-component-context-v1-20261011';DOC=B/NAME;LOCAL=HERE/'local'/NAME
PRIOR=B/'government-xl-mongkok-stadium240332-actual-native-union-authentic-core-inventory-v2-20261011';PLANES=B/'government-xl-mongkok-stadium240332-original494-overlap-plane-attribution-v1-20261011';FRINGE=B/'government-xl-mongkok-stadium240332-adjacent15c-complete-fringe-coverage-crosssheet-seams-v1-20261011';METHOD=B/(NAME+'-method')/'METHOD.md'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def verify(folder):
 r=read(folder/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
 return r

def main():
 assert not DOC.exists();receipts=[verify(p)for p in[PRIOR,PLANES,FRINGE]];sfile=HERE/'local'/PRIOR.name/'actual-union-authentic-whole-source-facets.json.gz';s=read(sfile);tin=next(ROOT/e['path']for e in s['sourceFiles']if e['path'].endswith('.gltf'));spec=importlib.util.spec_from_file_location('unchanged_original14d_decoder',HERE/'xl-second-pass.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.LOCAL=LOCAL;world=m.terrain_triangles(tin);assert world.shape==(109339,3,3)and np.isfinite(world).all()and digest(world.tobytes())==s['completeOriginalSheetSHA256'];parent=list(range(len(world)));edges=defaultdict(list);zero=[];dims=Counter();normals={}
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 def join(i,j):
  i,j=find(i),find(j)
  if i!=j:parent[max(i,j)]=min(i,j)
 for i,t in enumerate(world):
  f=rational_face(t);d=dimension(f);dims[d]+=1
  if d!=2:zero.append(dict(originalFacet=i,exactDimension=d));continue
  n=cross(sub(f[1],f[0]),sub(f[2],f[0]));normals[i]=('vertical'if n[1]==0 else'horizontal'if n[0]==n[2]==0 else'slope');v=[tuple(float(x)for x in p)for p in t]
  for a,b in zip(v,v[1:]+v[:1]):assert a!=b;edges[tuple(sorted((a,b)))].append((i,a,b))
  if i%10000==0:print(json.dumps(dict(wholeExact3DFacesThrough=i)),flush=True)
 for es in edges.values():
  for e in es[1:]:join(es[0][0],e[0])
 components=defaultdict(list)
 for i in normals:components[find(i)].append(i)
 bodies=sorted(components.values(),key=lambda fs:min(fs));labels={i:k for k,fs in enumerate(bodies)for i in fs};edge_rows=[]
 for (a,b),es in sorted(edges.items()):
  same=len(es)==2 and es[0][1:]==es[1][1:];edge_rows.append(dict(exactOriginalEndpoints=[a,b],allOriginalDirectedIncidences=[dict(originalFacet=i,start=u,end=v)for i,u,v in es],incidenceCount=len(es),twoSameDirectedIncidences=same))
 records=[];p=decoded(read(PLANES/'diagnostic.json.gz'));assert len(p['all494ExactOriginalOverlapPlaneAttributions'])==494
 for row in p['all494ExactOriginalOverlapPlaneAttributions']:
  i,j=row['originalSheetFacetIds'];a,b=rational_face(world[i]),rational_face(world[j]);points=sorted(finite_intersection_points(a,b));measure=contact_measure(points)if points else dict(dimension=-1);mid=tuple(sum(q[k]for q in points)/len(points)for k in range(3))if points else None;records.append(dict(originalFacets=[i,j],wholeExact3DEdgeComponents=[labels[i],labels[j]],sameWholeExact3DEdgeComponent=labels[i]==labels[j],exactFiniteIntersectionPoints=points,properBothRelativeInteriorCrossing=bool(points and measure['dimension']>0 and relative_interior(a,mid)and relative_interior(b,mid)),exactProjectedPlaneAttribution=row,**measure))
 involved=sorted({i for r in records for i in r['originalFacets']});body_rows=[dict(component=k,allOriginalFacetIds=fs,completeFaces=len(fs),boundsMin=world[fs].min((0,1)).tolist(),boundsMax=world[fs].max((0,1)).tolist(),exactPlaneOrientations=dict(Counter(normals[i]for i in fs)),all494ParticipatingOriginalFacetIds=sorted(set(fs)&set(involved)))for k,fs in enumerate(bodies)];DOC.mkdir();outputs=[]
 for kind,tri in [('whole-original109339',world),('selected-original14554',world[s['completeSelectedOriginalSheetFacetIds']])]:
  lo,hi=tri.min((0,1)),tri.max((0,1));fig=plt.figure(figsize=(12,9),dpi=200);ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(tri[:,:,[0,2,1]],facecolors='slategray',edgecolors='none',alpha=.14));ax.add_collection3d(Poly3DCollection(world[involved][:,:,[0,2,1]],facecolors='crimson',edgecolors='darkred',linewidths=.35,alpha=.7));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[2],hi[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect([hi[0]-lo[0],hi[2]-lo[2],hi[1]-lo[1]]);ax.view_init(elev=26,azim=-60);ax.set_xlabel('OriginalX');ax.set_ylabel('OriginalZ');ax.set_zlabel('OriginalY HKPD');ax.set_title(kind+' complete source / red318 exact overlap participants\nNo role/layer/height/function/current approval; occlusion possible');fig.tight_layout();out=DOC/(kind+'-3d--60.png');fig.savefig(out);plt.close(fig);outputs.append(dict(**ref(out),width=2400,height=1800,completeMeshSubmitted=True,completeAxes=True,occlusionNotCertified=True))
 code=['xl-second-pass.py','exact_original_shell_intersections_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_component_contacts_20261009.py','science_museum_original_open_sided_contact_topology_attribution_v1_20261011.py','test_exact_original_finite_triangle_contacts_20261010.py','test_science_museum_contact_relative_interior_v1_20261011.py'];refs=[ref(q)for q in[Path(__file__),METHOD,sfile]+[HERE/n for n in code]]+s['sourceFiles']+[ref(folder/n)for folder in[PRIOR,PLANES,FRINGE]for n in['result.json','diagnostic.json.gz']];assert all(ref(ROOT/e['path'])==e for e in refs);assert all(verify(folder)==r for folder,r in zip([PRIOR,PLANES,FRINGE],receipts));save(DOC/'diagnostic.json.gz',encoded(dict(uids=['landsd/240332:0','landsd/240527:0'],sourceOnly=True,currentAcceptance=False,terrainCandidateCreated=False,sourceGeometryChanges=0,liveTerrainChanges=0,completeOriginalFaces=109339,completeOriginalWorldSHA256=digest(world.tobytes()),allExactOriginalPrimitiveDimensions=dict(dims),allExactZeroOriginalPrimitives=zero,completeWholeNonzeroExactEdgeComponents=body_rows,allWholeExactOriginal3DEdgeIncidences=edge_rows,all494OriginalFinite3DPairRelationships=records,outputs=outputs,summary=dict(wholeOriginalFaces=109339,wholeNonzeroExactEdgeComponents=len(bodies),completeExactEdges=len(edges),sameDirectionTwoIncidenceEdges=sum(r['twoSameDirectedIncidences']for r in edge_rows),nonmanifoldEdges=sum(r['incidenceCount']>2 for r in edge_rows),all494Pairs=494,finiteContactPairs=sum(r['dimension']>=0 for r in records),properBothInteriorCrossingPairs=sum(r['properBothRelativeInteriorCrossing']for r in records),sameWholeEdgeComponentPairs=sum(r['sameWholeExact3DEdgeComponent']for r in records)),evidenceRefs=refs,qualification='Whole109339 exact nonzero shared WHOLE3D edge census and original winding/incidence context. Partial-edge/T-junction relationships are not added as component bridges; disconnected whole-edge components do not prove physical disconnection. Exact finite3D contact classification covers existing494 projected-positive pairs ONLY, not all whole-sheet surface pairs. Multilevel/retaining-wall/function/source-layer interpretation remains unresolved until actual views/source evidence; no 2.5D guard waiver, facet deletion, generated mesh, acceptance/root/native/F32/current support. All old494/6/4 and three crosssheet height gaps remain immutable.')));print(json.dumps(dict(wholeOriginalFaces=109339,wholeEdgeComponents=len(bodies),all494Pairs=494,currentAcceptance=False)))
if __name__=='__main__':main()
