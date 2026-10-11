"""DRAFT source-only complete cap-obligation attribution; no terrain proposal.
Reuse all48 exact finite cap/ground pairs only after full current tuple equality.
Replays recorded1939 parent clips, inventories responsible original rectangles.
No support/retention discharge, native reapproval or current acceptance.
"""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from rendered_patch_sampler import RenderedPatchSampler
from native_patch_resolution import _faces
from parkview_blocks7_16_retained_parent_cap_causality_v1_20261011 import matches
from parkview_block16_original_cap_primary_tin_comparison_v1_20261011 import rectangle_area
B=ROOT/'docs/astra-city/government-import';PIN='4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285'
CAP=B/'government-xl-parkview-next-three-exact-cap-refinement-v1-20261011';V4=B/'xl-terrain-recovery-20261011-parkview-authentic-foreign-preserved-terrain-proposal-v4';CURRENT=B/'government-xl-parkview-block16-fresh-current-carrier-capture-v1-20261011';PHYSICAL=B/'government-xl-parkview-block16-fresh-current-physical-capture-v1-20261011';DOC=B/'government-xl-parkview-block16-complete-cap-retained-obligations-v1-20261011'
PARENT=ROOT/'3d-viewer/city/data/government-native-255439-0.json';INSTALLED=ROOT/'3d-viewer/city/data/terrain-government-xl-parkview-block11-authentic-installed-v1-20261011.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==PIN
 paths=[Path(__file__),CAP/'diagnostic.json.gz',CAP/'result.json',V4/'terrain.json',V4/'result.json',CURRENT/'selection.json.gz',CURRENT/'capture-scope.json',CURRENT/'result.json',PHYSICAL/'source-preflight.json',PHYSICAL/'current-raw-outcome.json',PHYSICAL/'foundation.json',PHYSICAL/'result.json',PARENT,INSTALLED,ROOT/'3d-viewer/city/data/terrain.json',HERE/'rendered_patch_sampler.py',HERE/'native_patch_resolution.py',HERE/'xl-second-pass.py',HERE/'parkview_blocks7_16_retained_parent_cap_causality_v1_20261011.py',HERE/'parkview_block16_original_cap_primary_tin_comparison_v1_20261011.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']
 for folder in [CAP,V4,CURRENT,PHYSICAL]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 scope=read(CURRENT/'capture-scope.json');assert scope['currentManifest']['sha256']==PIN;sel=read(CURRENT/'selection.json.gz')['rows'][0];asset=ROOT/sel['candidate']['path'];paths.append(asset);native=decode_original_world_triangles(asset.read_bytes());old=read(CAP/'diagnostic.json.gz');assert digest(native.tobytes())==old['completeOriginalNativeWorldSHA256']
 runtime=HERE/'local'/CURRENT.name/'runtime-geometry.json.gz';paths.append(runtime);ground=np.asarray(read(runtime)['rows'][0]['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3);assert digest(ground.tobytes())==old['completeFrozenGroundSHA256'];assert len(ground)==25167
 row=next(r for r in old['rows']if r['uid']=='landsd/256319:0');face=native[row['cap']];assert row['cap']==45867 and digest(face.tobytes())==row['sourceFacetSHA256'];assert row['wholeFiniteCapStrictClear']is False
 assert sorted(p['originalGroundFace']for p in row['newPairProofs'])==sorted(row['completeClosedAABBCandidateGroundIDs']);assert len(row['newPairProofs'])==48
 v4=read(V4/'terrain.json');assert ref(PARENT)in read(V4/'result.json')['evidenceRefs'];assert ref(INSTALLED)['sha256']==v4['patch']['sha256']
 spec=importlib.util.spec_from_file_location('block16_parent_replay',HERE/'xl-second-pass.py');second=importlib.util.module_from_spec(spec);spec.loader.exec_module(second)
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');oldparent=read(PARENT);fallback=second.resolution.terrain.fine.DemSampler(parent,rendered=True);sampler=RenderedPatchSampler(oldparent,fallback,second.resolution.terrain.fine.DemSampler(oldparent,rendered=True));protected=shapely.union_all([shapely.box(*f['outwardDyadicRectangleBounds'])for f in v4['preservedOrdinaryForms']]).intersection(shapely.box(*v4['patch']['bounds']));retained=np.asarray(sampler.surface_faces(protected),dtype=np.float32).astype('<f8').reshape(-1,3,3);assert len(retained)==1939;installed=_faces(read(INSTALLED));rows=[]
 for pair in row['newPairProofs']:
  gid=pair['originalGroundFace'];g=ground[gid];proof=pair['proof'];assert digest(g.tobytes())==proof['groundFaceSHA256'];assert proof['sourceFaceSHA256']==row['sourceFacetSHA256']
  overlaps=[dict(uid=f['uid'],exactFullGroundFacetRectangleOverlapAreaM2=str(rectangle_area(g,f['outwardDyadicRectangleBounds'])),fullRecordedOrdinaryForm=f['fullCurrentForm'],rawBeforeAfterFinding=f['rawBeforeAfterFinding'])for f in v4['preservedOrdinaryForms']if rectangle_area(g,f['outwardDyadicRectangleBounds'])>0]
  im=matches(installed,g);rm=matches(retained,g);meet=proof['exactClosedHorizontalProjectionsMeet'];negative=bool(meet and F(proof['exactMinimumFiniteColumnGapM'])<0)
  rows.append(dict(originalGroundFace=gid,fullGroundFacetSHA256=proof['groundFaceSHA256'],exactPairProofVerbatim=proof,hasNegativeFiniteCapGap=negative,exactInstalledNativeFacetMatches=im,exactRecordedParentReplayFacetMatches=rm,fullGroundFacetPreservationOverlaps=overlaps,parentFacetAttribution=bool(im and rm),retentionDischarged=False))
 capoverlaps=[dict(uid=f['uid'],exactWholeCapRectangleOverlapAreaM2=str(rectangle_area(face,f['outwardDyadicRectangleBounds'])))for f in v4['preservedOrdinaryForms']if rectangle_area(face,f['outwardDyadicRectangleBounds'])>0]
 refs=[ref(p)for p in paths];assert digest(manifest.read_bytes())==PIN
 for r in refs:assert ref(ROOT/r['path'])==r
 out=dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,newlyInstalled=0,sourceGeometryChanges=0,terrainChanges=0,retentionRemovalApproved=False,nativeReacceptance=False,stableManifestSHA256=PIN,completeOriginalNativeWorldSHA256=old['completeOriginalNativeWorldSHA256'],completeCurrentDrawnGroundSHA256=old['completeFrozenGroundSHA256'],completeCapCurrentPairCount=48,completeRecordedParentReplayFacets=1939,existingWholeCapFailureVerbatim=row,wholeCapPreservationOverlap=capoverlaps,allCurrentCapPairAttributions=rows,fullCurrentRawOwnedFailureVerbatim=read(PHYSICAL/'current-raw-outcome.json'),wholeCurrentFoundationVerbatim=read(PHYSICAL/'foundation.json'),evidenceRefs=refs,qualification='Full facet provenance/recorded obligation attribution only. Full-facet rectangle intersections may exceed the cap-contact overlap and cannot imply obligation discharge. No proposed terrain or fresh support path; all installed/foreign obligations remain independently required.')
 save(DOC/'diagnostic.json.gz',out);print(json.dumps(dict(completePairs=48,negativeFinitePairs=sum(r['hasNegativeFiniteCapGap']for r in rows),negativeRetainedPairs=sum(r['hasNegativeFiniteCapGap']and r['parentFacetAttribution']for r in rows),wholeCapPreservationOverlap=capoverlaps,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
