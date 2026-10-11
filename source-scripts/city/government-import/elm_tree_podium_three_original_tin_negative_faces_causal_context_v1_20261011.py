"""DRAFT source/body/vertex attribution of three preserved authenticTIN negatives.
Uses complete saved exact pair proofs; no repeat clearance, grade/function waiver,
solver, source/terrain edit or current capture. No installation/root credit.
"""
from pathlib import Path
from fractions import Fraction as F
import json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-elm-tree-podium-three-original-tin-negative-faces-causal-context-v1-20261011';DOC=B/BATCH;TIN=B/'government-xl-elm-tree-b-podium-complete-original-authentic-tin-finite-v1-20261011';CONTACT=B/'government-xl-elm-tree-b-original-podium-complete-finite-contact-inventory-v1-20261011';OLD=B/'government-xl-elm-tree-podium-physical-20261007'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__)),ref(HERE/'exact_packed_world_geometry_20261009.py')]
 for doc in [TIN,CONTACT]:
  receipt=read(doc/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(doc/n)for n in ['result.json','diagnostic.json.gz','review.json']if(doc/n).exists())
 d=read(TIN/'diagnostic.json.gz');r=next(r for r in d['rows']if r['uid']=='landsd/258892:0');assert r['ordinaryFailingFaces']==[102,103,104]and not r['coverageFailingFaces'];asset=ROOT/r['source']['path'];assert ref(asset)==r['source'];world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(764,3,3)and digest(world.tobytes())==r['completeOriginalWorldSHA256'];contact=read(CONTACT/'diagnostic.json.gz');census=contact['completePodiumNonzeroBodyCensus'];bodies=census['sharedEdgeConnectedComponents'];assert len(bodies)==1 and sorted(bodies[0])==list(range(764))and contact['completePodiumWorldSHA256']==digest(world.tobytes());groundfile=HERE/'local'/TIN.name/'complete-original-tin-covering-whole-facets.json.gz';t=read(groundfile);ground=np.asarray(t['completeSelectedFacets'],float);assert digest(ground.tobytes())==t['completeSelectedFacetSHA256'];rows=[];corners={}
 for i in [102,103,104]:
  proof=r['allFaces'][i];assert proof['sourceFace']==i and not proof['ordinaryFiniteProved'];face=world[i];a,b,c=face;normal=np.cross(b-a,c-a);assert np.any(normal!=0)and normal[1]==0;pairs=[p for p in proof['allRefinedFiniteColumnPairs']if p['proof']['exactClosedHorizontalProjectionsMeet']];assert pairs;minimum=min(F(p['proof']['exactMinimumFiniteColumnGapM'])for p in pairs);assert minimum==F(proof['exactLowerM']);minima=[]
  for p in pairs:
   j=p['originalGroundFace'];pp=p['proof'];assert digest(face.tobytes())==pp['sourceFaceSHA256']and digest(ground[j].tobytes())==pp['groundFaceSHA256']
   for v in pp['allExactBasicFeasibleColumnVertices']:
    if F(v['exactGapM'])!=minimum:continue
    point=np.asarray([float(F(x))for x in v['exactSourcePoint']]);incident=np.flatnonzero(np.any(np.all(world==point,axis=2),axis=1)).tolist();assert incident,'Minimum source point not an original vertex; cannot infer corner incidence';key=tuple(v['exactSourcePoint']);corners[key]=dict(exactOriginalSourcePoint=list(key),completeOriginalIncidentFaces=incident,completeOriginalIncidentCoordinates=[dict(sourceFace=k,vertices=world[k].tolist())for k in incident],genuineBody=0);minima.append(dict(selectedOriginalTINFacet=j,completeOriginalSheetFacet=t['completeSelectedFacetIds'][j],originalTINFacet=ground[j].tolist(),exactPairMinimum=v))
  rows.append(dict(originalSourceFace=i,genuineBody=0,coordinates=face.tolist(),nonzero3DVerticalFacet=True,exactZeroProjectedArea=True,minimumExactGapM=str(minimum),allExactMinimizingFinitePairs=minima))
 old=next(r for r in read(OLD/'selection.json.gz')['rows']if r['uid']=='landsd/258892:0');assert old['sourceSHA256']==r['source']['sha256'];candidate=old['native']['model']['candidate'];refs.extend([ref(asset),ref(groundfile),ref(OLD/'selection.json.gz')]);assert all(ref(ROOT/x['path'])==x for x in refs)
 save(DOC/'diagnostic.json.gz',dict(uids=['landsd/258892:0','landsd/253874:0'],sourceOnly=True,currentAcceptance=False,installationApproved=False,originalSourceFacets=764,wholeSingleGenuineBodyRetained=True,threeRawNegativeFacets=rows,allExactNegativeCornerIncidence=list(corners.values()),recordedProviderBaseHeightHKPD=candidate['recordedBaseHeight'],recordedProviderTopHeightHKPD=candidate['recordedTopHeight'],metadataBaseNotGroundOrArchitecturalIntent=True,all306TowerBodyObligationsRemain=True,prior223CurrentNegativeFacetsPreserved=True,originalSourceGeometryChanges=0,terrainGeometryChanges=0,terrainProposalCreated=False,gradeRootCredit=False,functionUnknown=True,evidenceRefs=refs,qualification='Exact attribution of existing source-only whole764 finite proof: three nonzero vertical original facets remain genuinely below authentic sourceTIN. A single connected sourcebody forbids detached-detail omission. Provider recorded base is elevation metadata, not proof of intentional below-grade use or current support. No source shift, originalTIN/unchanged-terrain recovery, architectural function or tolerance waiver; a distinct authoritative grade/source input or explicitly evidenced altered-terrain method with complete 3D seams and current TowerB/native/foreign protection would be required. No global impossibility claim.'));print(json.dumps(dict(uids=['landsd/258892:0','landsd/253874:0'],negativeFaces=[102,103,104],exactMinimumSourceCorners=len(corners),currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
