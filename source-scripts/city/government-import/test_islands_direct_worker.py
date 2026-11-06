"""Reject incomplete or substituted original-port browser evidence."""
import copy
import unittest
from islands_direct_worker import solid_verified


class SolidEvidenceTests(unittest.TestCase):
    def setUp(self):
        uid='landsd/1:0';self.models=[{'uid':uid,'sha256':'a'*64,'triangles':12}]
        self.report={'passed':True,'errors':[],'views':[dict(uid=uid,width=w,time=t,sourceSHA256='a'*64,originalTriangles=12,
            active=True,visible=True,fullyFramed=True,solidAppearance=True,selectionClosed=True,pick=uid,collision=uid,
            overflow=False,fallbackFaces=0,meshVisibility=[True],wireframeFlags=[False],materialOpacities=[1])
            for w in(1280,390)for t in('15:00','22:00')]+[{'uid':uid,'width':390,'fallbackRetained':True}]}

    def test_complete_exact_original(self):
        self.assertTrue(solid_verified(self.report,self.models))

    def test_source_or_render_failures(self):
        for key,value in [('sourceSHA256','b'*64),('originalTriangles',11),('fallbackFaces',1),('wireframeFlags',[True]),
             ('materialOpacities',[.5]),('meshVisibility',[False]),('fullyFramed',False),('selectionClosed',False),('pick','other'),('collision','other')]:
            with self.subTest(key=key):
                report=copy.deepcopy(self.report);report['views'][0][key]=value
                with self.assertRaises(AssertionError):solid_verified(report,self.models)

    def test_missing_view_or_retry(self):
        for i in (0,-1):
            report=copy.deepcopy(self.report);report['views'].pop(i)
            with self.assertRaises(AssertionError):solid_verified(report,self.models)

    def test_duplicate_view_cannot_replace_missing_view(self):
        report=copy.deepcopy(self.report);report['views'][0]=copy.deepcopy(report['views'][1])
        with self.assertRaises(AssertionError):solid_verified(report,self.models)


if __name__=='__main__':unittest.main()
