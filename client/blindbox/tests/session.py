from blindbox.requests  import SecuredSession

with SecuredSession("http://localhost:8080", True) as secure_session:

    res = secure_session.post(endpoint="/enclave/predict", files={"audio": open("test.wav", "rb")})
    print(res.status_code)
    print(res.text)

    res = secure_session.get("/enclave")
    print(res.status_code)
    print(res.text)
