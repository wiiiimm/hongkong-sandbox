import unittest
import numpy as np
from retained_inset_work_budget_v1_20261026 import verify


class WorkBudgetTests(unittest.TestCase):
    def setUp(self):
        self.face=np.array([[0.,2.,0.],[1.,2.,0.],[0.,2.,1.]])
        self.base=np.array([self.face,self.face+2])
    def test_exact_inherited_mesh_can_exceed_new_work_cap(self):
        base=np.repeat(self.face[None],25001,axis=0)
        result=verify(base,base,[dict(kind='unchanged',parentFace=i)for i in range(len(base))])
        self.assertEqual(result['newWorkFaces'],0)
        self.assertFalse(result['installationApproved'])
    def test_bound_new_work_is_counted_separately(self):
        result=verify(self.base,self.base,[dict(kind='unchanged',parentFace=0),dict(kind='parent-fragment',parentFace=1)])
        self.assertEqual((result['unchangedFaces'],result['replacedFaces'],result['newWorkFaces']),(1,1,1))
    def test_altered_inherited_face_rejected(self):
        out=self.base.copy();out[0,0,1]+=.01
        with self.assertRaises(AssertionError):verify(self.base,out,[dict(kind='unchanged',parentFace=i)for i in range(2)])
    def test_duplicate_inherited_face_rejected(self):
        with self.assertRaises(AssertionError):verify(self.base,np.array([self.face,self.face]),[dict(kind='unchanged',parentFace=0)]*2)
    def test_omitted_parent_rejected(self):
        with self.assertRaises(AssertionError):verify(self.base,self.base[:1],[dict(kind='unchanged',parentFace=0)])
    def test_face_cannot_be_inherited_and_replaced(self):
        with self.assertRaises(AssertionError):verify(self.base,np.array([self.face,self.face,self.face+2]),[dict(kind='unchanged',parentFace=0),dict(kind='parent-fragment',parentFace=0),dict(kind='unchanged',parentFace=1)])
    def test_more_than_25000_new_work_faces_rejected(self):
        with self.assertRaises(AssertionError):verify(self.base[:1],np.repeat(self.face[None],25001,axis=0),[dict(kind='parent-fragment',parentFace=0)]*25001)
    def test_foreign_parent_and_nonfinite_rejected(self):
        for record,face in [(dict(kind='unchanged',parentFace=2),self.face),(dict(kind='unchanged',parentFace=0),self.face*np.nan)]:
            with self.subTest(record=record):
                with self.assertRaises(AssertionError):verify(self.base[:1],np.array([face]),[record])


if __name__=='__main__':unittest.main()
