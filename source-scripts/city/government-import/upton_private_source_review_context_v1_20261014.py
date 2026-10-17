"""Metadata/display adapter only; never contact or installation acceptance."""
from fractions import Fraction
from collections import Counter

def display_point(exact):
    assert len(exact)==3
    return [float(Fraction(v)) for v in exact]

def contact_summary(worlds,ground_sha,ground_count):
    out=[]
    for world in worlds:
        rows=world['freshMainContactGroundContext'];dimensions=Counter();whole_lines=0;failed=[];chords=0
        assert len(rows)==len(world['exactSourceOnlyContactsVerbatim']['contacts'])
        for i,row in enumerate(rows):
            c=row['originalContactVerbatim'];dim=c['dimension'];assert dim in [0,1,2]
            dimensions[dim]+=1
            proofs=row['freshWholeLineOrAreaChordGroundProofs']
            assert row['areaInteriorNotQualified']==(dim==2) and not row['rootRoleOrBridgeAccepted']
            assert (dim==0 and not proofs) or (dim==1 and len(proofs)==1) or (dim==2 and proofs)
            for p in proofs:
                q=p['freshCompleteCurrentGround'];s=q['selection']
                assert s['completeGroundSHA256']==ground_sha and s['completeGroundFacetCount']==ground_count
                assert s['everyNoncandidateStrictlyDisjoint'] and s['touchingAndCollapsedProjectionsRetained']
                assert q['rootOrStructuralCredit'] is False
            exposed=bool(proofs) and all(p['freshCompleteCurrentGround']['strictlyExposedWholePositiveInterface'] for p in proofs)
            if dim==1 and exposed:whole_lines+=1
            if dim>0 and not exposed:failed.append(i)
            if dim==2:chords+=len(proofs)
        out.append(dict(mode=world['mode'],actualWholeSourceWorldHashes=world['actualWholeSourceWorldHashes'],sourceContacts=len(rows),dimensions=dict(dimensions),strictlyExposedWholeLineContacts=whole_lines,positiveContactsWithUnprovedChordOrLineExposure=failed,areaBoundaryAndChordProofs=chords,areaInteriorQualification=False,oldPacketGroundHashVerbatim=world['oldPacketGroundHashNotRelabelled'],strictInterfacePassed=False,functionalSourceRoleAccepted=False,installationApproved=False))
    return out
