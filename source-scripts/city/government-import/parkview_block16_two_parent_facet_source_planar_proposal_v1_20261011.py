"""DRAFT nonpublishing two-facet source-planar recovery with strict3D seam rejection.
Writes NO local terrain proposal on seam/coverage failure; no live/geometry edits.
Any candidate passing this producer still needs fullsource/current/native gates.
"""
import importlib.util,json,copy
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest
from native_patch_resolution import _faces
from exact_source_planar_domain_recovery_seams_v1_20261011 import recover,projected
from exact_original_projection_coverage_v2_20261010 import subtract,signed_area
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-block16-two-parent-facet-source-planar-proposal-v1-20261011';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;AUTH=B/'xl-terrain-recovery-20261010-parkview-authentic-two-TIN-complete-conservative-v3';ATTR=B/'government-xl-parkview-block16-complete-cap-retained-obligations-v1-20261011';FOUR=B/'government-xl-parkview-block16-four-implicated-original-facets-primary-TIN-comparison-v1-20261011';INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json';PIN='4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def strings(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:strings(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [strings(v)for v in x]
 return x

def main():
 assert not DOC.exists()and not LOCAL.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start['sha256']==PIN
 refs=[ref(p)for p in [Path(__file__),INSTALLED,AUTH/'diagnostic.json.gz',AUTH/'result.json',ATTR/'diagnostic.json.gz',ATTR/'result.json',FOUR/'diagnostic.json.gz',FOUR/'result.json',HERE/'exact_source_planar_domain_recovery_seams_v1_20261011.py',HERE/'test_exact_source_planar_domain_recovery_seams_v1_20261011.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'native_patch_resolution.py',HERE/'pending-context.py']];attribution=read(ATTR/'diagnostic.json.gz');assert attribution['stableManifestSHA256']==PIN and read(FOUR/'result.json')['allFourOriginalTINStrictClear']is True;patch=read(INSTALLED);old=_faces(patch);assert len(old)==94794 and ref(INSTALLED)['sha256']=='12816eebe4f6600fd13a41a897bfd9c044e2a7ac5edf0dde0d7d76647642f1d6';removed=[94641,94645]
 for carrier,nid in zip([25014,25018],removed):
  r=next(r for r in attribution['allCurrentCapPairAttributions']if r['originalGroundFace']==carrier);assert r['exactInstalledNativeFacetMatches']==[nid]and digest(old[nid].tobytes())==r['fullGroundFacetSHA256'];assert [f['uid']for f in r['fullGroundFacetPreservationOverlaps']]==['landsd/256319:0']
 domains=old[removed];keptIDs=np.asarray([i for i in range(len(old))if i not in removed]);kept=old[keptIDs]
 spec=importlib.util.spec_from_file_location('block16_primary_tin_context',HERE/'pending-context.py');context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context);parts=[]
 for sheet in ['11-SE-21B','11-SE-16D']:
  folder=HERE/'local/government-xxl-second-20260911/sheets'/sheet;receiptpath=folder/'original/download.json';receipt=read(receiptpath);directory=folder/'directory/result.json';assert receipt['directorySHA256']==read(directory)['directorySHA256'];refs.extend([ref(receiptpath),ref(directory)]);gltfs=[]
  for ent in receipt['entries']:
   if ent['name'].startswith('TERRAIN')and ent['name'].endswith(('.gltf','.bin')):
    p=folder/'terrain'/ent['name'];assert digest(p.read_bytes())==ent['sha256'];refs.append(ref(p))
    if p.suffix=='.gltf':gltfs.append(p)
  assert gltfs;parts.extend(context.triangles(p)for p in sorted(gltfs))
 terrain=np.concatenate(parts);auth=next(r for r in read(AUTH/'diagnostic.json.gz')['rows']if r['uid']=='landsd/254491:0');assert len(terrain)==auth['authenticWholeSourceTerrainTriangles']==394774 and digest(terrain.tobytes())==auth['authenticWholeSourceTerrainSHA256'];assert digest(terrain.tobytes())=='740580e8f1bd38cddc48b956f5ca161de7fcebac2852d887d02ad60c1178cff5'
 lo,hi=domains[:,:,[0,2]].min((0,1)),domains[:,:,[0,2]].max((0,1))
 def candidates(faces):
  xz=faces[:,:,[0,2]];return np.flatnonzero(np.all(xz.max(1)>=lo,axis=1)&np.all(xz.min(1)<=hi,axis=1)).tolist()
 sid=candidates(terrain);rid=candidates(kept);assert len(sid)<=1024 and len(rid)<=1024,'Bounded complete projected inventories; never truncate';source=terrain[sid];retained=kept[rid];proof=recover(domains,source,retained);actual=None;candidate=None;proposalWritten=False;added=[]
 if proof['seamCompatible']:
  for piece in proof['exactSourcePlanarPieces']:
   poly=piece['exactPoints']
   for i in range(1,len(poly)-1):added.append([poly[0],poly[i],poly[i+1]])
  added=np.asarray(added,dtype='<f8').astype(np.float32).astype('<f8');assert np.isfinite(added).all();actual=recover(domains,added,retained);outside=F(0)
  for face in added:
   remain=[projected(face)]
   for domain in domains:remain=[p for oldpoly in remain for p in subtract(oldpoly,projected(domain))]
   outside+=sum(abs(signed_area(p))for p in remain)
  actual['exactAddedFloat32ProjectedExtentOutsideDomainsM2']=str(outside);actual['actualFloat32NonzeroFacets']=all(signed_area(projected(f))!=0 for f in added);actual['seamCompatible']=bool(actual['seamCompatible']and outside==0 and actual['actualFloat32NonzeroFacets'])
  if actual['seamCompatible']:
   proposal=copy.deepcopy(patch);mesh=proposal['nativeMesh'];originalPositions=list(mesh['position']);oldIndex=np.asarray(mesh['index']).reshape(-1,3);mesh['position']=originalPositions+added.reshape(-1).tolist();offset=len(originalPositions)//3;mesh['index']=oldIndex[keptIDs].reshape(-1).tolist()+list(range(offset,offset+added.size//3));mesh.pop('sourceOverlap',None);mesh['source']['twoParentFacetOriginalTINRecovery']=dict(removedOriginalInstalledFacets=removed,sourceFiles=refs,policy='Exact source-planar clipped original government TIN; strict3D retained-neighbour seams and actualFloat32 projection/seams. No sourceheight adjustment, snap or fabricated walls. Whole current/source/native/foreign acceptance remains required.');assert np.array_equal(_faces(proposal)[:len(kept)],kept);path=LOCAL/'terrain-two-parent-facet-original-TIN-candidate.json';save(path,proposal);proposalWritten=True;candidate=dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),triangles=len(mesh['index'])//3,bounds=[3892.5,3112.5,4312.5,3462.5],cells=[548,494,554,499],uids=['landsd/256319:0'],replaces=dict(url='city/data/'+INSTALLED.name,sha256=ref(INSTALLED)['sha256']));save(DOC/'terrain-candidates.json',[candidate])
 assert ref(manifest)==start
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,newlyInstalled=0,sourceGeometryChanges=0,liveTerrainChanges=0,nativeReacceptance=False,retentionRemovalApproved=False,currentManifest=start,removedOnlyOriginalInstalledFacets=removed,completeOriginalTINWorldSHA256=digest(terrain.tobytes()),completeSourceCandidateOriginalTINIds=sid,completeRetainedCandidateInstalledFacetIds=keptIDs[rid].tolist(),exactSourcePlanarPreFloat32Proof=strings(proof),actualFloat32Proof=strings(actual),localTerrainProposalWritten=proposalWritten,localTerrainCandidate=candidate,evidenceRefs=refs,required=['All11351 original/literal/left/balancedF32 finite-source/current-ground proof','All23foreign+all7installednative sourceground/support/regression gates; preserve completeBlock17drawnground','Bounded qualified nativegrade→wholeexposed sharededges→strictcap45867','Complete117groundedsourcepaths+7exactactualF32visualroles','Independentrootclosure/runtime/browser/publisher'],qualification='Strict3D retained-neighbour seam failure rejects localcandidate, even with2Dcoverage. No invented verticalwalls or height snaps. Passing seam/candidate production alone is not recovery/acceptance.'))
 print(json.dumps(dict(sourceCandidates=len(sid),retainedCandidates=len(rid),exactSourceSeamCompatible=proof['seamCompatible'],exactHeightIncompatibilities=sum(not p['heightCompatible']for p in proof['allExact3DSeamProofs']),localTerrainProposalWritten=proposalWritten,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
