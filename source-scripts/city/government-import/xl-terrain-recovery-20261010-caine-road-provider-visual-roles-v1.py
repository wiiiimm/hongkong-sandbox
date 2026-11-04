"""Freeze exact authored visual roles and every provider root/stream; no acceptance."""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from caine_road_original_named_projecting_details_v1_20261010 import WORLD,SOURCES,DETAILS
BASE=ROOT/'docs/astra-city/government-import';PHYSICAL=BASE/'government-xl-terrain-recovery-unnamed-268032-nested-original-pair-current-physical-v5-20261010';BATCH='xl-terrain-recovery-20261010-caine-road-provider-visual-roles-v1';DOC=BASE/BATCH
VISUAL=BASE/'xl-terrain-recovery-20261010-unnamed-268032-two-original-details-visual-v1';MOUNT=BASE/'xl-terrain-recovery-20261010-unnamed-268032-two-original-mount-diagnostics-v2'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();rows=read(PHYSICAL/'selection.json.gz')['rows'];assert {r['uid']:r['sourceSHA256'] for r in rows}==SOURCES;tri=[];streams={};assets=[]
 for r in rows:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];tri.append(decode_original_world_triangles(raw));streams[r['uid']]=source_stream_binding(raw);assets.append(p)
 assert digest(np.concatenate(tri).tobytes())==WORLD
 role=dict(contract='caine-road-pinned-open-back-cantilever-and-one-end-slanted-strip-visual-only-v1',sourceSHA256s=SOURCES,completeOriginalWorldSHA256=WORLD,roles=[dict(component=70,kind='original-ten-face-open-back-cantilever',completeOriginalFaces=DETAILS[70]),dict(component=202,kind='original-two-face-one-end-mounted-slanted-strip',completeOriginalFaces=DETAILS[202])]);save(DOC/'provider-role.json.gz',role)
 refs=[ref(p) for p in [Path(__file__),PHYSICAL/'selection.json.gz',*assets,VISUAL/'visual-context.json',VISUAL/'original-two-details-1800x900.png',VISUAL/'result.json',MOUNT/'diagnostic.json.gz',MOUNT/'result.json',HERE/'caine_road_original_named_projecting_details_v1_20261010.py',HERE/'test_caine_road_original_named_projecting_details_v1_actual_20261010.py',HERE/'xl_source_stream_binding_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']]
 provenance=dict(completeOriginalProviderRootAndStreams=streams,completeOriginalWorldSHA256=WORLD,sourceSHA256s=SOURCES,reviewedOriginalSourceVisualInterpretation='Exact original component70 is an authored ten-face open-back rooftop cantilever. Component202 is an authored two-face slanted projecting facade strip with a complete mounted end and separate opposite lower-corner finite-host witness. All free edges remain. This bounded visual interpretation was independently reviewed from full source context by root; it never supplies load-bearing contact, roots, bridge edges, closed-solid certification or clearance/foreign exemptions.',strictMountDistanceBandM=.1,allBodyRootsIndependentlyRequired=True,allCurrentPhysicalForeignProviderAndRuntimeGatesRequired=True,structuralCredit=False,geometryChanges=0,fullAcceptance=False,evidenceRefs=refs);save(DOC/'source-provider-provenance.json',provenance)
 spec=importlib.util.spec_from_file_location('f',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'pinned-provider-authored-two-visual-detail-roles-v1',[ROOT/r['path'] for r in refs]+[DOC/'provider-role.json.gz',DOC/'source-provider-provenance.json'],dict(uids=list(SOURCES),sourceSHA256s=SOURCES,completeOriginalWorldSHA256=WORLD,visualOnlyParts=[70,202],structuralCredit=False,fullAcceptance=False))
if __name__=='__main__':main()
