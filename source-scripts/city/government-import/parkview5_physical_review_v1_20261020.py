"""Exact original lower-wall interpretation; raw canonical failures preserved."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview5-physical-review-v1-20261020';DOC=BASE/BATCH;UID='landsd/256113:0';POD='landsd/254491:0'
def folder(n):return BASE/('government-xl-'+n+'-20261020')
assert not DOC.exists();refs=[Path(__file__)];pins={}
names=['parkview5-current-runtime-v1','parkview5-finite-path-verification-v2','parkview-low-contact-paths-v1','star-parkview-four-mode-foundations-v1','parkview-three-four-world-contacts-v2','parkview5-buried-face-context-v1','parkview-three-support-views-v1']
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for n in names:
  d=folder(n);r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);pins[n]={e['path']:e['sha256']for e in r['evidenceRefs']};refs.append(d/'result.json')
def consume(n,file):
 p=folder(n)/file;assert digest(p.read_bytes())==pins[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
current=consume('parkview5-current-runtime-v1','current-binding.json');assert all(r['sameCompleteWorld']and r['sameCompleteDrawnGround']for r in current['rows'])
raw=consume('parkview-three-four-world-contacts-v2','contacts.json.gz')['rows'];inputs=consume('parkview-three-four-world-contacts-v2','input.json.gz')['rows'];face=consume('parkview5-buried-face-context-v1','face.json');assert face['faceId']==5177
runtime=HERE/'local/government-xl-parkview5-current-runtime-v1-20261020/runtime-geometry.json.gz';assert digest(runtime.read_bytes())==pins['parkview5-current-runtime-v1'][str(runtime.relative_to(ROOT))];refs.append(runtime);ground=np.asarray(next(r for r in read(runtime)['rows']if r['uid']==UID)['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
# All face vertices project inside the SAME exact finite ground triangle. Its
# affine height and the source facet's affine position then bound the full face.
groundId=183;g=[[F(float(v))for v in p]for p in ground[groundId]];a,b,c=g;dx1,dz1=b[0]-a[0],b[2]-a[2];dx2,dz2=c[0]-a[0],c[2]-a[2];det=dx1*dz2-dz1*dx2;assert det
accounts=[];clearance=[]
for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
 f=consume('star-parkview-four-mode-foundations-v1','256113:0-'+mode+'.json');assert not f['strictFoundationAccepted']and f['foundation']['fullyBuriedTriangles']==1 and f['foundation']['fullyBuriedUpwardTriangles']==0
 low=next(r for r in consume('parkview-low-contact-paths-v1',mode+'-verified.json.gz')['rows']if r['uid']==UID);finite=consume('parkview5-finite-path-verification-v2',mode+'.json');assert len(finite['rows'])==13 and all(r['finitePathVerified']and r['withinEndpointHeight']and r['allSteepWallFaces']and r['maximumResidualM']==0 for r in finite['rows'])
 assert sum(r['terminalContactOnSourceBoundary']for r in finite['rows'])==12
 failed={tuple(r['position'])for r in low['details']if not r['verified']};fixed={tuple(r['target'])for r in finite['rows']if isinstance(r['target'],list)};assert failed==fixed and len(failed)==12
 assert low['boundedPaths']==48 and low['unresolved']==12
 r=next(r for r in raw if r['uid']==UID and r['mode']==mode);assert r['samples']==149 and r['canonicalContacts']==89 and not r['rawInterface']['passed'];assert 89+48+12==149
 assert f['worldSHA256']==low['worldSHA256']==finite['sourceWorldSHA256']==r['sourceWorldSHA256']
 row=next(r for r in inputs if r['uid']==UID and r['mode']==mode);geo=row['source'];t=np.asarray(geo['position'],dtype='<f8').reshape(-1,3)[np.asarray(geo['index']).reshape(-1,3)];assert digest(t.tobytes())==f['worldSHA256'];tri=t[5177];n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);assert n[1]==0 and np.linalg.norm(n)>0
 gaps=[];bary=[]
 for p in tri:
  x,y,z=map(lambda v:F(float(v)),p);dx,dz=x-a[0],z-a[2];u=(dx*dz2-dz*dx2)/det;v=(dx1*dz-dz1*dx)/det;assert u>=0 and v>=0 and u+v<=1;gap=y-(a[1]+u*(b[1]-a[1])+v*(c[1]-a[1]));assert gap>0;gaps.append(gap);bary.append([str(1-u-v),str(u),str(v)])
 buried=next(r for r in finite['rows']if r['target']==5177);assert buried['faces']==[5177,4206]and not buried['terminalContactOnSourceBoundary']
 clearance.append(dict(mode=mode,faceId=5177,groundFaceId=groundId,exactGroundBarycentricWeights=bary,exactVertexClearancesM=[str(v)for v in gaps],minimumWholeFaceGroundClearanceM=float(min(gaps)),proof='Convex affine interpolation over a single finite projected ground triangle; all exact barycentric weights nonnegative.'))
 accounts.append(dict(mode=mode,sourceWorldSHA256=f['worldSHA256'],supportWorldSHA256=r['supportWorldSHA256'],samples=149,canonicalStrictContacts=89,priorBoundedWallPaths=48,finiteBoundaryWallPaths=12,unresolved=0,rawBuriedSideFaces=1,rawBuriedUpwardFaces=0,buriedSideFaceClearOfActualGround=True))
images=[]
for name,file in [('parkview-three-support-views-v1','256113:0-junctions.png'),('parkview5-buried-face-context-v1','face-context.png')]:
 p=folder(name)/file;assert digest(p.read_bytes())==pins[name][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
save(DOC/'ROOT-PHYSICAL-REVIEW.json',dict(uid=UID,sourceSHA256=face['sourceSHA256'],supportUid=POD,supportSHA256=face['supportSHA256'],sourceSpecificPhysicalInterpretationAccepted=True,rawCanonicalInterfacePassed=False,rawStrictFoundationPassed=False,rawFailuresPreserved=True,sampleAccounts=accounts,exactWholeBuriedFaceTerrainClearance=clearance,imagesActuallyViewed=images,reviewer='Codex ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,basis='The residual twelve points are lower edges of two narrow original vertical wall features. Each follows only one or two original wall faces to a positive-length authored boundary on the podium deck; these are local wall-to-deck relationships, not roof detours or separate ground roots. The one highest-surface buried facet is a vertical side face below that deck, fully clear of actual ground by exact finite-triangle interpolation. It shares an original edge with wall4206, which has an interior intersection with the podium. That crossing remains an authored assembly intersection, not a boundary or structural-support certification. No upward face is wholly buried. The cropped oblique source views support this lower-wall interpretation but do not prove hiddenness. Accept only this unchanged source/podium/ground tuple; do not alter canonical numerical results or global tolerances.',scope='Physical source interpretation only. Exact source identity, loader, current neighbours, staged/live browser and guarded publication remain independent required gates. No optimisation approval.',installationApproved=False,publicationApproved=False))
module('parkview5_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-block5-lower-wall-physical-review',refs,dict(uids=[UID],sourceSpecificPhysicalInterpretationAccepted=True,installationApproved=False,minimumWholeFaceGroundClearanceM=min(r['minimumWholeFaceGroundClearanceM']for r in clearance)))
