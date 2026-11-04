"""Fence the complete 22 original component interface census; no terrain roots."""
from pathlib import Path
from run import ROOT,HERE,read
from lei_tung_lower_platform_current_bound_identity_20261010 import DOC as INPUT,UID,PLATFORM,module
BASE=INPUT.parent;GRAPH=BASE/'government-xl-lei-tung-two-original-complete-component-interfaces-20261010';BATCH='government-xl-lei-tung-two-original-complete-interface-checkpoint-20261010'
def main():
 d=read(GRAPH/'diagnostic.json.gz');assert d['completeOriginalComponentCounts']==[19,3] and len(d['completeOriginalComponentNodes'])==22 and not d['notConnectedToUpperMain'];assert d['groundAnchorAccepted'] is False and d['physicalAccepted'] is False
 (GRAPH/'README.md').write_text('All874 commercial254604 original faces/19parts and432 platform126434 faces/3parts retained. Complete exact pairwise component census finds37 positive-dimensional component edges; all22 parts connect through actual original lines/areas to uppermain5/9 and original lowerplatform. Point touches remain separate. This source-only graph does not establish a drawn-ground root or structural certification. Complete current original ground-interface/face clearance/foundation/native/foreign/runtime checks remain required. Zero source edits or installations.\n')
 refs=[Path(__file__),HERE/'xl-lei-tung-two-original-complete-component-interfaces-20261010.py',*[ROOT/p for p in d['inputHashes']],*[p for p in GRAPH.rglob('*') if p.is_file()]]
 r=module('lei_tung_complete_interface_fence','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete22-original-source-component-positive-interface-graph-v1',refs,{'uids':[UID,PLATFORM],'identityAccepted':False,'physicalAccepted':False,'scriptFullAcceptancePassed':False,'completeOriginalFaces':[874,432],'completeOriginalComponents':[19,3],'positiveDimensionalComponentEdges':37,'sourceContactConnectedParts':22,'drawnTerrainRootAccepted':False,'remainingReason':'fresh-complete-original-drawn-ground-root-clearance-foundation-foreign-runtime-gates'});print(r['jobId'],flush=True)
if __name__=='__main__':main()
