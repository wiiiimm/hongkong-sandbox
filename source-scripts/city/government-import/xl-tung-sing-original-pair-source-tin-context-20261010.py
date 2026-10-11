"""Recover authenticated original sheet terrain and test all original Tung Sing/commercial faces."""
import importlib.util,json
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from terrain_source_preflight import SourceSheetIndex
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from tung_sing_current_bound_identity_20261010 import DOC as INPUT,verify_receipt
BATCH='government-xl-tung-sing-original-pair-source-tin-context-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH;LOCAL=HERE/'local'/BATCH
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 assert not DOC.exists();verify_receipt(read(INPUT/'result.json'));capture=read(INPUT/'current-inputs.json.gz');row=read(INPUT/'selection.json.gz')['rows'][0];praw=(ROOT/capture['podiumOriginalPath']).read_bytes();podium=decode_original_world_triangles(praw);tower=decode_original_world_triangles((ROOT/row['candidate']['path']).read_bytes());p=np.concatenate([tower,podium]);tri=p;lo,hi=tri.min(axis=(0,1)),tri.max(axis=(0,1));bounds=[lo.tolist(),hi.tolist()];index=SourceSheetIndex(read(ROOT/'source-scripts/city/landmark-acquisition/index.json'));sheets=sorted({s['sheet'] for s in index.covering_sheets(bounds)});recover=module('tung_sing_actual_provider_tin','xl-routed-cell-indexed-terrain-continuation.py');second=module('tung_sing_unchanged_tin_decode','xl-second-pass.py');fragments=[];receipts=[];hashes={}
 for sheet in sheets:
  folder,receipt=recover.terrain_sheet(sheet,LOCAL);receipts.append(receipt)
  for f in sorted((folder/'terrain').rglob('*.gltf')):fragments.append(second.terrain_triangles(f))
  hashes.update({str((folder/'terrain'/q['name']).relative_to(ROOT)):q['sha256'] for q in receipt['terrainFiles']});hashes[str((folder/'original/download.json').relative_to(ROOT))]=digest((folder/'original/download.json').read_bytes());hashes[str((folder/'directory/result.json').relative_to(ROOT))]=digest((folder/'directory/result.json').read_bytes())
 ground=np.concatenate(fragments);keep=(ground[:,:,0].max(axis=1)>=lo[0]-1)&(ground[:,:,0].min(axis=1)<=hi[0]+1)&(ground[:,:,2].max(axis=1)>=lo[2]-1)&(ground[:,:,2].min(axis=1)<=hi[2]+1);ground=ground[keep];poly=shapely.polygons(ground[:,:,[0,2]]);good=shapely.area(poly)>1e-10;ground,poly=ground[good],poly[good];tree=shapely.STRtree(poly);n=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);length=np.linalg.norm(n,axis=1);ratio=np.divide(n[:,1],length,out=np.zeros(len(p)),where=length>0);contexts=[]
 for i,t in enumerate(p):
  c=face_ground_context(t,ground,poly,tree) if length[i]>0 else degenerate_ground_context(t,ground,poly,tree);contexts.append(dict(c,sourceFace=i,normalYRatio=float(ratio[i]) if length[i]>0 else None))
  if i%500==0:save(DOC/'progress.json',{'facesChecked':i,'completeOriginalPairFaces':len(p),'sourceTerrainFaces':len(ground)});print({'facesChecked':i,'completeOriginalPairFaces':len(p),'sourceTerrainFaces':len(ground)},flush=True)
 affected=[i for i,c in enumerate(contexts) if c['minimum'] and c['minimum']['minimumGapM']<-.5];upward=[i for i in range(len(p)) if ratio[i]>.25 and contexts[i]['minimum']];summary={'completeOriginalPairFaces':len(p),'authenticatedSourceTerrainFaces':len(ground),'completeOriginalSheets':sheets,'uncoveredFaces':sum(not c['groundProjectionCovered'] for c in contexts),'affectedFaces':len(affected),'affectedUpwardFaces':len(set(affected)&set(upward)),'upwardContinuousMinimumGapM':min(contexts[i]['minimum']['minimumGapM'] for i in upward),'completeOriginalTowerFaces':len(tower),'completeOriginalCommercialFaces':len(podium),'sourceGeometryChanges':0,'terrainGeometryChanges':0,'physicalAccepted':False}
 save(DOC/'complete-original-source-tin.json.gz',{'position':ground.reshape(-1).tolist(),'index':list(range(len(ground)*3)),'worldTriangleSHA256':digest(ground.astype('<f8').tobytes()),'completeSourceReceipts':receipts,'sourceFileHashes':hashes});save(DOC/'diagnostic.json.gz',{'summary':summary,'allOriginalPairFaceContexts':contexts,'completeSourceTerrainReceipts':receipts,'inputHashes':hashes|{capture['podiumOriginalPath']:digest(praw),row['candidate']['path']:digest((ROOT/row['candidate']['path']).read_bytes())},'qualification':'Complete unchanged original11445-face Tung Sing and432-face commercial source versus authenticated whole source sheets, no terrain edits or model changes. This source-only TIN diagnosis is distinct from actual drawn terrain and is not patch/foundation/foreign/runtime/browser acceptance.'});save(DOC/'summary.json',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
