from blindbox.requests.secure_session import SecureSession
from blindbox.requests import requests


SERVER_URL = "localhost"
SERVER_PORT = 8080
TEST_WAV = "tests/test.wav"
DEBUG = True


with SecureSession(f"http://{SERVER_URL}:{SERVER_PORT}", "./cce_policy.txt", "sampleAttester.eus.attest.azure.net", DEBUG) as secure_session:

    res = secure_session.post(endpoint="/enclave/predict", files={"audio": open(TEST_WAV, "rb")})
    print(res.status_code)
    print(res.text)

    res = secure_session.get("/enclave")
    print(res.status_code)
    print(res.text)

if DEBUG == False:
    res = requests.post(url=f"http://{SERVER_URL}:{SERVER_PORT}/enclave/predict", cce_policy="./cce_policy.txt", files={"audio": open("test.wav", "rb")})
    print(res.status_code)
    print(res.text)

    res = requests.get(f"http://{SERVER_URL}:{SERVER_PORT}/enclave", "./cce_policy.txt")
    print(res.status_code)
    print(res.text)
