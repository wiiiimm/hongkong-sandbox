"""Pure bounded selection from completed overlap rows; no terrain computation."""
from fractions import Fraction as F
import math
from collections import Counter

PREFERENCES={('old-old',True):16,('old-old',False):8,('old-append',True):16,
             ('old-append',False):8,('append-append',True):8,('append-append',False):8}
def select(chunks, faces=148459):
    buckets={k:[]for k in PREFERENCES};fallback=[];seen=set();eligible=0
    for chunk_ref,chunk in chunks:
        for ordinal,row in enumerate(chunk['completeDeterministicIntersectingPairs']):
            if 'measuredPositiveAreaM2' not in row:continue
            area=row['measuredPositiveAreaM2'];assert math.isfinite(area) and area>0
            if area<=1e-8:continue
            i,j=row['leftFace'],row['rightFace'];assert type(i)is int and type(j)is int and 0<=i<j<faces
            key=(i,j);assert key not in seen;seen.add(key)
            assert row['group'] in ('old-old','old-append','append-append')
            assert type(row['sameAuthenticatedIdealPlane'])is bool
            eligible+=1;record=(chunk_ref,ordinal,row);group=(row['group'],row['sameAuthenticatedIdealPlane'])
            if len(fallback)<64:fallback.append(record)
            if len(buckets[group])<PREFERENCES[group]:buckets[group].append(record)
    chosen=[];used=set()
    for key,target in PREFERENCES.items():
        for record in buckets[key]:
            row=record[2];used.add((row['leftFace'],row['rightFace']));chosen.append(record)
    for record in fallback:
        if len(chosen)==64:break
        row=record[2];key=(row['leftFace'],row['rightFace'])
        if key not in used:used.add(key);chosen.append(record)
    assert len(chosen)==64,'bounded-saved-chunks-have-fewer-than-64-eligible-pairs'
    sites=[]
    for chunk_ref,ordinal,row in chosen:
        vertices=[tuple(F(v)for v in p)for p in row['measuredIntersectionVerticesXZ']]
        assert len(vertices)>=3 and all(len(p)==2 for p in vertices)and len(set(vertices))==len(vertices)
        mean=[sum(p[d]for p in vertices)/len(vertices)for d in range(2)]
        x,z=map(float,mean);assert math.isfinite(x)and math.isfinite(z)
        sites.append(dict(x=x,z=z,leftFace=row['leftFace'],rightFace=row['rightFace'],group=row['group'],sameAuthenticatedIdealPlane=row['sameAuthenticatedIdealPlane'],
            exactMeanOfSavedGEOSVerticesXZ=[str(v)for v in mean],sourceChunkRef=chunk_ref,sourceRowOrdinal=ordinal,
            fullSavedMeasuredPair=row,roundedSiteMembershipRequiresActualRuntimeCheck=True))
    return dict(rows=sites,samples=64,boundedCandidateRows=eligible,actualGroupCounts=dict(Counter(r['group']for r in sites)),
        sourceClassPreferencesNotAdmissionConditions=True,savedGEOSVerticesNotExactContinuousIntersectionProof=True,
        selectedPairsNotWholeSurfaceOrContinuousMAXProof=True,noTerrainCoordinatesChanged=True)
