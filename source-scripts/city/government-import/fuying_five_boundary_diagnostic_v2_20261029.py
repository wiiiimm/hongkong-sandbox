"""Private whole-parent replacement contract and unchanged native validator replay."""
from pathlib import Path
import copy,json,subprocess,sys,uuid,traceback
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
import fuying_whole_parent_five_boundary_v1_20261029 as boundary
from fuying_private_boundary_connectors_v1_20261029 import add_connectors
from float32_coverage import approve_roundoff
from native_patch_resolution import projected_context
import shapely
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-fuying181489-five-member-boundary-contract-v2-20261029'
PRIOR='government-xl-fuying181489-five-node-roundoff-v1-20261029'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();receipt,pins=authenticate(BASE/PRIOR)
 refs=[Path(__file__),HERE/'fuying_whole_parent_five_boundary_v1_20261029.py',BASE/PRIOR/'result.json']
 def take(p):assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 summary=take(BASE/PRIOR/'summary.json');assert summary['allNumericalCoverageAndOverlapPassed']
 nomination=BASE/'government-xl-fuying181489-boundary-local-plane-nomination-v1-20261029';_,npins=authenticate(nomination);nompath=nomination/'summary.json';assert ref(nompath)['sha256']==npins[str(nompath.relative_to(ROOT))];nom=read(nompath);assert nom['allHaveLocalPlaneNomination']and nom['allHaveFiniteMateNomination'];refs.extend([nomination/'result.json',nompath,HERE/'fuying_private_boundary_connectors_v1_20261029.py',HERE/'float32_coverage.py',HERE/'native_patch_resolution.py'])
 oldpath=ROOT/summary['oldParent']['path'];assert ref(oldpath)==summary['oldParent'];old=read(oldpath);refs.append(oldpath)
 rootpath=ROOT/'3d-viewer'/old['meta']['parentTerrain'];assert digest(rootpath.read_bytes())==old['meta']['parentSha256'];root=read(rootpath);refs.append(rootpath)
 DOC.mkdir();members={};nodes={};originals={}
 for item in summary['members']:
  node=take(ROOT/item['candidate']['path']);originals[item['member']]=copy.deepcopy(node)
  node=add_connectors(node,[r for r in nom['witnesses']if r['member']==item['member']])
  node['nativeMesh'].pop('sourceOverlap',None);node['nativeMesh']['source'].pop('numericalProjectionOverlap',None)
  bounds=boundary.legacy.bounds(node);_,polygons,_,_=projected_context(node,bounds)
  if shapely.union_all(polygons).symmetric_difference(shapely.box(*bounds)).area:save(DOC/(item['member']+'-fresh-coverage.json'),approve_roundoff(node,bounds))
  unbound=copy.deepcopy(node);unbound['nativeMesh'].pop('sourceOverlap',None)
  p=LOCAL/(item['member']+'-contract-body.json');save(p,unbound);refs.append(p)
  members[item['member']]=dict(candidate=ref(p),canonicalSHA256=boundary.legacy.canonical_sha(unbound));nodes[item['member']]=node
 proof=dict(policy=boundary.POLICY,parent=ref(rootpath),oldNative=summary['oldParent'],members=members,targetUids=summary['completeTargetObligations'])
 proofpath=DOC/'whole-parent-contract.json';save(proofpath,proof);refs.append(proofpath)
 boundary.load(ref(proofpath),root);rows=[];marked=[]
 for name,node in nodes.items():
  node['nativeMesh']['source']['coordinatedBoundary']=dict(policy=boundary.POLICY,proof=ref(proofpath),member=name)
  node['nativeMesh'].pop('sourceOverlap',None)
  # The marker changes the proof identity, so regenerate only the metadata-bound
  # numerical overlap approval. Existing terrain coordinates stay identical.
  source=LOCAL/(name+'-marked-pre-overlap.json');save(source,node);refs.append(source)
  overlap=module('fuying_marked_overlap_'+name.replace('-','_'),HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py');overlap.DOC=DOC/name;overlap.DOC.mkdir()
  row=dict(member=name,terrainValidatorPassed=False)
  try:
   overlap.overlap_proof(node,[source,proofpath,Path(__file__)])
   original=originals[name];assert node['nativeMesh']['position'][:len(original['nativeMesh']['position'])]==original['nativeMesh']['position']and node['nativeMesh']['index'][:len(original['nativeMesh']['index'])]==original['nativeMesh']['index']
   with boundary.private_validator():
    from native_terrain_validation import validate_native_mesh
    validate_native_mesh(node,root)
   row['terrainValidatorPassed']=True
  except Exception as error:row.update(errorType=type(error).__name__,reason=str(error),traceback=traceback.format_exc())
  path=LOCAL/(name+'-private-boundary-candidate.json');save(path,node);refs.append(path);row['candidate']=ref(path);rows.append(row);marked.append(node);print({k:v for k,v in row.items()if k!='traceback'},flush=True)
 with boundary.private_validator():boundary.validate_effective_coordinated_members(marked)
 assert reservations.owns(lease);result=dict(uids=summary['uids'],sourceSHA256ByUid=summary['sourceSHA256ByUid'],oldParent=summary['oldParent'],members=rows,completeTargetObligations=summary['completeTargetObligations'],wholeOldExtentEffectiveReplacementVerified=True,allFiveEffectiveMembersVerified=True,allTerrainValidatorsPassed=all(r['terrainValidatorPassed']for r in rows),sourceGeometryChanges=0,sourcePoseChanges=0,terrainPositionsAndIndicesChanged=True,allPriorTerrainPositionsAndIndicesPreserved=True,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Private additive derived-terrain connectors from exact existing finite mates, retaining all prior coordinates/indices. Government buildings unchanged. Complete five-member whole-native-parent replacement. Canonical native validator replay with unchanged finite1cm seam/2mm same-triangle/vertical-strip arithmetic; outer edges retain ordinary root checks. No publication/runtime registration. Actual renderer, all6source/foreign regressions, physical identity and browsers remain separate obligations.')
 save(DOC/'summary.json',result);refs.extend([HERE/'sham_shui_po_pool_shared_terrain_v2_20261016.py',HERE.parent/'island-detail-integration/native_terrain_validation.py',HERE.parent/'island-detail-integration/coordinated_native_boundary.py',HERE/'coordinated_native_boundary_v1_20261023.py',HERE/'finite_native_boundary_strip_v1_20261023.py'])
 module('fuying_whole_parent_boundary_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-whole-native-parent-five-member-effective-boundary-validator',refs,result)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();summary=read(BASE/PRIOR/'summary.json')
 resources=['building:'+uid for uid in summary['completeTargetObligations']]+['terrain:city/data/terrain.json','terrain:city/data/government-native-fu-wong-original-v1-20261023.json']
 claim=reservations.claim('fuying-five-boundary-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)))
  subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
