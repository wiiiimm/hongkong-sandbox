"""Strict point membership for an independently proven closed embedded shell."""
from fractions import Fraction
from exact_original_shell_intersections_20261009 import rational_face,sub,add,mul,dot,cross


def point_membership(point,triangles):
    p=rational_face([point,point,point])[0]
    faces=[rational_face(f) for f in triangles]
    assert 1<=len(faces)<=1000
    normals=[cross(sub(f[1],f[0]),sub(f[2],f[0])) for f in faces]
    assert all(any(n) for n in normals)
    def sides(q,face,n):
        return [dot(n,cross(sub(b,a),sub(q,a))) for a,b in zip(face,face[1:]+face[:1])]
    for face,n in zip(faces,normals):
        if dot(n,sub(p,face[0]))==0 and all(s>=0 for s in sides(p,face,n)):
            return {'classification':'boundary','strictlyInside':False,'exactArithmetic':True}
    for direction in [(1,2,3),(2,3,5),(3,5,7),(5,7,11),(7,11,13)]:
        d=tuple(Fraction(x) for x in direction);crossings=0;ambiguous=False
        for face,n in zip(faces,normals):
            denominator=dot(n,d);numerator=dot(n,sub(face[0],p))
            if denominator==0:
                if numerator==0:ambiguous=True;break
                continue
            t=numerator/denominator
            if t<=0:continue
            q=add(p,mul(d,t));s=sides(q,face,n)
            if all(v>=0 for v in s):
                if any(v==0 for v in s):ambiguous=True;break
                crossings+=1
        if not ambiguous:
            inside=bool(crossings%2)
            return {'classification':'inside' if inside else 'outside','strictlyInside':inside,
                    'rayDirection':list(direction),'crossings':crossings,'exactArithmetic':True}
    return {'classification':'unresolved','strictlyInside':False,'exactArithmetic':True}
