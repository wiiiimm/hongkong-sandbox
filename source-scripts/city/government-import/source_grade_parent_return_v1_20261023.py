"""Blend authenticated land terrain to its existing parent without deepening water."""
import numpy as np


def blend(source_height,parent_height,weights):
    source=np.asarray(source_height,dtype=float);parent=np.asarray(parent_height,dtype=float);weight=np.asarray(weights,dtype=float)
    assert source.shape==parent.shape==weight.shape
    assert np.isfinite(source).all()and np.isfinite(parent).all()and np.isfinite(weight).all()
    assert np.all(source>=1.2),'New source terrain is below the unchanged land-height floor'
    assert np.all((weight>=0)&(weight<=1)),'Return weight outside bounded sector'
    result=source*(1-weight)+parent*weight
    low=result<1.2
    assert np.all(parent[low]<1.2)and np.all(result[low]>=parent[low]),'Return introduces or deepens below-clamp terrain'
    return result
