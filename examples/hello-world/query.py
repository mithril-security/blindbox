# import requests module
from blindbox  import requests

# replace the IP address here with the public IP address of your confidential VM which you can find on your Azure portal
CONFIDENTIAL_VM_IP_ADDRESS = ""

if CONFIDENTIAL_VM_IP_ADDRESS == "":
    print("Warning!! You need to modify the query.py file to include your ip address and port for the CONFIDENTIAL_VM_IP_ADDRESS variable: e.g. \"127.0.0.1:8080\"")
else:

    # we query our application, sending it a snippet of code to be completed by the model
    res = requests.get(url=f"http://{CONFIDENTIAL_VM_IP_ADDRESS}/hello")

    # display result
    print(res.text)