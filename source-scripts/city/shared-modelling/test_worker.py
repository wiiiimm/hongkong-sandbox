import unittest
from unittest.mock import patch,MagicMock
import worker

class WorkerTests(unittest.TestCase):
    def test_decoded_source_record(self):
        con=MagicMock()
        con.execute.return_value.fetchone.return_value=('''{"columns":["uid","height"],"rowid_alias":"rowid"}''',)
        with patch('worker.lookup_row',return_value=[7,'landsd:test',12.5]):
            self.assertEqual(worker.source_record(con,'snapshot','buildings',{}),
                             {'rowid':7,'uid':'landsd:test','height':12.5})

    def test_missing_source(self):
        with patch('worker.lookup_row',return_value=None):
            self.assertIsNone(worker.source_record(MagicMock(),'snapshot','buildings',{}))

    def test_adapter_failure_is_not_success(self):
        job={'payload':{},'id':'fixture','stage':'audit-input-v1'}
        with patch('worker.claim',side_effect=[job,None]), patch('worker.finish',return_value=True), patch('worker.report',return_value={}), patch('worker.audit_input',side_effect=ValueError('private details')):
            with self.assertRaisesRegex(RuntimeError,'Worker failed'):
                worker.run('test',workers=1,limit=2)

    def test_reuses_existing_adapter(self):
        result=worker.audit_input({'building':{'height':12.5,'height_source':'landsd',
            'embedded':0,'metadata_json':'{}'},'model':None})
        self.assertEqual(result['nextAction'],'look-up-available-source-model')
        self.assertEqual(result['concerns'],[])

if __name__=='__main__':unittest.main()
