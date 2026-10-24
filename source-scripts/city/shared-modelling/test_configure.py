import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from dotenv import dotenv_values
import configure
from db import CONFIG
from urllib.parse import urlsplit

class ConfigureTests(unittest.TestCase):
    def test_pins_branch_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'.env.local'
            source.write_text('DATABASE_URL_UNPOOLED="postgresql://user:fixture@old.neon.tech/neondb?sslmode=require"\n')
            with patch('configure.ROOT',root):
                result=configure.configure(source)
                output=root/'.env.modelling'
                self.assertEqual(urlsplit(dotenv_values(output)['MODELLING_DATABASE_URL']).hostname,CONFIG['host'])
                self.assertEqual(output.stat().st_mode & 0o777,0o600)
                self.assertNotIn('fixture',str(result))
                with self.assertRaises(FileExistsError):configure.configure(source)

    def test_missing_credentials_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'.env.local';source.write_text('DATABASE_URL=unused\n')
            with patch('configure.ROOT',root):
                with self.assertRaises(ValueError):configure.configure(source)
                self.assertFalse((root/'.env.modelling').exists())

if __name__=='__main__':unittest.main()
