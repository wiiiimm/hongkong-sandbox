"""Reuse frozen exact surface clips and check all six continuation/continuation pairs."""
from fractions import Fraction
from pathlib import Path
import itertools
import numpy as np
import shapely
from shapely.geometry import Polygon,Point
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_footing_prism_contacts_v1_20261028 import surface_contacts
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-sha-tin-'
SOURCE=PREFIX+'three-basic-continuation-foreign-volume-v1-20261029'
BATCH=PREFIX+'three-basic-continuation-pair-context-v1-20261029'


def main():
    out=BASE/BATCH;assert not out.exists()
    _,pins=authenticate(BASE/SOURCE);refs=[Path(__file__),BASE/SOURCE/'result.json',HERE/'exact_footing_prism_contacts_v1_20261028.py']
    def take(name):
        p=BASE/SOURCE/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
    context=take('summary.json');added=take('additions.json.gz');basics=take('basic.json')
    by_basic={r['uid']:r for r in basics['rows']};by_add={r['uid']:r for r in added['rows']};caps={};triangles={};footprints=[]
    for uid,row in by_add.items():
        tri=np.asarray(row['position']).reshape(-1,3)[np.asarray(row['index']).reshape(-1,3)]
        top=tri[:,:,1].max();cap=tri[(tri[:,:,1]==top).all(1)];caps[uid]=cap;triangles[uid]=tri
        b=by_basic[uid];old=np.asarray(b['position']).reshape(-1,3)[np.asarray(b['index']).reshape(-1,3)];old_cap=old[(old[:,:,1]==old[:,:,1].max()).all(1)]
        assert np.array_equal(cap[:,:,[0,2]],old_cap[:,:,[0,2]])
        footprints.append(dict(uid=uid,actualFloat32CapProjectionExactlyEqualsOriginalRoof=True,capFaces=len(cap),recordedFormUnchanged=True))
    out.mkdir();pairs=[]
    for target,other in itertools.permutations(by_add,2):
        tri=triangles[target];bottom,top=float(tri[:,:,1].min()),float(tri[:,:,1].max());proof=surface_contacts(triangles[other],caps[target],bottom,top)
        name=target.split('/')[1]+'--'+other.split('/')[1]+'-new-new.json.gz';save(out/name,proof)
        pairs.append(dict(targetUid=target,uid=other,completeOtherAdditionFaces=len(triangles[other]),closedPrismContactPairs=len(proof['contacts']),proof=name,collisionReviewApproved=False))
    rows=[]
    for row in context['rows']:
        if not row['contactPairs']:continue
        role=('same-owner-alternative-state'if row['uid']==row['targetUid']else'candidate-native-mixed-state'if row['role']=='candidate-original'else'other-proposed-basic-counterpart'if row['uid']in by_add else'external-retained-basic-interface')
        fresh=dict(row,sceneRole=role)
        if row['role']=='current-basic':
            proof=take(row['proof']);pts=np.asarray([[float(Fraction(v))for v in p]for r in proof['contacts']for p in r['exactClippedPoints']]);b=by_basic[row['targetUid']]['currentBuilding'];poly=Polygon(b['rings'][0],b['rings'][1:])
            fresh.update(clippedYRange=[float(pts[:,1].min()),float(pts[:,1].max())],maximumDistanceFromOriginalDecimalFootprintBoundaryM=max(poly.boundary.distance(Point(float(x),float(z)))for x,y,z in pts),foreignRecordedBase=by_basic[row['uid']]['currentBuilding']['base'],rawContactNotWaived=True)
        rows.append(fresh)
    result=dict(uids=context['uids'],targets=list(by_add),footprintRows=footprints,allSixNewNewPairs=pairs,rawContactRows=rows,allOriginalContactRowsRetained=True,sourceGeometryChanges=0,privateProposalOnly=True,commonNativeActivationStillNeedsActualLifecycleProof=True,reverseSolidContainmentProved=False,collisionReviewApproved=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification='All actual new Float32 top-cap XZ triangles equal the unchanged BASIC roof projection exactly. Six ordered new/new closed-prism clips supplement the existing291complete source/basic contexts. Own source versus BASIC is an alternative-state context; other candidate originals require actual common availability checks. External BASIC contacts remain explicit, including existing Float32/decimal boundary differences. No contact is discarded or thresholded away. This packet is geometry/interface context, not physical, structural, containment, browser or publication acceptance.')
    save(out/'summary.json',result)
    module('sha_tin_basic_pair_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-basic-continuation-exact-footprint-and-all-pair-context',list(dict.fromkeys(refs)),result)


if __name__=='__main__':main()
