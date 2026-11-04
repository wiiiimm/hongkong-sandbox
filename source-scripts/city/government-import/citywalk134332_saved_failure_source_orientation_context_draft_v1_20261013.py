"""DRAFT: saved source/proof orientation and views only; no ground/contact replay."""
import argparse,gzip,hashlib,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from west_wing26195_complete_current_finite_ground_draft_v3_20261012 import exact_orientation
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'docs/astra-city/government-import';P=BASE/'government-xl-citywalk134332-current-failure-source-role-recovery-proposal-v1-20261013';OUT=BASE/'government-xl-citywalk134332-saved-failure-source-orientation-context-v1-20261013';MANIFEST='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
def sha(b):return hashlib.sha256(b).hexdigest()
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes()))
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,sort_keys=True,indent=2,allow_nan=False)+'\n')
def inputs():
 c=read(P/'saved-input-contract.json');assert c['draftOnly']and c['noNumericalProofReplay']and not c['acceptance'];assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==MANIFEST
 for e in c['inputRefs']+c['codeRefs']:assert ref(ROOT/e['path'])==e
 plan=read(ROOT/c['groundCapturePlan']['path']);assert plan['sourceSHA256']==c['sourceSHA256']and plan['providerOriginalNPZ']==c['providerOriginalNPZ']and plan['capture']==c['actualAttributes']
 result=read(ROOT/c['finiteResult']['path']);assert result['jobId']==c['finiteJobId'];declared={e['path']:e['sha256']for e in result['evidenceRefs']};assert declared[c['finiteDiagnostic']['path']]==c['finiteDiagnostic']['sha256']
 d=read(ROOT/c['finiteDiagnostic']['path']);assert d['uid']=='landsd/134332:0'and d['currentManifest']['sha256']==MANIFEST and d['currentNativeCount']==6650;assert d['completeSourceFaces']==41277 and d['completeOriginalBodies']==193 and len(d['allSourceGroundBindings'])==12 and len(d['distinctCompleteFiniteProofs'])==3 and not d['physicalAccepted']and not d['installationApproved']
 components=read(ROOT/c['components']['path'])['components'];labels={i:b for b,z in enumerate(components)for i in z['sourceFaceIndices']};assert len(components)==193 and sorted(labels)==list(range(41277))
 with np.load(ROOT/c['providerOriginalNPZ']['path'],allow_pickle=False)as z:worlds={'providerOriginal':z[plan['providerOriginalNPZKey']].astype('<f8')}
 assert sha(worlds['providerOriginal'].tobytes())==plan['providerOriginalWorldSHA256']==c['providerOriginalWorldSHA256']
 attrs=read(ROOT/c['actualAttributes']['path']);r=attrs['rows'][0];assert r['loadedGroupScale']==[1,1,1];index=np.asarray(r['completeOriginalIndex'],int).reshape(-1,3);assert index.shape==(41277,3)
 for name,key in c['actualPositionFields'].items():
  position=np.asarray(r[key],dtype='<f8').reshape(-1,3);assert np.isfinite(position).all()and index.min()>=0 and index.max()<len(position);worlds[name]=position[index]
 for name,w in worlds.items():
  assert w.shape==(41277,3,3)and np.isfinite(w).all();bs=[b for b in d['allSourceGroundBindings']if b['sourceWorld']==name];assert len(bs)==3 and all(b['sourceWorldSHA256']==sha(w.tobytes())for b in bs)
 ground=read(ROOT/c['ground']['path']);t=np.asarray(ground['completeRegionalGroundWorlds']['actualLiteral'],dtype='<f8');assert t.shape==(4215,3,3)and np.isfinite(t).all()and sha(t.tobytes())==c['groundWorldSHA256']
 for p,h in ground['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 return c,d,components,labels,worlds,t,ground

def main():
 a=argparse.ArgumentParser();a.add_argument('--preflight-only',action='store_true');a=a.parse_args();c,d,components,labels,worlds,ground,g=inputs()
 if a.preflight_only:print(json.dumps(dict(savedInputsVerified=True,noGeometryPredicatesExecuted=True,noDB=True,noLease=True,completeFaces=41277,originalBodies=193,bindings=12)));return
 assert not OUT.exists();OUT.mkdir();profiles={};bindings=[]
 for name,w in worlds.items():
  binding=next(b for b in d['allSourceGroundBindings']if b['sourceWorld']==name and b['groundWorld']=='actualLiteral');key=binding['proofTupleSHA256'];bindings.append(dict(sourceWorld=name,proofTupleSHA256=key,wholeWorldSHA256=sha(w.tobytes())))
  if key in profiles:continue
  p=d['distinctCompleteFiniteProofs'][key];rows=p['allWholeFacetProofs'];assert [r['face']for r in rows]==list(range(41277));assert len(p['completeOriginalBodyObligations'])==193
  below=[r for r in rows if r['exactLowerM']is not None and F(r['exactLowerM'])<F(-1,2)];coverageonly=[r for r in rows if not r['completeProjectionCovered']and not(r['exactLowerM']is not None and F(r['exactLowerM'])<F(-1,2))];assert len(below)==683 and len(coverageonly)==1322
  records=[]
  for r in below:
   i=r['face'];assert labels[i]==r['originalBody'];records.append(dict(sourceFace=i,originalBody=labels[i],originalBodyLabelIsSourceProvenanceOnly=name!='providerOriginal',unchangedSourceWorldTriangle=w[i].tolist(),orientation=exact_orientation(w[i]),savedExactLowerM=r['exactLowerM'],savedExactMaximumFiniteColumnGapM=r['exactMaximumFiniteColumnGapM'],coverageProved=r['completeProjectionCovered'],savedProofFaceReference=dict(proofTupleSHA256=key,sourceFace=i),gradeRole=None,architectureFunction=None,groundRootAccepted=False))
  profiles[key]=dict(completeOriginalBodies=193,sourceWorld=name,belowMinusHalfFaceRecords=records,coverageOnlyFaceIDs=[r['face']for r in coverageonly],allCoverageFailureIDs=p['coverageFailingFaces'],allStrictWarningIDs=p['strictUncertifiedFaces'],allOrdinaryFalseIDs=p['ordinaryFailingFaces'])
 originalkey=next(b['proofTupleSHA256']for b in bindings if b['sourceWorld']=='providerOriginal');pp=profiles[originalkey];failed=[r['sourceFace']for r in pp['belowMinusHalfFaceRecords']];coverageonly=pp['coverageOnlyFaceIDs'];lowbody=sorted({labels[i]for i in failed});assert len(lowbody)==18
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 from PIL import Image
 w=worlds['providerOriginal'];outputs=[]
 def finish(fig,path,metadata):
  fig.savefig(path,dpi=150);plt.close(fig)
  with Image.open(path)as im:assert im.size==(1800,1500);size=list(im.size)
  outputs.append(dict(**ref(path),dimensions=size,**metadata))
 fig,ax=plt.subplots(figsize=(12,10));ax.add_collection(PolyCollection(w[:,:,[0,2]],facecolors='#c5c5c5',edgecolors='none',alpha=.25));ax.add_collection(PolyCollection(w[coverageonly][:,:,[0,2]],facecolors='#7250b7',edgecolors='#7250b7',linewidths=.2,alpha=.6));ax.add_collection(PolyCollection(w[failed][:,:,[0,2]],facecolors='#ef6500',edgecolors='#ef6500',linewidths=.3,alpha=.8));ax.autoscale();ax.set_aspect('equal');ax.set_xlabel('Unchanged source world X (m)');ax.set_ylabel('Unchanged source world Z (m)');ax.set_title('Complete original Citywalk: orange below-bound683; purple coverage-only1322\nOrientation/role unresolved; projected views cannot prove 3D collision or support')
 finish(fig,OUT/'complete-source-failure-plan-1800x1500.png',dict(sourceFacesSubmitted=41277,belowBoundHighlightedFaceIDs=failed,coverageOnlyHighlightedFaceIDs=coverageonly,completeSourcePlan=True))
 for title,filename,low in [('Complete source/current ground context','complete-source-ground-3d-1800x1500.png',False),('Low body0 and repeated upright source-surface context','lower-body0-repeated-source-context-1800x1500.png',True)]:
  fig=plt.figure(figsize=(12,10));ax=fig.add_subplot(111,projection='3d');ax.add_collection3d(Poly3DCollection(ground[:,:,[0,2,1]],facecolor='#808080',edgecolor='none',alpha=.035));ax.add_collection3d(Poly3DCollection(w[:,:,[0,2,1]],facecolor='#679ac0',edgecolor='none',alpha=.035));ax.add_collection3d(Poly3DCollection(w[failed][:,:,[0,2,1]],facecolor='#ef6500',edgecolor='#ef6500',linewidth=.15,alpha=.85));lo=np.minimum(w.min((0,1)),ground.min((0,1)));hi=np.maximum(w.max((0,1)),ground.max((0,1)));focus=[components[i]for i in range(114,120)];xl=[min(z['worldBounds'][0][0]for z in focus)-2,max(z['worldBounds'][1][0]for z in focus)+2]if low else[float(lo[0]),float(hi[0])];zl=[min(z['worldBounds'][0][2]for z in focus)-2,max(z['worldBounds'][1][2]for z in focus)+2]if low else[float(lo[2]),float(hi[2])];yl=[2,11]if low else[float(lo[1]),float(hi[1])];ax.set_xlim(*xl);ax.set_ylim(*zl);ax.set_zlim(*yl);ax.set_box_aspect((xl[1]-xl[0],zl[1]-zl[0],yl[1]-yl[0]));ax.view_init(elev=22,azim=-65);ax.set_xlabel('Source X (m)');ax.set_ylabel('Source Z (m)');ax.set_zlabel('Source Y (m)');ax.set_title(title+'\nTransparent diagnostic layers; duplicate highlight overlays; occlusion possible'+('\nDisplay repeated114–119 bounds+2m and Y2..11m crop; all source triangles submitted'if low else''))
  finish(fig,OUT/filename,dict(sourceFacesSubmitted=41277,currentLiteralGroundFacesSubmitted=4215,highlightedOriginalBodyIDs=lowbody,highlightedFaceIDs=failed,allSourceTrianglesSubmitted=True,transparentLayeredDiagnosticNotActualGPUVisibility=True,duplicateHighlightOverlays=True,occlusionPossible=True,verticalDisplayCropY=[2,11]if low else None,horizontalDisplayCropXZ=[xl,zl]if low else None,displayFocusOriginalBodies=list(range(114,120))if low else None,equalSourceUnitBoxAspect=True))
 for e in c['inputRefs']+c['codeRefs']:assert ref(ROOT/e['path'])==e
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==MANIFEST
 for p,h in g['inputHashes'].items():assert ref(ROOT/p)['sha256']==h
 save(OUT/'source-context.json',dict(sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,gradeRootAccepted=False,sourceGeometryChanges=0,terrainGeometryChanges=0,noDBQueries=True,noReservations=True,noFiniteContactOrTerrainReplay=True,completeSourceFaces=41277,completeOriginalBodies=193,bodyPartition=components,allSourceGroundBindings=d['allSourceGroundBindings'],orientationProfiles=profiles,profileBindings=bindings,positiveSavedMaximumIsNotMAXExposure=True,noSourceRoleFromSignsOrCounts=True,completeGroundIsCapturedActualLiteralOnlyForViews=True,inputRefs=c['inputRefs']+c['codeRefs'],inputContract=ref(P/'saved-input-contract.json'),outputs=outputs));print(json.dumps(dict(context=ref(OUT/'source-context.json'),outputs=outputs)),flush=True)
if __name__=='__main__':main()
