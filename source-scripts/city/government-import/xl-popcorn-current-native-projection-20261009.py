"""Whole installed Grandiose originals versus whole PopCorn originals.

Diagnostic only. Strict disjointness permits a subsequent exact parent-region
protection proof; it supplies no existing support or installation waiver.
"""
import importlib.util
from pathlib import Path
import numpy as np
import shapely
from run import ROOT, HERE, read, save, digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BATCH='government-xl-popcorn-current-native-projection-20261009'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
CAT=ROOT/'3d-viewer/city/data/official-models/government-xl-supported-towers-second-20260914/catalogue.json'
INPUT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-current-complete-face-ground-20261009/exact-current-renderer-face-inputs.json.gz'
UIDS={'landsd/81008:0','landsd/81678:0'}

def main():
 assert not (DOC/'result.json').exists()
 source=[]
 for row in read(INPUT)['rows']:
  tri=np.asarray(row['position'],dtype='<f8').reshape(-1,3,3)
  assert len(tri)==row['triangles'] and digest(tri.tobytes())==row['worldTriangleSHA256']
  source.append(tri)
 source=np.concatenate(source)
 projection=shapely.union_all([shapely.MultiPoint(t[:,[0,2]]).convex_hull for t in source])
 rows=[];paths=[Path(__file__),CAT,INPUT,ROOT/'3d-viewer/city/data/manifest.json',HERE/'exact_packed_world_geometry_20261009.py']
 catalog=read(CAT);entries=[m for m in catalog['models'] if m['uid'] in UIDS]
 assert {e['uid'] for e in entries}==UIDS and len(entries)==2
 for entry in entries:
  asset=CAT.parent/entry['asset'];raw=asset.read_bytes();assert digest(raw)==entry['sha256']
  tri=decode_original_world_triangles(raw);assert len(tri)==entry['triangles']
  assert np.allclose(np.array([tri.min(axis=(0,1)),tri.max(axis=(0,1))]),entry['worldBounds'],rtol=0,atol=1e-7)
  native=shapely.union_all([shapely.MultiPoint(t[:,[0,2]]).convex_hull for t in tri])
  rows.append({'uid':entry['uid'],'label':entry.get('label'),'sourceSHA256':digest(raw),
   'wholeOriginalFaces':len(tri),'decodedWorldTrianglesSHA256':digest(tri.astype('<f8').tobytes()),
   'nativeProjectionWKB_SHA256':digest(native.wkb),'strictlyDisjoint':bool(native.disjoint(projection)),
   'distanceM':float(native.distance(projection)),'intersectionAreaM2':float(native.intersection(projection).area),
   'parentProtectionAccepted':False,'supportAccepted':False,'installationApproved':False})
  paths.append(asset)
 save(DOC/'whole-native-projection.json',{'wholeNewOriginalSourceFaces':len(source),'sourceProjectionWKB_SHA256':digest(projection.wkb),'rows':rows,'diagnosticOnly':True})
 spec=importlib.util.spec_from_file_location('popcorn_native_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-original-current-native-projection-v1',paths,
  {'uids':sorted(UIDS),'rows':rows,'humanStatus':'held-unknown','requiresHumanDecision':False,
   'requiresMoreComputeOrSourceEvidence':True,'requiresAIModelGeometry':False,
   'remainingReason':'exact-whole-native-projection-parent-protection-and-fresh-current-native-checks-pending',
   'nextStep':'If disjoint, prove complete protected-region coverage and retain unchanged existing parent terrain; replay current foundations/neighbours/runtime. Existing sampled support failures remain explicit and grant no new support credit.'})
 print(rows,flush=True)

if __name__=='__main__':main()
