"""Complete untouched FBX/glTF comparison against pinned historical footprint.
No conversion, source acceptance inheritance, fitting or mesh edits.
"""
import importlib.util,json
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-lee-kong-145527-original-fbx-gltf-comparison-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
A=DOC.parent/'government-xl-lee-kong-145527-original-fbx-acquisition-v1-20261011'
V1=DOC.parent/'government-xl-lee-kong-145527-original-raw-fbx-inspection-v1-20261011'
V2=DOC.parent/'government-xl-lee-kong-145527-original-raw-fbx-inspection-v2-20261011'
ID=DOC.parent/'government-xl-lee-kong-independent-145527-0-current-identity-v1-20261011'
def projection(t):
 p=shapely.polygons(t[:,:,[0,2]]);return shapely.union_all(p[shapely.area(p)>0])
def main():
 assert not DOC.exists();inspection=read(V2/'inspection.json');assert inspection['supportedTranslationOnlyMetreEastNorthUpContract']and not inspection['unresolvedConventionReasons']
 source=ROOT/inspection['source']['sourcePath'];assert digest(source.read_bytes())==inspection['source']['sourceSHA256']=='da5a24c789e25b6af2494be9e8e7385f68ba5515a52f0772fa87b96564526a16'
 npz=HERE/'local'/V2.name/'complete-original-viewer-world.npz';arr=np.load(npz);fbx=arr['triangles'];assert digest(fbx.astype('<f8').tobytes())==inspection['completeViewerWorldTriangleSHA256'];assert len(fbx)==584
 row=read(ID/'selection.json.gz')['rows'][0];assert row['uid']=='landsd/145527:0';gltf_file=ROOT/row['candidate']['path'];raw=gltf_file.read_bytes();assert digest(raw)==row['sourceSHA256'];gltf=decode_original_world_triangles(raw)
 current=shapely.Polygon(row['source']['building']['rings'][0],row['source']['building']['rings'][1:]);a,b=projection(fbx),projection(gltf);missing=current.difference(a)
 # Whole face-stream order is retained, with a separately labelled projection
 # equality test. No fitted vertex correspondence or geometry normalization.
 same_shape=fbx.shape==gltf.shape
 out=dict(uid=row['uid'],originalFBXSourceSHA256=inspection['source']['sourceSHA256'],originalGLTFSourceSHA256=row['sourceSHA256'],completeFBXWorldSHA256=digest(fbx.astype('<f8').tobytes()),completeGLTFWorldSHA256=digest(gltf.astype('<f8').tobytes()),completeFBXFaces=len(fbx),completeGLTFFaces=len(gltf),completeFBXControlPoints=len(arr['viewerWorldControlPoints']),completeFBXUnusedControlPointIds=inspection['completeUnusedSourceControlPoints'],authoredCoordinateContract=inspection['coordinateDerivation'],capturedHistoricalCurrentForm=row['source']['building'],capturedHistoricalManifestSHA256=read(ID/'result.json')['manifestSHA256'],freshCurrentIdentityClaimed=False,
  completeOrderedWorldTrianglesEqual=bool(same_shape and np.array_equal(fbx,gltf)),orderedWorldMaximumCoordinateDifferenceM=float(np.max(np.abs(fbx-gltf)))if same_shape else None,completeProjectionEquals=bool(a.equals(b)),completeProjectionSymmetricDifferenceM2=a.symmetric_difference(b).area,
  capturedCurrentTargetAreaM2=current.area,completeFBXCoverageOfCapturedCurrentTarget=1-missing.area/current.area,completeGLTFCoverageOfCapturedCurrentTarget=current.intersection(b).area/current.area,FBXMissingCapturedCurrentTargetM2=missing.area,completeFBXMissingRegions=json.loads(shapely.to_geojson(missing)),FBXSourceInsideCapturedCurrentTarget=a.intersection(current).area/a.area,completeFBXExcessAreaM2=a.difference(current).area,
  untouchedFBXInspection=inspection,sourceFormatAcceptanceInherited=False,governmentGeometryChanges=0,sourceFacesOmitted=0,physicalAccepted=False,installationApproved=False,qualification='Independent complete original FBX double-control-point hierarchy/unit/pose interpretation and untouched glTF comparison. Footprints are the pinned historical diagnostic, not fresh provider acceptance. No fitting/triangulation/conversion or source threshold waiver.')
 save(DOC/'diagnostic.json.gz',out)
 refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',npz,gltf_file,source,ID/'result.json',ID/'selection.json.gz']
 for directory in [A,V1,V2]:refs.extend(p for p in directory.rglob('*')if p.is_file());refs.extend(p for p in (HERE/'local'/directory.name).rglob('*')if p.is_file())
 refs.extend(HERE/name for name in ['xl-lee-kong-145527-original-fbx-acquisition-v1-20261011.py','xl-lee-kong-145527-original-raw-fbx-inspection-v1-20261011.py','xl-lee-kong-145527-original-raw-fbx-inspection-v2-20261011.py'])
 (DOC/'README.md').write_text('Complete untouched official FBX compared against the pinned historical glTF/current footprint.\n\nFBX coverage: '+str(out['completeFBXCoverageOfCapturedCurrentTarget'])+'; projection symmetric difference: '+str(out['completeProjectionSymmetricDifferenceM2'])+' square metres. No geometry conversion or inherited source-format acceptance. Both parser attempts and exact acquisition/toolchain/control-point arrays are retained.\n')
 spec=importlib.util.spec_from_file_location('fbx_compare_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'unchanged-original-FBX-complete-coverage-comparison-no-inherited-acceptance',refs,dict(uid=row['uid'],uids=[row['uid']],completeOriginalFBXFaces=len(fbx),completeProjectionEquals=out['completeProjectionEquals'],completeFBXCoverageOfCapturedCurrentTarget=out['completeFBXCoverageOfCapturedCurrentTarget'],freshCurrentIdentityClaimed=False,installationApproved=False,newlyInstalled=0))
 print(json.dumps({k:out[k]for k in ['completeProjectionEquals','completeProjectionSymmetricDifferenceM2','completeFBXCoverageOfCapturedCurrentTarget','completeOrderedWorldTrianglesEqual','orderedWorldMaximumCoordinateDifferenceM']}),flush=True)
if __name__=='__main__':main()
