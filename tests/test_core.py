import unittest
from dockspawn.ports import get_next_available_port
from dockspawn.utils import extract_jupyter_url
from dockspawn.gpu import parse_gpu_config

class TestPorts(unittest.TestCase):
    def test_get_next_available_port(self):
        # Unless all ports from 40000 to 65535 are used, this should work locally.
        port = get_next_available_port(start_port=40000)
        self.assertGreaterEqual(port, 40000)

class TestUtils(unittest.TestCase):
    def test_extract_jupyter_url(self):
        logs = """
[I 2024-03-04 12:00:00.000 ServerApp] Jupyter Server 2.7.3 is running at:
[I 2024-03-04 12:00:00.000 ServerApp] http://127.0.0.1:8888/lab?token=abcde12345
[I 2024-03-04 12:00:00.000 ServerApp]     http://127.0.0.1:8888/lab?token=abcde12345
[I 2024-03-04 12:00:00.000 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
        """
        url = extract_jupyter_url(logs)
        self.assertEqual(url, "http://127.0.0.1:8888/lab?token=abcde12345")

class TestGpu(unittest.TestCase):
    def test_parse_gpu_config(self):
        self.assertEqual(parse_gpu_config(""), "all")
        self.assertEqual(parse_gpu_config("all"), "all")
        self.assertEqual(parse_gpu_config("ALL"), "all")
        self.assertEqual(parse_gpu_config("0"), "['0']")
        self.assertEqual(parse_gpu_config("0,1,2 "), "['0', '1', '2']")
        
if __name__ == '__main__':
    unittest.main()
