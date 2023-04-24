# How does BlindBox protect your data?
_________________________________

BlindBox protects user data by leveraging the power of confidential computing, a fast-growing new technology in cybersecurity. Let’s take a look at what Confidential Computing is and how it protects your data.

The [Confidential Computing Consortium](https://confidentialcomputing.io/) (CCC) describes confidential computing as “the protection of data in use by performing computations in a hardware-based Trusted Execution Environment (TEE)”.

## What is a Trusted Execution Environment?
____________________________________

A **TEE**, otherwise known as a secure enclave, is a **highly isolated compute environment** in which data and applications can reside and run. Data sent to the enclave is only decrypted inside the enclave. Even if hackers or malicious insiders gain access to the host machine an enclave is running on, they will not be able to access data inside the enclave.

![Trusted Execution Environment](../../assets/TEE.png)

## Attestation
___________________

When a user wants to establish communication with an enclave, checks will first be performed to **verify the authenticity** of **the enclave identity and the application** running inside. 

!!! warning "Important"

	<font size="3">
	The goal of this process is to check that the code running is indeed the code of the application we are expecting and that it has not been tampered with. The attestation doesn't **audit the application code itself**. You could compare it to using a checksum utility when you download a software.
	</font>

With Nitro enclaves, specifically, the attestation will also verify the **trusted OS**.

If any of these **checks fail**, an error is produced and the **user will not be able to communicate with an enclave**. In terms of BlindBox, this means that a user would not be able to connect to a BlindBox server that has been tampered with or is not running the official latest version of that server. If these checks are **successful**, the user is able to **communicate** with the enclave **securely using TLS**. The enclave's private key never leaves the enclave, so it is never accessible to anyone, including the cloud or service provider.

## Limitations
__________________________

With great security features come great responsibilities! TEEs also have limitations which are very important to know:

+ The **enclave application code must be trusted**! The attestation process verifies that the enclave is running the official enclave application, but it does not run any checks on what the verified application code does.

### Nitro Enclaves

+ **AWS, as the cloud provider, their hardware and the enclave’s OS** must be **trusted**. That is because Nitro enclaves are designed to separate and isolate the host from the enclave and vice versa, but they do not protect against the cloud operator (AWS) or infrastructure. (*See our [Nitro guide](https://blindbox.mithrilsecurity.io/en/latest/docs/concepts/Trusted_Execution_Environments/#nitro-enclaves) for more information.*)

+ While **Nitro enclaves** limit operations within enclaves by default (such as no durable storage, no network/interactive access), any of these features can be added back into an enclave application by the application provider, so we cannot assume a Nitro enclave will never have any of these features.

## Conclusions
___________________________________________

That brings us to the end of this introduction to confidential computing. Let’s sum up what we’ve covered:

- Trusted Execution Environments are **highly isolated compute environments**.
- During the attestation process, we **verify that the enclave application code** in the enclave has not been modified or tampered with.
- We also **verify the authenticity of the enclave configuration and OS**.
- If attestation is successful, **communication** between the client and enclave is **established using TLS**.
- TEEs, like any other technology, are not without some limitations. It is important to keep them in mind.

If you haven’t already, you can check out our [Quick Tour](quick-tour.ipynb) to see a hands-on example of how BlindBox can be used to protect user data while querying AI models.