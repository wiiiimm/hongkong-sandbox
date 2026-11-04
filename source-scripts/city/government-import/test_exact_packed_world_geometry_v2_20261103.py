"""Unsigned-byte index compatibility must preserve exact vertices and checks."""
import unittest
import numpy as np
from source43101_provider_roots_v1_20261029 import glb
from exact_packed_world_geometry_20261009 import decode_original_world_triangles as old
from exact_packed_world_geometry_v2_20261103 import decode_original_world_triangles as new


def fixture(kind=5121,bad=False):
    positions=np.array([[834500,0,-816500],[834501,0,-816500],[834500,1,-816500]],dtype='<f4')
    indices=np.array([0,1,255 if bad else 2],dtype={5121:'u1',5123:'<u2',5125:'<u4'}[kind])
    binary=positions.tobytes()+indices.tobytes()
    doc=dict(asset=dict(version='2.0'),buffers=[dict(byteLength=len(binary))],
        bufferViews=[dict(buffer=0,byteOffset=0,byteLength=positions.nbytes),dict(buffer=0,byteOffset=positions.nbytes,byteLength=indices.nbytes)],
        accessors=[dict(bufferView=0,componentType=5126,count=3,type='VEC3'),dict(bufferView=1,componentType=kind,count=3,type='SCALAR')],
        meshes=[dict(primitives=[dict(attributes=dict(POSITION=0),indices=1)])],nodes=[dict(mesh=0)],scenes=[dict(nodes=[0])],scene=0)
    return glb(doc,binary)


class IndexWidths(unittest.TestCase):
    def test_uint8_exact_geometry(self):
        expected=np.array([[[0,0,0],[1,0,0],[0,1,0]]],dtype=float)
        np.testing.assert_array_equal(new(fixture()),expected)
    def test_existing_uint16_stream_unchanged(self):
        raw=fixture(5123);np.testing.assert_array_equal(new(raw),old(raw))
    def test_existing_uint32_stream_unchanged(self):
        raw=fixture(5125);np.testing.assert_array_equal(new(raw),old(raw))
    def test_uint8_out_of_bounds_still_rejected(self):
        with self.assertRaises(AssertionError):new(fixture(bad=True))


if __name__=='__main__':unittest.main()
