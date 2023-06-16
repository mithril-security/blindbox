# import requests module
from blindbox.requests import SecureSession

# replace the IP address here with the public IP address of your confidential VM which you can find on your Azure portal
CONFIDENTIAL_VM_IP_ADDRESS = "0.0.0.0:80" #port should always be 80 to use blindbox
POLICY="./cce_policy.txt"

# we query our application with out user prompt
with SecureSession(f"http://{CONFIDENTIAL_VM_IP_ADDRESS}", POLICY) as secure_session:
    res = secure_session.post(endpoint="/test", json={"input_text": "Write me a poem about Valencia"})
    print(res.text)