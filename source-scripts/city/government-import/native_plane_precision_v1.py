"""Exact 3D source-plane residuals at native Float32 precision; no contact waiver."""
from fractions import Fraction as F
import numpy as np

def assess(face,raw):
 a,b,c=[[F(float(v))for v in p]for p in face];u=[b[i]-a[i]for i in range(3)];v=[c[i]-a[i]for i in range(3)];n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];scale=max(map(abs,n));assert scale>0
 p=[F(float(v))for v in raw];packed=[F(float(v))for v in np.asarray(raw,dtype='<f4')];budget=sum(F(abs(float(np.spacing(np.float32(v)))))/2 for v in raw)
 def bound(point):return abs(sum(n[i]*(point[i]-a[i])for i in range(3)))/scale
 pre,post=bound(p),bound(packed);return dict(rawPlaneDistanceUpperBoundM=str(pre),packedPlaneDistanceUpperBoundM=str(post),coordinateHalfULPSumM=str(budget),withinNativeCoordinatePrecision=pre<=budget and post<=2*budget)
