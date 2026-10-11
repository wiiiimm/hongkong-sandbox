"""Complete original P/T parts and finite interfaces; no rooted/support credit."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from exact_mesh_components import face_components
from xl_source_stream_binding_20261009 import source_stream_binding
BATCH='government-xl-one-peking-two-complete-original-component-contacts-v1-20261010'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;SOURCE=BASE/'government-xl-one-peking-hullett-complete-original-boundary-context-v1-20261010'
UIDS=['landsd/233985:0','landsd/240487:0']
def main():
 assert not DOC.exists();context=read(SOURCE/'diagnostic.json.gz');rows={r['uid']:r for r in context['sources']};originals={};actors=[];assets=[]
 for uid in UIDS:
  row=rows[uid];path=ROOT/row['source']['path'];raw=path.read_bytes();assert digest(raw)==row['source']['sha256'];a=decode_original_world_triangles(raw)
  assert len(a)==row['completeFaces'] and digest(a.astype('<f8').tobytes())==row['worldTrianglesSHA256'] and np.isfinite(a).all()
  parts=[list(map(int,p)) for p in face_components(a)];assert sorted(f for part in parts for f in part)==list(range(len(a)))
  originals[uid]=a;assets.append(path);actors.append(dict(uid=uid,sourceSHA256=digest(raw),completeFaces=len(a),worldTrianglesSHA256=digest(a.astype('<f8').tobytes()),completeOriginalParts=parts,completeProviderStreams=source_stream_binding(raw),bounds=[a.min((0,1)).tolist(),a.max((0,1)).tolist()]))
 p,t=[originals[u] for u in UIDS];contacts=exact_component_contacts(p,range(len(p)),t,range(len(t)));assert contacts['allPairsExamined']
 out=dict(uids=UIDS,actors=actors,completeOriginalFaces=len(p)+len(t),completePairContacts=contacts,sourceGeometryChanges=0,physicalSupportAccepted=False,identityAccepted=False,installationApproved=False,qualification='All original parts and every finite original P/T interface retained. Positive interfaces alone give no root, load-bearing or foreign-collision credit. Every part still needs complete actual current ground/host support and source/literal physical checks.')
 save(DOC/'diagnostic.json.gz',out)
 s=importlib.util.spec_from_file_location('peking_pair_contact_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 refs=[Path(__file__),SOURCE/'diagnostic.json.gz',SOURCE/'result.json',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_mesh_components.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py',*assets]
 r=m.freeze(BATCH,'complete-two-original-component-and-finite-interface-source-only-diagnostic-v1',refs,out)
 print(json.dumps(dict(jobId=r['jobId'],parts={a['uid']:len(a['completeOriginalParts']) for a in actors},positiveInterfaces=sum(c['dimension']>0 for c in contacts['contacts']),allPairsExamined=True)),flush=True)
if __name__=='__main__':main()
