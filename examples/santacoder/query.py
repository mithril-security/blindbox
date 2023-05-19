# import requests module
from blindbox  import requests

# replace the IP address here with the public IP address of your confidential VM which you can find on your Azure portal
CONFIDENTIAL_VM_IP_ADDRESS = "127.0.0.1:80"

# we query our application, sending it a snippet of code to be completed by the model
res = requests.post(url=f"http://{CONFIDENTIAL_VM_IP_ADDRESS}/generate", json={"input_text": "def print_hello_world():"})

# force the interpretation of new lines
output = res.text.replace('\\n', '\n')

# display result
print(output)