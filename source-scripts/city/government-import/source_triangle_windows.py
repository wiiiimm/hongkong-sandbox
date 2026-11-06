"""Cached exact triangle AABBs; selection matches the former full-array scan."""
import numpy as np


class TriangleWindows:
    def __init__(self, triangles):
        self.triangles=np.asarray(triangles)
        assert self.triangles.ndim==3 and self.triangles.shape[1:]==(3,3) and np.isfinite(self.triangles).all()
        self.min_x=self.triangles[:,:,0].min(axis=1);self.max_x=self.triangles[:,:,0].max(axis=1)
        self.min_z=self.triangles[:,:,2].min(axis=1);self.max_z=self.triangles[:,:,2].max(axis=1)

    def select(self, bounds):
        x0,z0,x1,z1=bounds
        assert np.isfinite(bounds).all() and x0<=x1 and z0<=z1
        return self.triangles[(self.max_x>=x0)&(self.min_x<=x1)&(self.max_z>=z0)&(self.min_z<=z1)]
