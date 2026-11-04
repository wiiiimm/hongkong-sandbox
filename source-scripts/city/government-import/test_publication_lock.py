import multiprocessing as mp
import tempfile
import unittest
from publication_lock import locked_publication

def writer(root,connection):
    with locked_publication(root):
        connection.send('acquired')
        connection.recv()
    connection.send('released')

class PublicationLockTests(unittest.TestCase):
    def test_second_writer_waits_until_first_writer_releases(self):
        with tempfile.TemporaryDirectory() as root:
            a,ca=mp.Pipe();b,cb=mp.Pipe()
            first=mp.Process(target=writer,args=(root,ca));second=mp.Process(target=writer,args=(root,cb))
            try:
                first.start();self.assertTrue(a.poll(5));self.assertEqual(a.recv(),'acquired')
                second.start();self.assertFalse(b.poll(.1))
                a.send('finish');self.assertTrue(a.poll(5));self.assertEqual(a.recv(),'released')
                self.assertTrue(b.poll(5));self.assertEqual(b.recv(),'acquired');b.send('finish')
                self.assertTrue(b.poll(5));self.assertEqual(b.recv(),'released')
            finally:
                for process in [first,second]:
                    if process.pid:
                        process.join(5)
                        if process.is_alive():process.terminate();process.join()
            self.assertEqual(first.exitcode,0);self.assertEqual(second.exitcode,0)
    def test_exception_releases_lock_for_another_process(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(RuntimeError):
                with locked_publication(root):raise RuntimeError('Interrupted writer')
            parent,child=mp.Pipe();process=mp.Process(target=writer,args=(root,child))
            try:
                process.start();self.assertTrue(parent.poll(5));self.assertEqual(parent.recv(),'acquired');parent.send('finish')
                self.assertTrue(parent.poll(5));self.assertEqual(parent.recv(),'released')
            finally:
                process.join(5)
                if process.is_alive():process.terminate();process.join()
            self.assertEqual(process.exitcode,0)

if __name__=='__main__':unittest.main()
