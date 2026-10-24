"""Four-coordinate analysis against unchanged current terrain; no acceptance waiver."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_grade_partition_v1 import partition_triangle,area_vector
BASE=ROOT/'docs/astra-city/government-import';B='government-xl-china-merchants-current-above-base-v1-20261023';D=BASE/B;UID='landsd/264206:0'
N=dict(runtime='government-xl-china-merchants-basement-current-capture-v1-20261023',attributes='government-xl-china-merchants-basement-current-attributes-v1-20261023',context='government-xl-basement-burial-context-v1-20261023')
assert not D.exists();refs=[Path(__file__),HERE/'original_grade_partition_v1.py',HERE/'exact_packed_world_geometry_20261009.py'];pins={}
for k,n in N.items():
 _,pins[k]=authenticate(BASE/n);refs.append(BASE/n/'result.json')
def take(k,p):
 assert digest(p.read_bytes())==pins[k][str(p.relative_to(ROOT))];refs.append(p);return read(p)
selection=take('runtime',BASE/N['runtime']/'selection.json.gz');assert len(selection['rows'])==1;r=selection['rows'][0];assert r['uid']==UID
context=next(r for r in take('context',BASE/N['context']/'summary.json')['rows']if r['uid']==UID);assert context['sourceSHA256']==r['sourceSHA256'];base=context['officialBaseHeightHKPD'];assert base==r['source']['building']['baseHeightHKPD']==4
geometry=next(r for r in take('runtime',HERE/'local'/N['runtime']/'runtime-geometry.json.gz')['rows']if r['uid']==UID)
attributes=take('attributes',BASE/N['attributes']/'attributes.json.gz');assert attributes['startEndAllInputsVerified'];attr=next(r for r in attributes['rows']if r['uid']==UID)
assert attr['sourceSHA256']==geometry['sourceSHA256']==r['sourceSHA256'];asset=ROOT/r['candidate']['path'];blob=asset.read_bytes();assert digest(blob)==r['sourceSHA256'];refs.append(asset)
index=np.asarray(attr['completeOriginalIndex']).reshape(-1,3);worlds={'original':decode_original_world_triangles(blob)}
for mode,field in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(attr[field],dtype='<f8').reshape(-1,3)[index]
assert np.array_equal(worlds['literal'],np.asarray(geometry['position']).reshape(-1,3)[np.asarray(geometry['index']).reshape(-1,3)])
ground=np.asarray(geometry['drawnGroundGeometry']).reshape(-1,3,3);form=r['source']['building'];polygon=Polygon(form['rings'][0],form['rings'][1:]);final=module('current_above_base_foundation',HERE/'xl-final-script-pass.py');rows=[]
for mode,tri in worlds.items():
 assert len(tri)==r['triangles'];above=[];below=[];degenerate=[];facetMap=[]
 for face_id,face in enumerate(tri):
  high,low=partition_triangle(face,base);start=len(above);above.extend(high);below.extend(low)
  if not any(area_vector([tuple(tuple(__import__('fractions').Fraction.from_float(float(x))for x in p)for p in face)])):degenerate.append(face_id)
  facetMap.append(dict(originalFace=face_id,abovePieceStart=start,abovePieceCount=len(high),belowPieceCount=len(low)))
 high=np.asarray(above,dtype='<f8');raw=final.foundation_context(tri,ground,polygon);ab=final.foundation_context(high,ground,polygon)
 report=dict(uid=UID,mode=mode,sourceSHA256=r['sourceSHA256'],originalWorldSHA256=digest(tri.astype('<f8').tobytes()),sourceFaces=len(tri),recordedBaseHeight=base,aboveBaseAnalysisPieces=len(high),belowBaseAnalysisPieces=len(below),zeroAreaOriginalFaces=degenerate,aboveAnalysisHasBelowBasePoints=bool(np.any(high[:,:,1]<base)),rawWholeOriginalFoundation=raw,aboveBaseSampledFoundation=ab,aboveBaseSampledClearanceCandidate=ab['completeTerrainTriangles']==ab['triangles']and ab['fullyBuriedTriangles']==ab['fullyBuriedUpwardTriangles']==0 and ab['minimumGapM']>=-.5,physicalAcceptance=False,installationApproved=False)
 save(D/(mode+'.json'),report);save(D/(mode+'-facet-map.json.gz'),dict(sourceSHA256=r['sourceSHA256'],originalWorldSHA256=report['originalWorldSHA256'],originalToAnalysisFacets=facetMap,qualification='Exact original-facet analysis partition; no source or runtime geometry changes. Degenerate original facets remain accounted; check below-base-point indicator before interpreting above-base sample minima.'))
 rows.append(report);print(dict(mode=mode,aboveBaseMinimumGap=ab['minimumGapM'],aboveBaseBuried=ab['fullyBuriedTriangles'],rawBuried=raw['fullyBuriedTriangles'],candidate=report['aboveBaseSampledClearanceCandidate'],degenerateOriginals=len(degenerate)),flush=True)
manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.extend([manifest,HERE/'xl-final-script-pass.py'])
summary=dict(uids=[UID],sourceSHA256=r['sourceSHA256'],currentManifestSHA256=selection['manifestSHA256'],officialBasementMetadata=context['officialStructureRecords'],rows=rows,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,newlyInstalled=0,qualification='Four coordinate representations sampled against the complete unchanged current drawn ground after exact analysis-only partition at official BaseHeight4. This neither approves a basement role nor replaces full-original/source-identity/continuous/support/current-neighbour/collision/visual acceptance. Raw full-original burial/clearance failures remain. No production files, source geometry, source pose, clamp, threshold or acceptance policy changes.')
save(D/'summary.json',summary);module('china_current_above_base_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(B,'current-four-coordinate-above-base-diagnostic',refs,summary)
