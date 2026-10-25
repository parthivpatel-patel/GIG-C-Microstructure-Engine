import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from terminal.server.app import create_app

class RecordingAPI(unittest.TestCase):
    def test_explicit_authored_save_verify_delete(self):
        with tempfile.TemporaryDirectory() as root, patch('terminal.server.app.ROOT',Path(root)):
            with TestClient(create_app(),base_url='http://127.0.0.1:8787') as client:
                def post(data):return client.post('/api/v1/recording',json=data,headers={'Origin':'http://127.0.0.1:8787'})
                self.assertEqual(post({'action':'save'}).status_code,409)
                self.assertFalse((Path(root)/'terminal/recordings').exists())
                self.assertEqual(post({'action':'save','enabled':True}).status_code,200)
                verified=post({'action':'verify'});self.assertEqual(verified.status_code,200)
                self.assertEqual(verified.json()['result']['native_accepted'],'260')
                self.assertFalse(verified.json()['observed_recording'])
                self.assertEqual(post({'action':'save','enabled':True}).status_code,409)
                self.assertEqual(post({'action':'verify','path':'/private'}).status_code,400)
                self.assertEqual(post({'action':'delete'}).status_code,200)
                self.assertEqual(post({'action':'verify'}).status_code,409)

if __name__=='__main__':unittest.main()
