"""Compare a rendered vertical boundary strip to a finite mate height curve.

A vertical strip provides no height-field, ground, root or structural credit.
This verifies only its complete rendered boundary geometry within the existing
strict 1cm seam limit, including isolated curve points and one-sided limits.
"""
from fractions import Fraction
import numpy as np
from coordinated_native_boundary_v1_20261023 import rational,value


def strip_report(face,axis,coordinate,segments,lo,hi,tolerance=Fraction(1,100)):
    face=np.asarray(face,dtype='float32').astype('float64')
    assert axis in [0,2]and face.shape==(3,3)and np.isfinite(face).all()
    points=[tuple(map(rational,p))for p in face];c=rational(coordinate);other=2 if axis==0 else 0
    assert all(p[axis]==c for p in points),'Strip is not on the exact shared plane'
    polygon=[(p[other],p[1])for p in points]
    (a,b),(d,e),(g,h)=polygon
    assert (d-a)*(h-b)-(e-b)*(g-a)!=0,'Nonrendering primitive cannot supply a rendered strip witness'
    start,end=min(p[0]for p in polygon),max(p[0]for p in polygon)
    assert lo<=start<end<=hi and segments
    cuts={p[0]for p in polygon}
    for s in segments:
        cuts.update(t for t in s[:2]if start<=t<=end)
    for i,a in enumerate(segments):
        if a[0]==a[1]:continue
        for b in segments[i+1:]:
            x0=max(start,a[0],b[0]);x1=min(end,a[1],b[1])
            if x0>=x1:continue
            y0=value(a,x0)-value(b,x0);y1=value(a,x1)-value(b,x1)
            if y0*y1<0:cuts.add(x0-y0*(x1-x0)/(y1-y0))
    def strip_heights(t):
        heights=[]
        for a,b in zip(polygon,polygon[1:]+polygon[:1]):
            if a[0]==t:heights.append(a[1])
            if (a[0]<t<b[0])or(b[0]<t<a[0]):heights.append(a[1]+(t-a[0])*(b[1]-a[1])/(b[0]-a[0]))
        assert heights
        return heights
    maximum=Fraction(0);checks=0;ordered=sorted(cuts)
    for t in ordered:
        covering=[s for s in segments if s[0]<=t<=s[1]];assert covering
        height=max(value(s,t)for s in covering)
        for y in strip_heights(t):maximum=max(maximum,abs(y-height));checks+=1
    for a,b in zip(ordered,ordered[1:]):
        mid=(a+b)/2;covering=[s for s in segments if s[0]<=mid<=s[1]];assert covering
        winner=max(covering,key=lambda s:value(s,mid))
        for t in [a,mid,b]:
            for y in strip_heights(t):maximum=max(maximum,abs(y-value(winner,t)));checks+=1
    assert maximum<tolerance,'Rendered shared-boundary strip differs from finite mate'
    return dict(completeRenderedStripCompared=True,checks=checks,maximumErrorM=float(maximum),
                heightFieldCredit=False,structuralSupportCredit=False)
