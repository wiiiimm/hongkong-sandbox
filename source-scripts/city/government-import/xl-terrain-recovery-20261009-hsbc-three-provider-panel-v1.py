"""Freeze named provider-authored HSBC mounted panel evidence; no acceptance."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from xl_source_stream_binding_20261009 import source_stream_binding
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='xl-terrain-recovery-20261009-hsbc-three-provider-panel-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-hsbc-three-retained-physical-v1-20261009'
SUPPORT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-hsbc-three-current-ordinary-support-v1'
CONTEXT=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-265848-three-current-complete-context-v2'
UID='landsd/265848:0';SOURCE='848eb61d88b19162d2166127f3c04c4f920f986c55106ffbb121b110ef0973cd'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();row=next(r for r in read(PHYSICAL/'selection.json.gz')['rows'] if r['uid']==UID);asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==SOURCE
 geom=HERE/'local'/PHYSICAL.name/'runtime-geometry.json.gz';g=next(r for r in read(geom)['rows'] if r['uid']==UID);tri=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 decoded=decode_original_world_triangles(raw);assert decoded.shape==tri.shape and np.max(np.abs(decoded-tri))<=1e-9
 graph=read(SUPPORT/'diagnostic.json.gz');assert graph['actors'][0]['uid']==UID and graph['actors'][0]['globalFaceRange']==[0,15336]
 assert graph['components'][29]['globalOriginalFaces']==list(range(10036,10041)) and graph['components'][29]['actorUID']==UID and graph['resolvedOriginalComponents']==list(range(29))+list(range(30,62))
 context=read(CONTEXT/'diagnostic.json.gz');assert context['sourceSHA256']==SOURCE and not context['continuousAffectedFaces'] and context['wholeSourceUncoveredFaces']==0
 stream=source_stream_binding(raw)
 role=dict(role='original-provider-mounted-HSBC-visual-panel',uid=UID,sourceSHA256=SOURCE,component=29,originalFaces=list(range(10036,10041)),rootedBodyComponent=0,rootedBodyContactFaces=[4811,7553,7554,9300,9301,9302,9303,13212,13213,13214],independentlyVerifiedPackedWorldRoundoffM=float(np.max(np.abs(decoded-tri))),completeSourceOriginalFaceCount=15336,providerRootStreams=stream,completePodiumOriginalWorldTrianglesSHA256=digest(tri.tobytes()),strictIndependentSupport=ref(SUPPORT/'diagnostic.json.gz'),currentWholeFacetContext=ref(CONTEXT/'diagnostic.json.gz'),qualification='Named unchanged government-authored mounted visual panel. Two exact distinct top corner attachments to independently rooted original body; no ground root/load bearing credit. Every other source component must root independently without this panel. Original point-only attachment failure retained. No source geometry edits.')
 save(DOC/'expected-role.json',role)
 refs=[ref(p) for p in [Path(__file__),asset,geom,SUPPORT/'diagnostic.json.gz',SUPPORT/'result.json',SUPPORT/'neon-sync.json',CONTEXT/'diagnostic.json.gz',PHYSICAL/'selection.json.gz',PHYSICAL/'owned-source-identity-contact-265848-0.json',ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-hsbc-original-panel-context-v1/diagnostic.json.gz',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']]
 save(DOC/'original-source-provenance.json',dict(uid=UID,sourceSHA256=SOURCE,originalPackedStreams=stream,originalFaces=list(range(10036,10041)),providerBuildingCSUID=row['source']['building']['buildingCSUID'],originalRole=ref(DOC/'expected-role.json'),evidenceRefs=refs,sourceGeometryChanges=0,installationApproved=False))
 print(DOC)
if __name__=='__main__':main()
