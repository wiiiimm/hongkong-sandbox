import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from migrate_database import params, check_identity

class MigrationSafetyTests(unittest.TestCase):
    def test_connection_must_match_verified_direct_endpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'source-branch.json').write_text(json.dumps({'host':'expected.neon.tech','database':'neondb'}))
            for host in ('wrong.neon.tech','expected-pooler.neon.tech'):
                (root/'source-connection.json').write_text(json.dumps({'MODELLING_DATABASE_URL':f'postgresql://u:p@{host}/neondb'}))
                with self.assertRaises(ValueError):params(root,'source')
            (root/'source-connection.json').write_text(json.dumps({'MODELLING_DATABASE_URL':'postgresql://u:p@expected.neon.tech/neondb'}))
            self.assertEqual(params(root,'source')['sslmode'],'verify-full')

    def test_server_branch_identity_must_match(self):
        con=Mock()
        con.execute.return_value.fetchone.return_value=('neondb','project','wrong-branch')
        with self.assertRaises(ValueError):
            check_identity(con,{'database':'neondb','project_id':'project','branch_id':'expected'})
        con.execute.return_value.fetchone.return_value=('neondb','project','expected')
        check_identity(con,{'database':'neondb','projectId':'project','branchId':'expected'})

if __name__=='__main__':unittest.main()
