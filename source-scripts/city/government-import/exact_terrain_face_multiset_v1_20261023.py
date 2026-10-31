"""Compare every finite terrain triangle exactly, retaining winding and multiplicity."""
from collections import Counter
import numpy as np


def same_faces(left,right):
    a=np.asarray(left,dtype='<f8');b=np.asarray(right,dtype='<f8')
    assert a.ndim==b.ndim==3 and a.shape[1:]==b.shape[1:]==(3,3)
    assert np.isfinite(a).all()and np.isfinite(b).all()
    return a.shape==b.shape and Counter(f.tobytes()for f in a)==Counter(f.tobytes()for f in b)
