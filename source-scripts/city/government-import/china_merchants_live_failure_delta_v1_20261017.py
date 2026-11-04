"""Index current canonical foundation failures; preserve diagnostic-only component roles."""
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from foundation_source_face_attribution_adapter_v2_20261013 import attribute,canonical_pin
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-merchants-live-failure-delta-v1-20261017';DOC=BASE/BATCH
CAP=BASE/'government-xl-china-merchants-live-baseline-foundation-v1-20261017';RT=HERE/'local'/CAP.name/'runtime-geometry.json.gz'
SOURCE=BASE/'government-xl-china-merchants264206-saved-face-attribution-v1-20261013/source-face-attribution.json.gz'
def main():
 assert not DOC.exists();r=read(CAP/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 rt=read(RT);g=rt['rows'][0];saved=read(SOURCE);assert g['sourceSHA256']==saved['sourceSHA256'];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);assert t.shape==(19551,3,3);assert np.max(np.abs(t-np.asarray(saved['completeOriginalSourceFaceVerticesInOrdinalOrder'])))<1e-10
 b=read(CAP/'selection.json.gz')['rows'][0]['source']['building'];fn=module('china_delta_canonical',HERE/'xl-final-script-pass.py').foundation_context
 out=attribute(fn,t,ground,Polygon(b['rings'][0],b['rings'][1:]),saved['completeSavedDiagnosticComponentInventory'],expected_canonical_pin=canonical_pin(fn));assert out['canonicalFoundationMetrics']==read(CAP/'foundation.json')['foundation']
 old=set(saved['fullyBuriedSourceFaceIndices']);new=set(out['fullyBuriedSourceFaceIndices']);added=sorted(new-old);removed=sorted(old-new)
 summary=dict(uid=g['uid'],sourceSHA256=g['sourceSHA256'],historicalBuriedFaces=len(old),currentBuriedFaces=len(new),addedFaces=added,removedFaces=removed,addedUpwardFaces=sorted(set(added)&set(out['fullyBuriedUpwardSourceFaceIndices'])),addedFaceWorldVertices=t[added].tolist(),removedFaceWorldVertices=t[removed].tolist(),sourceGeometryChanges=0,installationApproved=False,qualification='Current installed terrain versus historical proposed-wrapper terrain; not a before/after installation regression claim. Component census remains diagnostic shared-vertex grouping, not certified architectural bodies.')
 save(DOC/'attribution.json.gz',out);save(DOC/'delta.json',summary)
 refs=[Path(__file__),SOURCE,RT,CAP/'result.json',CAP/'selection.json.gz',CAP/'foundation.json',HERE/'foundation_source_face_attribution_adapter_v1_20261013.py',HERE/'foundation_source_face_attribution_adapter_v2_20261013.py',HERE/'xl-final-script-pass.py']
 for p,h in rt['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=module('china_delta_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-canonical-source-face-failure-delta-v1',refs,dict(uids=[g['uid']],historicalBuriedFaces=len(old),currentBuriedFaces=len(new),addedFaces=added,removedFaces=removed,fullAcceptance=False,nextStep='Use current 598-face failure set and current installed terrain; obsolete Caine Road replacement contract requires a separate validated terrain proposal, not repointing its URL.'))
 print(dict(jobId=result['jobId'],addedFaces=added,removedFaces=removed),flush=True)
if __name__=='__main__':main()
