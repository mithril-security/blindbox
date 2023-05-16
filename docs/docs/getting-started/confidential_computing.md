# How we protect your data
_________________________________

BlindBox protects user data with two key elements: 

+ By leveraging **confidential computing** technologies to deploy applications within secure hardware-based highly-isolated environment called **secure enclaves** or **Trusted Execution Environments (TEEs)**.
+ By allowing data owners to set **custom security policies** to control what can happen inside of their BlindBox enclave.

Let's now take a look at the technologies behind our solution and how they protect user data!

## Confidential Computing
__________________________

In typical workflows, data may be encrypted in transit, but it is accessible in clear when being analyzed by software. [Confidential computing](https://en.wikipedia.org/wiki/Confidential_computing) is a fast-growing new technology which aims to tackle this problem and protects data during computation.

Solutions usually center around three key concepts.

+ **Isolation**: data is processed in highly-isolated Trusted Execution Environments.
+ **Attestation**: we verify the authenticity of the Trusted Execution Environments and its components. 
+ **Runtime encryption**: data is encrypted, even during analysis.

Let's dive into a bit more detail about these concepts.

## Isolation
____________________________________

In a confidential workflow, data is sent to and analyzed within a **Trusted Execution Environment (TEE)**, otherwise known as a secure enclave. Data sent to the enclave is only decrypted in isolated environments or when being processed. Even if hackers or malicious insiders gain access to the host machine an enclave is running on, they will not be able to access data inside the enclave.

![TEE_dark](../../assets/TEE_dark.png#only-dark)
![TEE_light](../../assets/TEE_light.png#only-light)

We currently support the following TEEs: **[AMD SEV-SNP](../concepts/amd-sev.md) confidential VM**.

## Attestation
___________________

When a user wants to establish communication with an enclave, checks can be performed to **verify the authenticity of the TEE**, **its configuration** and elements such as the  **application** running in the TEE and **the OS (where relevant)**. This process is called attestation.

!!! warning "Important"

	<font size="3">
    Where attestation verifies the application code, the goal is to check that the code running is indeed the expected application code and that it has not been tampered with. The attestation doesn't **audit the application code itself**. You could compare it to using a checksum utility when you download a software.
	</font>


❌ If any of these **checks fail**, an error is produced and the **user will not be able to communicate with the enclave**. For BlindBox, this means that a user will only be able to connect to a genuine, verified TEE.

✔️ If these checks are **successful**, the user is able to **communicate** with the enclave **securely using TLS**. The enclave's private key never leaves the enclave, so it is never accessible to anyone, including the cloud or service provider!

Let's take a look at the basic attestation workflow for BlindBox:

![attest_light](../../assets/attest_light.png#only-light)
![attest_dark](../../assets/attest_dark.png#only-dark)

1. When a user queries a BlindBox application, our client will attempt to **create a connection** between the user and the application running in the BlindBox. This will **trigger the attestation process**. 

2. The TEE will be asked to **generate a report to prove its identity**. This report is signed by keys derived from hardware.

3. This **report and a TLS certificate**, which will be used for communications if attestation is successful, are **sent** back to the client.

4. A **verification process** is **triggered**, where the client will check the **TEE is authentic** and has the expected identity and settings.

5. **If** the verification process is **successful**, **communication via TLS is established** and the query will be performed. **If** the verification process **fails**, an attestation **error** will be returned.

Here, we were able to transcribe our audio file while keeping the audio file confidential, even from the SaaS vendor!

## Verifying security
___________________________________________ 

BlindBox is under development, so this code is still being implemented, but we wanted to give you a clear illustration of **what will happen when the Confidential VM is not secure**. 

+ If we talk to a server without signature from the hardware provider (meaning it has no collateral to prove it is secure), then an error will be raised:

	```python
	import blindbox.requests as requests

	CONFIDENTIAL_VM_IP = "127.0.0.1:8080" # replace with your VM IP address + port

	session = requests.SecureSession(addr=CONFIDENTIAL_VM_IP)

	>> NotAnEnclaveError
	```

+ If the first check passes, but the hash of the code is not the publicly available hash of BlindBox, another error will be raised:

	```python
	import blindbox.requests as requests

	CONFIDENTIAL_VM_IP = "127.0.0.1:8080" # replace with your VM IP address + port

	session = requests.SecureSession(addr=CONFIDENTIAL_VM_IP)

	>> InvalidEnclaveCode
	```

## [Coming Soon ⌛] BlindBox security features

+ BlindBox with **remote attestation** is on its way! Attestation will be performed when users connect to a BlindBox to verify the authenticity of their BlindBox and TEE environment.

+ **Attested network isolation**: We will add an additional layer to our attestation process where we will verify that the BlindBox we are connecting to has the expected security policies in place.

+ **Data owner security policies**: We'll wrap application images in an **additional security layer** which enforces custom security policies. These custom policies will allow the data owner to set up:
	+ **Authentication**: Data owners will be able to specify who should be able to query their BlindBox.
	+ **Outward-bound network isolation**: Data owners will be able to whitelist external domains that the SaaS application may contact if necessary. Any calls to external domains not on this whitelist will be blocked.

![blindbox_architecture_light](../../assets/blindbox_arch_light.png#only-light)
![blindbox_architecture_dark](../../assets/blindbox_arch_dark.png#only-dark)

These security features allow us to offer a solution which is able to rival the security provided by on-premise SaaS deployment while retaining all the advantages of SaaS Cloud deployment!

<!--
## Limitations
__________________________

As discussed previously, the attestation process verifies the authenticity of the enclave, it does not run any checks on what the verified application code does. An enclave protects what is inside from the outside, but not what is inside from the inside.

This is why we wrap application images in an  an **additional security layer** to BlindBox, so developers can define **custom security policies** for protection. For example, they could decide who can query the service in their BlindBox or restrict networking access to the application running within the enclave.
-->

??? abstract "Learn more about Confidential Computing 📖" 

	+ [Discover the Confidential Computing ecosystem](../concepts/ecosystem.md)
	+ [A guide to AMD-SEV](../concepts/amd-sev.md)
	+ [Confidential Computing Explained](https://confidential-computing-explained.mithrilsecurity.io/en/latest/), a hands-on course to learn how enclaves work and how to create your own mini-KMS
