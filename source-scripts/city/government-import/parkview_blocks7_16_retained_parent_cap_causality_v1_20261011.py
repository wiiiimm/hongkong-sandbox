"""Source-only attribution of existing exact buried-cap witnesses.

Replays only recorded old-parent preservation, never constructs/modifies terrain.
No new cap refinement, source edit, tolerance, acceptance or publication credit.
"""
import importlib.util,itertools,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from rendered_patch_sampler import RenderedPatchSampler
from native_patch_resolution import _faces
B=ROOT/'docs/astra-city/government-import'
CAP=B/'government-xl-parkview-next-three-exact-cap-refinement-v1-20261011'
V4=B/'xl-terrain-recovery-20261011-parkview-authentic-foreign-preserved-terrain-proposal-v4'
PROBE=B/'government-xl-terrain-recovery-parkview-block11-complete-original-proposed-current-probe-v4-20261011'
DOC=B/'government-xl-parkview-blocks7-16-retained-parent-cap-causality-v1-20261011'
PARENT=ROOT/'3d-viewer/city/data/government-native-255439-0.json'
INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def matches(faces,t):
 ids=set()
 for perm in itertools.permutations(range(3)):
  ids.update(np.flatnonzero(np.all(faces[:,perm,:]==t,axis=(1,2))).tolist())
 return sorted(ids)
def main():
 assert not DOC.exists()
 refs=[ref(p)for p in [Path(__file__),CAP/'diagnostic.json.gz',CAP/'result.json',V4/'terrain.json',V4/'result.json',PARENT,INSTALLED,ROOT/'3d-viewer/city/data/terrain.json',HERE/'rendered_patch_sampler.py',HERE/'native_patch_resolution.py',HERE/'xl-second-pass.py',HERE/'xl-terrain-recovery-20261011-parkview-authentic-foreign-preserved-terrain-proposal-v4.py']]
 for folder in [CAP,V4]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 # Bind before-parent from the original immutable producer's receipt, rather
 # than infer provenance solely from membership in a preserved rectangle.
 oldrefs=read(V4/'result.json')['evidenceRefs'];assert ref(PARENT)in oldrefs
 cap=read(CAP/'diagnostic.json.gz');v4=read(V4/'terrain.json');assert ref(INSTALLED)['sha256']==v4['patch']['sha256']
 runtime=HERE/'local'/PROBE.name/'runtime-geometry.json.gz';refs.append(ref(runtime));rt=next(r for r in read(runtime)['rows']if r['uid']=='landsd/254491:0');ground=np.asarray(rt['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert digest(ground.tobytes())==cap['completeFrozenGroundSHA256']
 spec=importlib.util.spec_from_file_location('parkview_causal_resolution',HERE/'xl-second-pass.py');second=importlib.util.module_from_spec(spec);spec.loader.exec_module(second)
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');old=read(PARENT);fallback=second.resolution.terrain.fine.DemSampler(parent,rendered=True);sampler=RenderedPatchSampler(old,fallback,second.resolution.terrain.fine.DemSampler(old,rendered=True))
 protected=shapely.union_all([shapely.box(*f['outwardDyadicRectangleBounds'])for f in v4['preservedOrdinaryForms']]).intersection(shapely.box(*v4['patch']['bounds']))
 retained=np.asarray(sampler.surface_faces(protected),dtype=np.float32).astype('<f8').reshape(-1,3,3)
 assert len(retained)==v4['additionalParentPreservation']['parentTriangles']==1939
 installed=_faces(read(INSTALLED));rows=[]
 for row in cap['rows']:
  if row['uid']not in ['landsd/256319:0','landsd/255646:0']:continue
  pair=min((p for p in row['newPairProofs']if p['proof']['exactClosedHorizontalProjectionsMeet']),key=lambda p:F(p['proof']['exactMinimumFiniteColumnGapM']))
  witness=min(pair['proof']['allExactBasicFeasibleColumnVertices'],key=lambda p:F(p['exactGapM']));x,y,z=map(F,witness['exactSourcePoint']);gid=pair['originalGroundFace'];face=ground[gid]
  assert digest(face.tobytes())==pair['proof']['groundFaceSHA256'];assert F(witness['exactGapM'])<0
  im=matches(installed,face);rm=matches(retained,face)
  containing=[f['uid']for f in v4['preservedOrdinaryForms']if F(f['outwardDyadicRectangleBounds'][0])<=x<=F(f['outwardDyadicRectangleBounds'][2])and F(f['outwardDyadicRectangleBounds'][1])<=z<=F(f['outwardDyadicRectangleBounds'][3])]
  rows.append(dict(uid=row['uid'],cap=row['cap'],existingExactNegativeWitness=witness,exactGapM=witness['exactGapM'],frozenGroundFace=gid,groundFacetSHA256=pair['proof']['groundFaceSHA256'],exactInstalledNativeFacetMatches=im,exactReplayedRecordedParentClipMatches=rm,preservedOrdinaryFormWitnessContains=containing,retainedParentAttributionProved=bool(im and rm),qualifications=['Exact witness and full responsible facet only; not a whole cap/root/ground proof.','Recorded ordinary forms remain independent obligations. Attribution does not authorize removal of retention, lower source caps, terrain edits or waivers.']))
 for r in refs:assert ref(ROOT/r['path'])==r
 out=dict(rows=rows,completeRecordedParentReplayFacets=len(retained),completeFrozenGroundSHA256=cap['completeFrozenGroundSHA256'],installedTerrain=ref(INSTALLED),unchangedRecordedParent=ref(PARENT),evidenceRefs=refs,sourceOnly=True,sourceGeometryChanges=0,terrainChanges=0,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0,causalWitnessAttributionOnly=True)
 save(DOC/'diagnostic.json.gz',out);print(json.dumps(dict(rows=rows,sourceOnly=True)),flush=True)
if __name__=='__main__':main()
