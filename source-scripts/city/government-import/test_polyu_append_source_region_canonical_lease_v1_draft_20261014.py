"""One synthetic receipt/lifecycle fixture; extract main without source imports."""
import ast,copy,datetime,json,tempfile,unittest,uuid
from pathlib import Path
from types import SimpleNamespace

CALLER=Path(__file__).with_name('polyu_append_source_region_residual_repair_caller_v1_draft_20261014.py')
class CanonicalLeaseReceiptFixture(unittest.TestCase):
    def test_actual_nested_group_serialization_and_protected_cleanup(self):
        tree=ast.parse(CALLER.read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
        compiled=compile(ast.fix_missing_locations(ast.Module(body=[main],type_ignores=[])),str(CALLER),'exec')
        for failure in [None,'save','worker','ownership-ended']:
            with self.subTest(failure=failure),tempfile.TemporaryDirectory()as tmp:
                base=Path(tmp);batch='synthetic-only';key='immutable-source-proof:'+batch
                group=dict(token=uuid.UUID('01234567-89ab-cdef-0123-456789abcdef'),owner='fixture-owner',batch=batch,resources=[key],generations={key:23},
                    heartbeat_at=datetime.datetime(2026,10,14,tzinfo=datetime.timezone.utc),lease_until=datetime.datetime(2026,10,14,1,tzinfo=datetime.timezone.utc),released_at=None)
                before=copy.deepcopy(group);events=[]
                def claim(owner,resources,**kwargs):
                    self.assertEqual(resources,[key]);self.assertEqual(kwargs,dict(batch=batch,ttl=3600));events.append('claim');return dict(ok=True,reservation=group)
                def save(path,value):
                    self.assertEqual(path,base/'local/reservation.json');self.assertEqual(value,json.loads(json.dumps(group,default=str)))
                    self.assertEqual(value['token'],str(group['token']));self.assertIsInstance(value['lease_until'],str);events.append('save')
                    if failure=='save':raise OSError('synthetic save failure')
                def run(args):
                    self.assertIn('--lease-file',args);self.assertEqual(args[-1],'--owned');events.append('worker')
                    return SimpleNamespace(returncode=7 if failure=='worker'else 0)
                def owns(lease):self.assertIs(lease,group);events.append('owns');return failure!='ownership-ended'
                def release(lease):self.assertIs(lease,group);events.append('release')
                env=dict(Path=Path,json=json,uuid=uuid,sys=SimpleNamespace(argv=['fixture','--nominate-append-only-source-regions'],executable='synthetic-python'),
                    DOC=base/'doc',LOCAL=base/'local',LEASE=base/'local/reservation.json',BATCH=batch,HERE=base/'government-import',load=lambda:None,
                    save=save,subprocess=SimpleNamespace(run=run),reservations=SimpleNamespace(claim=claim,owns=owns,release=release),__file__=str(CALLER))
                exec(compiled,env)
                if failure=='save':
                    with self.assertRaises(OSError):env['main']()
                elif failure=='worker':
                    with self.assertRaises(AssertionError):env['main']()
                else:env['main']()
                self.assertEqual(group,before);self.assertEqual(events[:2],['claim','save'])
                self.assertEqual(events[-1],'owns'if failure=='ownership-ended'else'release')
                if failure=='save':self.assertNotIn('worker',events)
if __name__=='__main__':unittest.main(verbosity=2)
