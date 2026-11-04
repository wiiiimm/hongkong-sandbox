"""Regression checks for vertical terrain at clipped join boundaries."""
import numpy as np
from shapely.geometry import box
from stanford_local_terrain_join_v4_20261015 import split_vertical

def area(parts):
 return sum(np.linalg.norm(np.cross(t[1]-t[0],t[2]-t[0]))/2 for t in np.asarray(parts)) if parts else 0

def main():
 face=np.array([[0.,0,0],[2,0,0],[0,2,0]])
 inside=split_vertical(face,box(.5,-1,1.5,1));assert len(inside)==2 and abs(area(inside)-1)<1e-12
 assert np.array_equal(np.asarray(split_vertical(face,box(-1,-1,3,1)))[0],face)
 assert not split_vertical(face,box(3,-1,4,1))
 assert abs(area(split_vertical(face,box(-1,-1,3,1).difference(box(.5,-1,1.5,1))))+area(inside)-area([face]))<1e-12
 # Repeat with the projected line running along Z rather than X.
 rotated=face[:,[2,1,0]];assert abs(area(split_vertical(rotated,box(-1,.5,1,1.5)))-1)<1e-12
 print('5 vertical terrain split checks passed')
if __name__=='__main__':main()
