"""UNEXECUTED ROOT bounded saved891 adapter equivalence; no mask repartition.

Proposed external30s timeout. Reads only the completed one-face143 nomination;
no full actor/source decode, constructor, current DB or lease.
"""
from pathlib import Path
from fractions import Fraction as F
import argparse,gzip,hashlib,json
import numpy as np
from polyu_v3_computed_outside_enclosure_adapter_draft_20261014 import affected_outside

ROOT=Path(__file__).resolve().parents[3]
PROPOSAL=ROOT/'docs/astra-city/government-import/government-xl-polyu-five-eligible-current-parent-nomination-v3-20261014-proposal'


def check(q):
    p=ROOT/q['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==q['sha256'];return p


def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw)if p.suffix=='.gz'else raw)


def audit():
    pins=read(PROPOSAL/'draft-pins.json')
    for q in pins['codeRefs']+pins['inputRefs']:check(q)
    source=read(check(pins['saved891PartitionRef']));nominee=read(check(pins['saved891EnclosureRef']))
    assert source['complete']and source['face']==891 and nominee['complete']and len(nominee['regions'])==143
    pieces,account=affected_outside(source['exactIdealPartition'],source['sourceFaceLineageVerbatim']['exactProposedPoints'],{})
    expected=[t for r in nominee['regions']for t in r['triangles']]
    assert len(pieces)==len(expected)
    for got,wanted in zip(pieces,expected):
        assert got['exactOwnPlanePoints']==[tuple(F(v)for v in p)for p in wanted['idealSourcePlanePoints']]
        assert np.asarray(got['packedPieceTriplet'],dtype='<f8').tobytes()==np.asarray(wanted['packedPieceTriplet'],dtype='<f8').tobytes()
    assert len(account['completeComputedOutsidePolygonAccounting'])==143
    for got,wanted in zip(account['completeComputedOutsidePolygonAccounting'],nominee['regions']):
        assert got['exactHullExpansionAreaM2']==F(wanted['exactHullExpansionAreaM2'])
        assert got['exactFloat32CellEnclosingHull']==[tuple(F(v)for v in p)for p in wanted['exactFloat32CellEnclosingHull']]
    for q in pins['codeRefs']+pins['inputRefs']:check(q)
    return dict(passed=True,outsideRegions=143,packedPieces=len(pieces),
        orderedPackedSHA256=hashlib.sha256(np.asarray([t['packedPieceTriplet']for t in pieces],dtype='<f8').tobytes()).hexdigest(),
        savedRootNominationBytesReproduced=True,actualMaskPartitionCalls=0,
        fullActorOrFullCandidateReplay=False,physicalAccepted=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check-saved891-outside-adapter-only',action='store_true',required=True);parser.parse_args()
    print(json.dumps(audit(),sort_keys=True))
