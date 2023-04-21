We will soon provide a CLI tool to deploy your own server logic on AWS Nitro Enclaves.
In the meantime, you can have a look at our example deployment in the `ai_server_example` folder
and play with it using our python client.

The example server can be deployed using terraform:
```bash
export AWS_ACCESS_KEY_ID="Your key"
export AWS_SECRET_ACCESS_KEY="Your secret"
terraform apply
```

The client can be installed from PyPI:
```bash
pip install blindbox[ai]
```
