import unittest
from coverage import coverage
from blindbox.requests.requests import _parse_url

SERVER_URL = "localhost"
SERVER_PORT = 8080
TEST_FILE = "tests/test.wav"

class TestBlindBoxRequests(unittest.TestCase):
    def test_parse_url(self):
        url = "https://example.com/api"
        root, endpoint = _parse_url(url)
        self.assertEqual(root, "https://example.com")
        self.assertEqual(endpoint, "/api")

        url = "http://localhost:8000"
        root, endpoint = _parse_url(url)
        self.assertEqual(root, "http://localhost:8000")
        self.assertEqual(endpoint, "")

    '''
    def test_post(self):
        with open(TEST_FILE, "rb") as file:
            response = requests.post(url=f"http://{SERVER_URL}:{SERVER_PORT}/enclave/predict", cce_policy="./cce_policy.txt", files={"audio": file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "[POST] /enclave : Server response")

    def test_get(self):
        response = requests.get(f"http://{SERVER_URL}:{SERVER_PORT}/enclave", "./cce_policy.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "[GET] /enclave : Server response")
    '''

if __name__ == '__main__':
    unittest.main()
