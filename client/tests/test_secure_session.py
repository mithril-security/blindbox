import unittest
from coverage import coverage
import warnings
from blindbox.requests.secure_session import SecureSession, connect, BlindBoxDebugModeWarning
from requests.exceptions import ContentDecodingError


SERVER_URL = "localhost"
SERVER_PORT = 8080
TEST_FILE = "tests/test.wav"


class TestBlindBoxSecureSession(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore", BlindBoxDebugModeWarning)

    def test_SecureSession_init_with_debug_mode(self):
        # Assert that a warning is raised for debug mode
        with self.assertWarns(BlindBoxDebugModeWarning):
            session = SecureSession("https://example.com", debug_mode=True)

    def test_get_method(self):
        with SecureSession("http://localhost:8080", debug_mode=True) as session:
            self.assertEqual(session.base_url, "http://localhost:8080")
            response = session.get("/enclave")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "[GET] /enclave : Server response")

    def test_options_method(self):
        with SecureSession("http://localhost:8080", debug_mode=True) as session:
            response = session.options("/enclave")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "[OPTIONS] /enclave : Server response")

    def test_head_method(self):
        with SecureSession("http://localhost:8080", debug_mode=True) as session:
            response = session.head("/enclave/head")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["text"], "[HEAD] /enclave/head : Server response")

    def test_post_method(self):
        with SecureSession("http://localhost:8080", debug_mode=True) as session:
            with open(TEST_FILE, "rb") as file:
                response = session.post("/enclave/predict", files={"audio": file})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "[POST] /enclave/predict : Server response")

    def test_put_method(self):
        with SecureSession("http://localhost:8080", debug_mode=True) as session:
            with open(TEST_FILE, "rb") as file:
                response = session.put("/enclave", data=file.read())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "[PUT] /enclave : Server response")

    def test_patch_method(self):
        with SecureSession("http://localhost:8080", debug_mode=True) as session:
            with open(TEST_FILE, "rb") as file:
                response = session.patch("/enclave", data=file.read())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "[PATCH] /enclave : Server response")

    def test_delete_method(self):
        with SecureSession("http://localhost:8080", debug_mode=True) as session:
            with open(TEST_FILE, "rb") as file:
                response = session.delete("/enclave", data=file.read())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text, "[DELETE] /enclave : Server response")

    def test_SecureSession_init_with_valid_params(self):
        # Assert that a cce policy needs to be provided when not in debug mode
        with self.assertRaises(ContentDecodingError):
            session = SecureSession("https://example.com")
            self.assertEqual(session.base_url, "https://example.com")

    def test_SecureSession_init_with_missing_addr(self):
        with self.assertRaises(ValueError):
            session = SecureSession(None)

    def test_connect(self):
        session = connect("https://example.com", None, debug_mode=True)
        self.assertIsInstance(session, SecureSession)
        self.assertEqual(session.base_url, "https://example.com")

if __name__ == '__main__':
    unittest.main()
