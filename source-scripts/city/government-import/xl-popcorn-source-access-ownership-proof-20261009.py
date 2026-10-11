"""Source-bound, independently reviewable PopCorn exterior-step proof; no acceptance waiver."""
import json,collections,numpy as np,shapely,pymupdf
from shapely.geometry import shape,mapping,LineString
from run import ROOT,HERE,read,save,digest
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection,LineCollection
BATCH='government-xl-popcorn-source-access-ownership-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH;G=ROOT/'docs/astra-city/government-import/government-xl-popcorn-station-collection-20261009';F=ROOT/'docs/astra-city/government-import/government-xl-source-authored-openings-20261009'
roles=read(G/'full-original-extra-role-diagnostics.json.gz');collection=read(G/'complete-original-popcorn-station-measures.json.gz');vec=read(DOC/'decoded-original-feature-geometries.json.gz');tri=np.load(HERE/'local/government-xl-source-authored-openings-20261009/raw-fbx/B447991877202063C0/full-world-triangles.npz')['triangles'];assert digest(tri.astype('<f8').tobytes())==roles['worldSourceTriangleSHA256'];v=np.stack([tri[:,:,0]-834500,tri[:,:,2],816500-tri[:,:,1]],axis=2)
target=shapely.union_all([shape({'type':'Polygon','coordinates':b['rings']}) for b in collection['groupForms']]);faces=shapely.polygons(v[:,:,[0,2]]);edges={};parent=np.arange(len(tri))
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=int(parent[i])
 return i
def join(a,b):parent[root(a)]=root(b)
for i,t in enumerate(tri):
 for k in range(3):
  key=tuple(sorted([tuple(t[k]),tuple(t[(k+1)%3])]))
  if key in edges:join(i,edges[key])
  else:edges[key]=i
labels=np.array([root(i) for i in range(len(tri))]);groups=collections.defaultdict(list)
for i,l in enumerate(labels):groups[int(l)].append(i)
step_lines=[]
for fi,f in enumerate(vec['rows']):
 if f['layer']=='8_CartoPedLine_1K' and f['properties']['_symbol']==8:
  g=shape(f['geometry']);step_lines += [(fi,j,a) for j,a in enumerate(g.geoms if hasattr(g,'geoms') else[g])]
rows=[];fig,axs=plt.subplots(2,2,figsize=(14,12))
for role in roles['rows']:
 ids=np.array(role['originalFaceIndices']);p=shape(role['originalProjectedGeometry']);matched=[(fi,j,a) for fi,j,a in step_lines if a.intersects(p)];ctx=[(fi,j,a) for fi,j,a in step_lines if a.distance(p)<1];lines=shapely.union_all([a for _,_,a in matched]);records=[]
 for lab in np.unique(labels[ids]):
  allids=groups[int(lab)];t=v[allids];projection=shapely.union_all(faces[allids]);records.append({'exactVertexEdgeConnectedComponent':int(lab),'totalOriginalFaceCount':len(allids),'allOriginalFaceIndices':allids,'farOriginalFaceIndices':ids[labels[ids]==lab].tolist(),'fullComponentBoundsXYZ':[t.min(axis=(0,1)).tolist(),t.max(axis=(0,1)).tolist()],'componentOverlapsRetainedTargetM2':projection.intersection(target).area,'componentDistanceToCurrentStepLinesM':float(projection.distance(lines)) if not projection.is_empty else None,'sourceAuthoredNode':'B447991877202063C0','qualification':'Exact complete original edge-connected topology. Components including body touch exact retained forms; small detached rail pieces remain parts of same untouched provider mesh node, not fabricated independent stair ownership.'})
 vertices=v[ids][:,:,[0,2]].reshape(-1,2);row={'roleIndex':role['component'],'everyFarOriginalFaceIndex':ids.tolist(),'rawFarFaceCount':len(ids),'originalProjectedGeometry':role['originalProjectedGeometry'],'matchedCurrentProviderSteps':[{'vectorFeatureIndex':fi,'partIndex':j,'geometry':mapping(a)} for fi,j,a in matched],'matchedStepLineCount':len(matched),'stepLineLengthM':sum(a.length for _,_,a in matched),'stepLineInsideSourceProjectionLengthM':sum(a.intersection(p).length for _,_,a in matched),'allFarVertexDistanceToMatchedStepLinesM':shapely.distance(shapely.points(vertices),lines).tolist(),'maximumFarVertexDistanceToMatchedStepLinesM':float(shapely.distance(shapely.points(vertices),lines).max()),'heightRangeHKPD':[float(v[ids,:,1].min()),float(v[ids,:,1].max())],'completeOriginalComponents':records,'foreignFormOverlapM2':collection['completeCollectionMeasures']['unrelatedExcessOverlapM2'],'semanticConclusion':'Positive exact-location original stair/tread function, source-authored node linkage and original attached-body/rail topology; reviewed complete ancillary-source ownership proposed, not automatic acceptance.'};rows.append(row)
 ax=axs[role['component'],0];ax.add_collection(PolyCollection(v[ids][:,:,[0,2]],facecolors='#e77166',edgecolors='#98352d',linewidths=.12,alpha=.6));ax.add_collection(LineCollection([np.array(a.coords) for _,_,a in ctx],colors='#156b38',linewidths=1.3));ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.set_title(f'Original stair {role["component"]}: all far faces red / current steps green')
 ax=axs[role['component'],1];t=v[ids];ax.add_collection(PolyCollection(t[:,:,[0,1]],facecolors='#e77166',edgecolors='#98352d',linewidths=.12,alpha=.6));ax.autoscale();ax.set_aspect('equal');ax.set_title('Every original far face: x / HKPD height')
