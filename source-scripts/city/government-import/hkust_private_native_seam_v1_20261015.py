"""Apply existing bounded terrain seam helper to private HKUST proposal only."""
from pathlib import Path
import numpy as np,shapely,uuid
from run import ROOT,HERE,read,save,digest,reservations
from primrose_compound_foundation_v2_20261015 import module
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-hkust-private-native-candidate-v2-20261015';DOC=B/'government-xl-hkust-private-native-seam-v1-20261015';P=B/'government-xl-hkust309822-232155-target-provenance-draft-v1-20261014/cached-complete-original-arrays-v1'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();r=read(OLD/'result.json');pins={x['path']:x['sha256'] for x in r['evidenceRefs']};plan=read(OLD/'proposal.json');pp=ROOT/plan['parent']['path'];mp=ROOT/plan['manifest']['path'];assert ref(pp)==plan['parent'] and ref(mp)==plan['manifest'];patchp=ROOT/plan['candidate']['path'];assert ref(patchp)==plan['candidate'];patch=read(patchp);parent=read(pp);paths=[Path(__file__),OLD/'result.json',OLD/'proposal.json',pp,mp,patchp,HERE/'native_patch_resolution.py',HERE/'resolve-pass.py'];shapes=[]
 for uid in r['uids']:
  p=P/(uid.replace('/','-').replace(':','-')+'.json.gz');assert ref(p)['sha256']==pins[str(p.relative_to(ROOT))];t=np.array(read(p)['completeOrderedOriginalTriangles']);poly=shapely.polygons(t[:,:,[0,2]]);shapes.append(shapely.union_all(poly[shapely.area(poly)>0]));paths.append(p)
 projection=shapely.union_all(shapes);helper=module('hkust_seam_helper',HERE/'native_patch_resolution.py');constructor=module('hkust_seam_validator',HERE/'resolve-pass.py');sampler=constructor.terrain.fine.DemSampler(parent,rendered=True);bounds=plan['bounds'];claim=reservations.claim('hkust-seam-'+str(uuid.uuid4()),['private-terrain-seam:'+DOC.name],batch=DOC.name,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();error=None;fill=None;snap=None
  try:
   gap=helper.projected_context(patch,bounds)[2].intersection(projection);fill=helper.fill_narrow_source_seam(patch,bounds,projection,sampler,tolerance=.02) if gap.area>1e-6 else helper.fill_parent_only_holes(patch,parent,bounds,projection,sampler);snap=helper.snap_boundary_to_parent(patch,bounds,sampler);constructor.validate_patch(patch,parent)
  except Exception as e:error={'type':type(e).__name__,'message':str(e)}
  save(DOC/'unapproved-native-patch.json',patch);ctx=helper.projected_context(patch,bounds);out={'uids':r['uids'],'fill':fill,'boundarySnap':snap,'validatorPassed':error is None,'validatorFailure':error,'remainingGapAreaM2':ctx[2].area,'protectedRemainingGapAreaM2':ctx[2].intersection(projection).area,'projectedOverlapAreaM2':ctx[3],'sourceBuildingGeometryChanges':0,'publication':False,'installationApproved':False};save(DOC/'diagnostic.json',out)
  module('hkust_seam_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(DOC.name,'hkust-private-existing-source-seam-repair-v1',paths,{**out,'nextStep':'Resolve exact remaining constructor/validator issue before actual runtime capture and complete parent-extent current-actor regression. Source interpretation and identity still independent.'});print(out,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
