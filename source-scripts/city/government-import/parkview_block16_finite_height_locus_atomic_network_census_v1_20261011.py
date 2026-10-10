"""DRAFT exact all-pair arrangement of frozen174 locus segments; no candidate."""
import json
from fractions import Fraction as F
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_finite_3d_segment_network_v1_20261011 import network
B=ROOT/'docs/astra-city/government-import';OLD=B/'government-xl-parkview-block16-finite-source-current-height-locus-census-v1-20261011';DOC=B/'government-xl-parkview-block16-finite-height-locus-atomic-network-census-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def strings(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:strings(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [strings(v)for v in x]
 return x

def main():
 assert not DOC.exists();assert read(OLD/'result.json')['currentAcceptance']is False
 refs=[ref(p)for p in [Path(__file__),OLD/'diagnostic.json.gz',OLD/'result.json',HERE/'exact_finite_3d_segment_network_v1_20261011.py',HERE/'test_exact_finite_3d_segment_network_v1_20261011.py']];d=read(OLD/'diagnostic.json.gz');assert d['completeSourceCurrentProjectedAABBPairs']==3008 and d['counts']['finite-positive-3D-equal-height-segment']==174
 indices=[i for i,r in enumerate(d['rows'])if r['proof']['classification']=='finite-positive-3D-equal-height-segment'];segments=[d['rows'][i]['proof']['exactSegment']for i in indices];assert len(segments)==174
 proof=network(segments);assert proof['completeSegmentPairCount']==15051
 for r in refs:assert ref(ROOT/r['path'])==r
 save(DOC/'diagnostic.json.gz',dict(uid='landsd/256319:0',sourceOnly=True,currentAcceptance=False,nativeReacceptance=False,terrainProposalWritten=False,sourceGeometryChanges=0,terrainChanges=0,originalLocusRowIndices=indices,exactAtomicNetwork=strings(proof),evidenceRefs=refs,qualification='Complete exact3D arrangement of existing174 equality segments including interior crossings and positivecollinear overlaps, all15051pairs no truncation. All original pair incidences preserved. Point incidence here is graph context only, never positive structural/contact/root bridge credit. A networkcycle alone is not a sourcepiece domain: outside retainedside, full source/internal/F32 topology/coverage/overlap, terrain clearance and affected17/native/foreign/source support obligations remain mandatory. No budget/domain expansion or candidate.'))
 print(json.dumps(dict(segments=174,completePairs=15051,atomicEdges=len(proof['atomicEdges']),components=len(proof['components']),cycleRank=proof['cycleRank'],positiveOverlapPairs=proof['positiveOverlapPairs'],terrainProposalWritten=False,currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
