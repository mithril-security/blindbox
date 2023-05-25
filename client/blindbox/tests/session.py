from blindbox.requests  import SecureSession, requests

SERVER_URL = "localhost"
SERVER_PORT = 8080

with SecureSession(f"http://{SERVER_URL}:{SERVER_PORT}", "./cce_policy.txt", "sampleAttester.eus.attest.azure.net", True) as secure_session:

    res = secure_session.post(endpoint="/enclave/predict", files={"audio": open("test.wav", "rb")})
    print(res.status_code)
    print(res.text)

    res = secure_session.get("/enclave")
    print(res.status_code)
    print(res.text)


res = requests.post(url=f"http://{SERVER_URL}:{SERVER_PORT}/enclave/predict", files={"audio": open("test.wav", "rb")})
print(res.status_code)
print(res.text)

res = requests.get(url=f"http://{SERVER_URL}:{SERVER_PORT}/enclave")
print(res.status_code)
print(res.text)
