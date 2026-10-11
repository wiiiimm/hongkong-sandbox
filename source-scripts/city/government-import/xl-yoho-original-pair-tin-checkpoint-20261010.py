"""Fence authentic source-TIN improvement and exact remaining exterior/gap faces."""
import importlib.util,json
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from yoho_eight_related_original_podium_identity_20261009 import ring_poly
BATCH='government-xl-yoho-original-pair-source-tin-context-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
def main():
 d=read(DOC/'diagnostic.json.gz');summary=d['summary'];assert summary['affectedUpwardFaces']==0 and summary['affectedFaces']==2 and summary['uncoveredFaces']==3
 base=DOC.parent;capture=read(base/'government-xl-yoho-eight-bound-current-provider-source-20261009/current-inputs.json.gz');source=ROOT/capture['podiumOriginalPath'];tri=decode_original_world_triangles(source.read_bytes());g=read(base/'government-xl-yoho-original-podium-current-ground-20261010/diagnostic.json.gz');targets=shapely.union_all([ring_poly(b['rings']) for b in g['allCurrentForms'] if b['uid'] in ['landsd/146396:0','landsd/231756:0']]);dist=shapely.distance(shapely.points(tri[:,:,[0,2]].reshape(-1,2)),targets).reshape(-1,3);ids=np.flatnonzero(dist.max(axis=1)>10).tolist();parts=g['completeComponents'];lookup={f:i for i,p in enumerate(parts) for f in p['faceIndices']};assert len(ids)==30 and all(lookup[i]==2 for i in ids)
 save(DOC/'exact-remaining-source-context.json.gz',{'completeOriginalFarFaceIds':ids,'completeOriginalFarFaces':tri[ids].tolist(),'farFacesAllInSourceMainComponent':2,'completeSourceMainComponentFaces':parts[2]['faceIndices'],'rawFullPairMaximumExtentM':float(dist.max()),'allRemainingCoverageFaces':[c for c in d['allOriginalPodiumFaceContexts'] if not c['groundProjectionCovered']],'allRemainingBuriedFaces':[c for c in d['allOriginalPodiumFaceContexts'] if c['minimum'] and c['minimum']['minimumGapM']<-.5],'sourceGeometryChanges':0,'qualification':'All30 far original faces are part of the4019-face complete mainbody, not unowned geometry. Their low5.629–8.810HKPD exterior role needs independent source/site evidence; raw12.63m is retained. Coverage witnesses6810/6814/6815 form one tiny0.0003384m² authentic-source seam, not an extent/coverage waiver.'})
 (DOC/'README.md').write_text('''# Yoho original pair authentic terrain recovery

Untouched original terrain from complete authenticated6-NW-10D and6-NW-15B
government packages yields2637 relevant positive-projection facets. All7731
original podium faces are measured continuously against this different source.
There are zero upward violations, upward minimum−0.144m. Current-ground failed
upward faces183/184 become ordinary-clear−0.000878/−0.000876m. No original model
or terrain geometry was edited. This provides a genuine source-TIN patch lead.

Three exact no-buffer projection diagnostics remain: sourcefaces6810/6814/6815
share a tiny0.0003384m² native seam; two of those are vertical walls with depths
−0.74888/−2.168m and exposed roof8.81HKPD above surrounding source terrain7.797.
The unchanged established narrow source-seam fill/complete physical checker may
investigate the tiny gap; no numeric limit was changed and no coverage credit
is granted here. All30 source faces beyond10m lie in the complete4019-face source
mainbody at5.629–8.810HKPD. Independent exterior/access/adjacent-source identity
remains necessary; raw12.630m and exact canopy/Block7 overlaps remain retained.

The first local runner assumed terrain receipt entries used`path`; they actually
use`name`. That KeyError was a local API/schema error before surface computation,
not acquisition corruption. The runner was corrected to bind each exact source
filename/hash and reused verified unchanged bytes. Source package provenance,
directory hashes and every used glTF/bin file are retained. Current-ground and
original source-TIN diagnostics remain distinct; no patch/physical/runtime/browser
acceptance or installation is claimed. Next work follows a paired original terrain
candidate, exact far-face role and neighbouring source evidence.
''')
 paths=[ROOT/p for p in d['inputHashes']]+[Path(__file__)]+[HERE/p for p in ['xl-yoho-original-pair-source-tin-context-20261010.py','xl-routed-cell-indexed-terrain-continuation.py','xl-second-pass.py','terrain_source_preflight.py','original_face_ground_crossing_v2_20261009.py','original_face_ground_crossing_20261009.py','original_degenerate_ground_context_20261009.py','yoho_eight_related_original_podium_identity_20261009.py']]+[base/'government-xl-yoho-original-podium-current-ground-20261010/diagnostic.json.gz',base/'government-xl-yoho-original-podium-current-ground-20261010/result.json',base/'government-xl-yoho-original-podium-strict-anchor-paths-20261010/result.json']
 s=importlib.util.spec_from_file_location('yoho_source_tin_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'complete-authenticated-original-pair-terrain-and-exact-mainbody-exterior-gaps-v1',paths,{'uids':['landsd/146396:0','landsd/231756:0'],'identityAccepted':False,'scriptFullAcceptancePassed':False,'completeOriginalPodiumFaces':7731,'authenticSourceTerrainFacets':2637,'wholeSourceTerrainSheets':['6-NW-10D','6-NW-15B'],'affectedUpwardFaces':0,'upwardContinuousMinimumGapM':summary['upwardContinuousMinimumGapM'],'remainingSourceSeamFaces':[6810,6814,6815],'remainingBuriedWallFaces':[6814,6815],'completeOriginalFarFaces':30,'requiresAIModelGeometry':False,'requiresHumanDecision':False,'remainingReason':'original-pair-source-bound-exterior-neighbour-identity-plus-narrow-source-seam-fullphysical','nextStep':'Use original TIN in a fresh paired physical candidate after explicit source-bound original far/foreign roles; preserve all source faces, four detached podium parts/143 Tower8 parts and every current actor.'})
if __name__=='__main__':main()
