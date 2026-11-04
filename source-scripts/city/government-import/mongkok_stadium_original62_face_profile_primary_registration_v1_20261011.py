"""DRAFT exact original62-facet authored plane/edge profile; no role or extent waiver."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json,numpy as np
from run import ROOT,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-mongkok-stadium-complete-original-far-extent-body-attribution-v1-20261011';PRIMARY=B/'government-xl-mongkok-stadium-bounded-official-lcsd-primary-context-v1-20261011';VISUAL=B/'government-xl-mongkok-stadium-complete-original-source-visual-context-v2-20261011';METHOD=B/'government-xl-mongkok-stadium-original62-face-profile-primary-registration-method-v1-20261011/METHOD.md';DOC=B/'government-xl-mongkok-stadium-original62-face-profile-primary-registration-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def q(v):return dict(numerator=v.numerator,denominator=v.denominator)
def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def main():
 assert not DOC.exists();d=read(OLD/'diagnostic.json.gz');context=read(VISUAL/'context.json');assert d['completeOriginalFaces']==context['completeOriginalFaces']==15456 and context['farFeatureDirection']=='southwest';refs=[]
 for base in [OLD,PRIMARY]:
  receipt=read(base/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for e in receipt['evidenceRefs']:assert ref(ROOT/e['path'])==e
  refs.append(ref(base/'result.json'))
 asset=ROOT/d['source']['path'];assert ref(asset)==d['source'];tri=decode_original_world_triangles(asset.read_bytes());assert tri.shape==(15456,3,3)and digest(tri.astype('<f8').tobytes())==d['completeOriginalWorldSHA256'];far=[r['originalFace']for r in d['all62OriginalFarFaceAttributions']];assert len(set(far))==62 and all(r['genuineSourceBody']==0 and r['wholeSourceExactSharedEdgePathToTargetProjectedOriginalFacet']for r in d['all62OriginalFarFaceAttributions']);rows=[];edges={};counts=Counter()
 for i in sorted(far):
  pts=[tuple(F(float(x))for x in p)for p in tri[i]];normal=cross(tuple(pts[1][j]-pts[0][j]for j in range(3)),tuple(pts[2][j]-pts[0][j]for j in range(3)));assert any(normal);kind='horizontal'if normal[0]==normal[2]==0 else'vertical'if normal[1]==0 else'inclined';counts[kind]+=1
  rows.append(dict(originalFace=i,exactPlaneNormal=[q(v)for v in normal],literalPlaneClass=kind,originalTriangle=tri[i].tolist(),minimumY=float(min(p[1]for p in pts)),maximumY=float(max(p[1]for p in pts)),functionUnqualified=True))
  for j in range(3):
   a,z=pts[j],pts[(j+1)%3];key=tuple(sorted([a,z]));edges.setdefault(key,[]).append(i)
 edge_rows=[dict(originalEndpoints=[[float(v)for v in p]for p in key],signedCanonicalRise=q(key[1][1]-key[0][1]),sameHeight=key[0][1]==key[1][1],allIncidentFarOriginalFaces=ids,wholeBodyIncidenceNotInferred=True)for key,ids in sorted(edges.items())]
 refs.extend(ref(p)for p in [Path(__file__),METHOD,asset,OLD/'diagnostic.json.gz',VISUAL/'context.json',PRIMARY/'diagnostic.json'])
 assert ref(asset)==d['source'];save(DOC/'diagnostic.json.gz',dict(uid='landsd/240332:0',source=d['source'],completeOriginalFaces=15456,completeOriginalWorldSHA256=d['completeOriginalWorldSHA256'],profileOriginalFaceCount=62,farOriginalOwningBody=0,exactOriginalFacePlaneProfiles=rows,literalPlaneCounts=dict(counts),completeFarOriginalEdgeProfiles=edge_rows,uniqueHorizontalOriginalLevels=sorted({r['minimumY']for r in rows if r['literalPlaneClass']=='horizontal'}),sourceOnly=True,currentAcceptance=False,identityAccepted=False,extentGuardWaived=False,architectureRoleAccepted=False,geographicPixelRegistrationPerformed=False,sourceGeometryChanges=0,terrainGeometryChanges=0,qualification='Exact original source face/edge profile only. Qualitative source/primary feature comparison is a separate human/AI source interpretation, with AnnexB marked not to scale and no sourceUID/height/ownership/support registration. All original14body/15zero/current identity/extent/physical obligations survive. Horizontal/vertical/inclined literal source planes are not architectural function or support.',evidenceRefs=refs));print(json.dumps(dict(faces=len(rows),literalPlaneCounts=dict(counts),edges=len(edges),currentAcceptance=False)))
if __name__=='__main__':main()
