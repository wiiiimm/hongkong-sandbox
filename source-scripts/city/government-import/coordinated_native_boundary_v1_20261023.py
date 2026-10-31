"""Exact piecewise-linear comparison of two finite rendered terrain seams.

Diagnostic math only. This module changes no validator or publication contract.
Projected-vertical faces receive no height credit, matching native-terrain.js.
"""
from fractions import Fraction
import numpy as np


def rational(value):return Fraction.from_float(float(value))


def seam_segments(triangles,axis,coordinate,start,end):
    assert axis in [0,2]and start<end
    values=np.asarray(triangles,dtype='float32').astype('float64')
    assert values.ndim==3 and values.shape[1:]==(3,3)and np.isfinite(values).all()
    other=2 if axis==0 else 0
    c,lo,hi=map(rational,[coordinate,start,end]);segments=[]
    selected=np.flatnonzero((values[:,:,axis].min(1)<=coordinate)&(values[:,:,axis].max(1)>=coordinate)&(values[:,:,other].min(1)<=end)&(values[:,:,other].max(1)>=start))
    for face_id in selected:
        face=values[face_id];a,b,d=face
        determinant=(b[2]-d[2])*(a[0]-d[0])+(d[0]-b[0])*(a[2]-d[2])
        if abs(determinant)<1e-10:continue
        points=[tuple(map(rational,p))for p in face];crossings=set()
        for a,b in zip(points,points[1:]+points[:1]):
            if a[axis]==c:crossings.add((a[other],a[1]))
            if (a[axis]<c<b[axis])or(b[axis]<c<a[axis]):
                t=(c-a[axis])/(b[axis]-a[axis]);crossings.add((a[other]+t*(b[other]-a[other]),a[1]+t*(b[1]-a[1])))
        if not crossings:continue
        ordered=sorted(crossings);left,right=ordered[0],ordered[-1]
        assert left[0]!=right[0]or left[1]==right[1]
        if right[0]<lo or left[0]>hi:continue
        if left[0]==right[0]:
            segments.append((left[0],left[0],left[1],left[1],int(face_id)));continue
        start_at=max(lo,left[0]);end_at=min(hi,right[0])
        def at(t):return left[1]+(t-left[0])*(right[1]-left[1])/(right[0]-left[0])
        segments.append((start_at,end_at,at(start_at),at(end_at),int(face_id)))
    return segments


def value(segment,t):
    a,b,ya,yb,*_=segment
    assert a<=t<=b
    return ya if a==b else ya+(t-a)*(yb-ya)/(b-a)


def seam_comparison_report(left,right,start,end,tolerance=Fraction(1,100)):
    """Check entire upper envelopes, including isolated vertex contacts and limits."""
    lo,hi=map(rational,[start,end]);assert lo<hi and 0<tolerance<=Fraction(1,100)
    cuts={lo,hi}
    for segments in [left,right]:
        assert segments,'No finite rendered seam surface'
        for s in segments:
            assert lo<=s[0]<=s[1]<=hi
            cuts.update(s[:2])
        # Upper-envelope kinks may occur where overlapping source planes cross.
        for i,a in enumerate(segments):
            if a[0]==a[1]:continue
            for b in segments[i+1:]:
                x0=max(a[0],b[0]);x1=min(a[1],b[1])
                if x0>=x1:continue
                d0=value(a,x0)-value(b,x0);d1=value(a,x1)-value(b,x1)
                if d0*d1<0:cuts.add(x0-d0*(x1-x0)/(d1-d0))
    cuts=sorted(cuts);maximum=Fraction(0);checks=0;witness=None
    def check(a,b,t,kind):
        nonlocal maximum,witness,checks
        error=abs(a-b);checks+=1
        if error>maximum:
            maximum=error;witness=dict(coordinate=float(t),exactCoordinate=str(t),leftHeight=float(a),rightHeight=float(b),comparison=kind)
    def maximum_at(segments,t):
        covering=[s for s in segments if s[0]<=t<=s[1]]
        assert covering,'Gap in shared boundary surface'
        return max(value(s,t)for s in covering)
    for t in cuts:
        check(maximum_at(left,t),maximum_at(right,t),t,'point-upper-envelope')
    for a,b in zip(cuts,cuts[1:]):
        mid=(a+b)/2
        winners=[]
        for segments in [left,right]:
            covering=[s for s in segments if s[0]<=mid<=s[1]]
            assert covering,'Gap in shared boundary interval'
            winners.append(max(covering,key=lambda s:value(s,mid)))
        # Compare one-sided limits as well as point values. A point-only spike
        # cannot conceal a mismatch immediately beside an interval endpoint.
        for t in [a,mid,b]:
            check(value(winners[0],t),value(winners[1],t),t,'finite-interval-limit')
    return dict(passed=maximum<tolerance,maximumWitness=witness,completeFiniteUpperEnvelopesChecked=True,breakpoints=len(cuts),checks=checks,
        maximumErrorM=float(maximum),exactMaximumError=str(maximum),toleranceM=float(tolerance),
        projectedVerticalFacesProvideNoHeightCredit=True,validatorChanged=False,publicationApproved=False)


def compatible_seam(left,right,start,end,tolerance=Fraction(1,100)):
    report=seam_comparison_report(left,right,start,end,tolerance)
    assert report['passed'],'Shared terrain boundary differs beyond unchanged 1cm boundary guard'
    return report
