from blindbox.requests  import SecureSession, requests

with SecureSession("http://20.223.63.77:80", "./cce_policy.txt",True) as secure_session:

    res = secure_session.post(endpoint="/whisper/predict", files={"audio": open("test.wav", "rb")})
    print(res.status_code)
    print(res.text)

    #res = secure_session.get("/enclave")
    #print(res.status_code)
    #print(res.text)


res = requests.post(url="http://localhost:8080/enclave/predict", files={"audio": open("test.wav", "rb")})
print(res.status_code)
print(res.text)

res = requests.get(url="http://localhost:8080/enclave")
print(res.status_code)
print(res.text)