fig.tight_layout();fig.savefig(DOC/'every-original-far-face-current-steps.png',dpi=180)
# Page transform comes solely from printed HK80 grid intersections, not fitting source geometry.
page=pymupdf.open(F/'primary/mtr-tseung-kwan-o-railway-protection-plan.pdf')[0];draw={d['seqno']:d for d in page.get_drawings()}
def ends(seq):
 items=[a for a in draw[seq]['items'] if a[0]=='l'];return np.array(items[0][1]),np.array(items[-1][2])
def intersection(seq1,seq2):
 a,b=ends(seq1);c,d=ends(seq2);mat=np.stack([b-a,-(d-c)],axis=1);u=np.linalg.solve(mat,c-a);return a+u[0]*(b-a)
origin=intersection(8007,8003);e100=intersection(8008,8003)-origin;nminus100=intersection(8007,8002)-origin;M=np.stack([e100/100,-nminus100/100],axis=1);tests=[{'lineSequence':seq,'easting':east,'pointOnN818800':intersection(seq,8003).tolist(),'gridPositionResidualPDFPoints':float(np.linalg.norm(intersection(seq,8003)-(origin+M@np.array([east-844700,0]))))} for seq,east in [(8006,844600),(8007,844700),(8008,844800),(8009,844900),(8010,845000)]]
pix=page.get_pixmap(matrix=pymupdf.Matrix(2,2),alpha=False);img=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n);fig,ax=plt.subplots(figsize=(16,12));ax.imshow(img,extent=[0,page.rect.width,page.rect.height,0])
for role in roles['rows']:
 ids=role['originalFaceIndices'];pdftri=(v[ids][:,:,[0,2]]*np.array([1,-1])+np.array([834500-844700,816500-818800]))@M.T+origin;ax.add_collection(PolyCollection(pdftri,facecolors='#fb3d44',edgecolors='#7b1114',linewidths=.1,alpha=.65))
ax.set_xlim(220,825);ax.set_ylim(500,120);fig.tight_layout();fig.savefig(DOC/'original-mtr-grid-overlay.png',dpi=180);save(DOC/'mtr-grid-registration.json',{'primaryPDF':str((F/'primary/mtr-tseung-kwan-o-railway-protection-plan.pdf').relative_to(ROOT)),'primaryPDFSHA256':digest((F/'primary/mtr-tseung-kwan-o-railway-protection-plan.pdf').read_bytes()),'basis':'Printed HK1980 grid E844700(seq8007),E844800(seq8008),N818800(seq8003),N818700(seq8002); independent gridlines validate. No mesh/pose fits. Railway protection boundary is NOT a property ownership boundary.','originWorldEN':[844700,818800],'originPDFPoints':origin.tolist(),'matrixWorldMetresToPDFPoints':M.tolist(),'independentGridChecks':tests})
save(DOC/'source-bound-ancillary-step-identity-proposal.json.gz',{'sourceProofs':collection['sourceProofs'],'allOriginalGeoRefCells':collection['originalCells'],'rawCompleteMeasures':collection['completeCollectionMeasures'],'rawStrictSpatialPass':False,'all311FarFacesPositivelyLocatedAtCurrentSteps':sum(r['rawFarFaceCount'] for r in rows)==311 and all(r['matchedStepLineCount']>10 for r in rows),'rows':rows,'sourceGeometryChanges':0,'sourcePoseChanges':0,'identityAccepted':False,'installationApproved':False,'physicalAndRuntimePass':False,'proposalOnly':True,'ownershipBasis':'Same original single provider FBX mesh root, exact source GeoRef and source SHA, current function from independent original government STP E lines, exact topology/foreign separation, independently grid-registered MTR mall/site plan. MTR plan railway boundary is not property boundary; role inference requires independent review.'});print({'roles':[{'index':r['roleIndex'],'faces':r['rawFarFaceCount'],'steps':r['matchedStepLineCount'],'connectedComponents':len(r['completeOriginalComponents']),'maxStepDistanceM':r['maximumFarVertexDistanceToMatchedStepLinesM']} for r in rows],'gridChecks':tests},flush=True)
