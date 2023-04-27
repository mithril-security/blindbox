# Protecting data with Confidential Computing
_________________________________

BlindBox protects user data by leveraging the power of [confidential computing](https://en.wikipedia.org/wiki/Confidential_computing), a fast-growing new technology in cybersecurity. Let’s take a look at what Confidential Computing is and how it protects your data.


The [Confidential Computing Consortium](https://confidentialcomputing.io/) (CCC) describes confidential computing as “the protection of data in use by performing computations in a hardware-based Trusted Execution Environment (TEE)”.

## What is a Trusted Execution Environment?
____________________________________


A **Trusted Execution Environment (TEE)**, otherwise known as a secure enclave, is a **highly isolated compute environment** in which data and applications can reside and run. Data sent to the enclave is only decrypted inside the enclave. Even if hackers or malicious insiders gain access to the host machine an enclave is running on, they will not be able to access data inside the enclave.


![Trusted Execution Environment](../../assets/TEE.png)

## TEEs providers
______________________


For this first version of BlindBox, we have used the following TEEs: **Nitro enclaves** developed **by AWS**  and the **AMD SEV-SNP confidential VM**. But there are other TEEs providers such as **Intel-SGX** (which we're very familiar with since this is the technology used in our historical product, BlindAI) and **Nvidia confidential GPUs** (a new take on TEEs promised for 2023).

> To learn more about Nitro enclaves, check out our guide [here](../concepts/nitro-enclaves.md).
> To learn more about AMD SEV-SNP, check out our guide [here](../concepts/amd-sev.md).

## Attestation
___________________

When a user wants to establish communication with an enclave, checks will first be performed to **verify the authenticity** of **the enclave identity and anything running inside the enclave** such as the **application** and **the trusted OS (where relevant)**. This is called the attestation.

!!! warning "Important"
    <font size="3">
    The goal of this process is to check that the code running is indeed the code of the application we are expecting and that it has not been tampered with. The attestation doesn't **audit the application code itself**. You could compare it to using a checksum utility when you download a software.
    </font>


❌ If any of these **checks fail**, an error is produced and the **user will not be able to communicate with the enclave**. For BlindBox, this means that a user would not be able to connect to a BlindBox server that has been tampered with or is not running the official latest version of that server.


✔️ If these checks are **successful**, the user is able to **communicate** with the enclave **securely using TLS**. The enclave's private key never leaves the enclave, so it is never accessible to anyone, including the cloud or service provider.

## Trusted Computing Base

_________________________

One strategy to reduce the enclave's attack surface pursued by many CC solutions is reducing the Trusted Computing Base (TCB).

### So what is the TCB?

Normally, when you run an application on a computer, you need to trust multiple elements: the application itself, the operating system, the hypervisor and the hardware. This doesn't mean we "trust" them in the everyday sense of the word- this means that our application could be affected by a bug or vulnerability in these elements! These trusted elements makes up what we call the Trusted Computing Base or TCB of our application.

## Limitations
__________________________

With great security features come great responsibilities! TEEs also have limitations which are very important to know.

+ The **enclave application code *must* be trusted**! The attestation process verifies that the enclave is running the official enclave application, but it does not run any checks on what the verified application code does.

This is why we are currently working on adding a customizable sandbox layer where data owners will be able to apply security policies to their BlindBox. This will include who can query the service in their BlindBox and networking access allowed to the application running within the enclave. This puts the data owner in control and removes the need to blindly trust the SaaS provider and their application code.

![VPS arch](../../assets/vps-archg.png)


+ There are also two important Nitro enclaves specific limitations that we cover in [the following concept guide](https://blindbox.mithrilsecurity.io/en/latest/docs/concepts/Trusted_Execution_Environments/nitro-enclaves)!


## Conclusions
___________________________________________

That brings us to the end of this introduction to confidential computing. Let’s sum up what we’ve covered:

- Trusted Execution Environments are **highly isolated compute environments**.
- During the attestation process, we **verify that the enclave application code** in the enclave has not been modified or tampered with.
- We also **verify the authenticity of the enclave configuration and OS**.
- If attestation is successful, **communication** between the client and enclave is **established using TLS**.
- TEEs, like any other technology, are **not without some limitations**. It is important to keep them in mind.

If you haven’t already, you can check out our [Quick Tour](quick-tour.ipynb) to see a hands-on example of how BlindBox can be used to protect user data while querying AI models.