"""Freeze current Lippo P/T inputs; physical and installation checks pending."""
import json,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from lippo_pair_current_identity_v2_20261011 import UIDS
from lippo_current_bound_six_roof_identity_v4_20261011 import DOC as INPUT,module
from lippo_three_original_current_inventory_20261010 import catalogue_inventory
from lippo_disjoint_current_parent_cells_v1_20261011 import proposed_cells,PARENT_URL,extent,complete_geometry_containment
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from lippo_actual_render_float32_diagnostic_20261010 import reconstruct
import numpy as np
BATCH='government-xl-lippo-two-original-current-physical-inputs-v2-20261011';DOC=INPUT.parent/BATCH
TOWER=INPUT.parent/'government-xl-lippo-tower-current-complete-original-identity-diagnostic-v2-20261011'
PROMOTION=INPUT.parent/'government-xl-lippo-current-bound-six-roof-promotion-v4-20261011'
def verify_receipt(doc):
 receipt=read(doc/'result.json')
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256'],r['path']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 return receipt
def main():
 assert not DOC.exists()
 claim=reservations.claim('lippo-two-original-inputs-'+str(uuid.uuid4()),['building:'+u for u in sorted(UIDS)],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  before=(ROOT/'3d-viewer/city/data/manifest.json').read_bytes();capture=read(INPUT/'current-inputs.json.gz');inventory=catalogue_inventory(before)
  assert digest(before)==capture['manifestSHA256'] and inventory==capture['catalogueInventory']
  source=read(INPUT/'selection.json.gz');rows=[r for r in source['rows'] if r['uid'] in UIDS];assert len(rows)==2
  t=read(TOWER/'selection.json.gz');assert next(r for r in rows if r['uid']=='landsd/239465:0')==t['rows'][0] and t['manifestSHA256']==digest(before)
  receipts=[verify_receipt(p) for p in [INPUT,TOWER,PROMOTION]]
  identities=[read(PROMOTION/'identity.json'),read(TOWER/'identity.json')];assert {p['uid'] for p in identities}==UIDS and all(p['passed'] and not p['reasons'] for p in identities)
  contexts=read(INPUT/'context.json.gz')['rows']+read(TOWER/'context.json.gz')['rows'];assert len(contexts)==2 and {c['uid'] for c in contexts}==UIDS
  for r in rows:
   assert r['currentReview'] is None and digest((ROOT/r['candidate']['path']).read_bytes())==r['sourceSHA256']
   with connect() as c:
    c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,r['native']['cacheKey'])).fetchone()==(r['native']['resultSha'],)
  parent=read(ROOT/'3d-viewer'/PARENT_URL);cells=proposed_cells(rows,parent)
  literal=read(INPUT/'literal-production-geometry.json.gz');render=read(INPUT/'actual-render-attribute-geometry.json.gz')
  streams,pins=reconstruct(render,literal)
  representations={kind:{u:t for u,t in actors.items() if u in UIDS} for kind,actors in streams.items()}
  representations['completeOriginal']={r['uid']:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in rows}
  representations['literalWorldFloat64']={r['uid']:np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index'],dtype=np.int64).reshape(-1,3)] for r in literal['rows'] if r['uid'] in UIDS}
  containment=complete_geometry_containment(rows,parent,representations)
  save(DOC/'check-selection.json.gz',dict(rows=rows,manifestSHA256=digest(before),nativeRun=NATIVE_RUN,batch=BATCH))
  save(DOC/'context.json.gz',dict(rows=contexts));save(DOC/'prior-identities.json',dict(rows=identities))
  save(DOC/'proposed-disjoint-parent-region.json',dict(parentURL=PARENT_URL,parentSHA256=digest((ROOT/'3d-viewer'/PARENT_URL).read_bytes()),cells=cells,bounds=extent(cells,parent),existingChildren=len(parent['patches']),modelGeometryChanges=0,terrainAccepted=False,physicalAccepted=False,publication=False))
  save(DOC/'complete-original-literal-and-two-f32-core-containment.json',containment)
  assert (ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==before and catalogue_inventory(before)==inventory
  refs=[Path(__file__),HERE/'lippo_pair_current_identity_v2_20261011.py',HERE/'lippo_disjoint_current_parent_cells_v1_20261011.py',HERE/'test_lippo_disjoint_current_parent_cells_v1_20261011.py',ROOT/'3d-viewer'/PARENT_URL]
  refs += [p/'result.json' for p in [INPUT,TOWER,PROMOTION]]
  refs += [INPUT/'literal-production-geometry.json.gz',INPUT/'actual-render-attribute-geometry.json.gz',HERE/'lippo_actual_render_float32_diagnostic_20261010.py',HERE/'exact_packed_world_geometry_20261009.py']
  result=module('lippo_pair_input_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-current-physical-inputs-v2',refs,dict(uids=sorted(UIDS),manifestSHA256=digest(before),completeOriginalFaces=sum(r['triangles'] for r in rows),bothUniqueNativeMembershipsVerified=True,priorIdentityJobs=[r['jobId'] for r in receipts],sourceGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalAccepted=False,installationApproved=False,currentHeldReason='full-source-terrain-neighbour-native-runtime-support-required',qualification='Source-bound candidate input only. Named six-roof podium identity plus independent ordinary tower identity; Silvercord and every other current actor remain foreign physical actors. Reduced terrain padding preserves complete source/core and full transition at reduced edge; numerical checks pending.'))
  print(json.dumps(dict(jobId=result['jobId'],manifestSHA256=digest(before),physicalAccepted=False)),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
