"""Freeze complete source-authored visual detail provenance; no acceptance."""
import importlib.util
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from ko_fung_original_mounted_facade_roles_v3_20261010 import SOURCES,canonical
BATCH='xl-terrain-recovery-20261010-ko-fung-provider-mounted-roles-v1';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH
PHYSICAL=BASE/'government-xl-terrain-recovery-ko-fung-original-pair-current-physical-v3-20261010';SUPPORT=BASE/'xl-terrain-recovery-20261010-ko-fung-original-current-support-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();selected=read(PHYSICAL/'selection.json.gz');graph=read(SUPPORT/'diagnostic.json.gz');streams={};parts=[];refs=[ref(p) for p in [Path(__file__),PHYSICAL/'selection.json.gz',PHYSICAL/'result.json',SUPPORT/'diagnostic.json.gz',SUPPORT/'result.json',BASE/'xl-terrain-recovery-20261010-ko-fung-mounted-visual-v1/original-detail-context-1800x1440.png',BASE/'xl-terrain-recovery-20261010-ko-fung-open-facade-boundaries-v1/diagnostic.json.gz',BASE/'xl-terrain-recovery-20261010-ko-fung-mounted-original-context-v1/diagnostic.json.gz',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']]
 for row in selected['rows']:
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCES[row['uid']];streams[row['uid']]=source_stream_binding(raw);parts.append(decode_original_world_triangles(raw));refs.append(ref(asset))
 tri=np.concatenate(parts);assert digest(tri.tobytes())==graph['binding']['completeOriginalWorldTrianglesSHA256'];rooted=set(graph['resolvedOriginalComponents']);visual=sorted(set(range(len(graph['components'])))-rooted);assert len(visual)==119 and graph['components'][598]['globalOriginalFaces']==[13402]
 role=dict(contract='ko-fung-complete-original-mounted-facade-role-v3',sources=SOURCES,allVisualComponents=visual,openBackComponents=[k for k in visual if k!=598],slantedSeamComponent=598,seamRootedBodyComponent=0,completeOriginalComponents=666,completeOriginalFaces=15561,providerRootAndStreams=streams,providerRootAndStreamsSHA256=canonical(streams),completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),strictIndependentOriginalGraph=ref(SUPPORT/'diagnostic.json.gz'),allNamedVisualOriginalComponents=[dict(component=k,actorUID=graph['components'][k]['actorUID'],completeOriginalFaces=graph['components'][k]['globalOriginalFaces'],completeOriginalVerticesSHA256=digest(tri[graph['components'][k]['globalOriginalFaces']].tobytes())) for k in visual],qualification='Named provider-authored open-back facade projections and one original slanted hanging triangular seam. Complete source vertices/indices/root/NORMAL/COLOR/hierarchy retained. Finite existing contact-band mounts or exact distinct top-edge point mounts are visual-only: no ground root, load-bearing edge, body bridge or synthetic back surface. Complete current identity/source/foundation/foreign/runtime/browser remain mandatory.')
 save(DOC/'expected-role.json',role);save(DOC/'original-source-provenance.json',dict(uids=list(SOURCES),sources=SOURCES,providerRootAndStreams=streams,exactSourceBuildingCSUIDs={r['uid']:r['source']['building']['buildingCSUID'] for r in selected['rows']},sourceBoundRole=ref(DOC/'expected-role.json'),evidenceRefs=refs,fullAcceptance=False,installationApproved=False))
 spec=importlib.util.spec_from_file_location('ko_fung_provider_role_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'named-complete-original-ko-fung-mounted-facade-provenance-v1',[ROOT/r['path'] for r in refs]+[DOC/'expected-role.json',DOC/'original-source-provenance.json'],dict(uids=list(SOURCES),completeOriginalFaces=15561,completeOriginalComponents=666,namedVisualComponents=119,fullAcceptance=False,structuralRootCredit=False))
 print(DOC)
if __name__=='__main__':main()
