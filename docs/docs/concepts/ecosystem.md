# The Confidential Computing ecosystem
_______________________________

??? abstract "Learn more about Confidential Computing 📖" 

	+ [Our intro to Confidential Computing](../getting-started/confidential_computing.md)
	+ [A guide to AMD-SEV](./amd-sev.md)
	+ [Confidential Computing Explained](https://confidential-computing-explained.mithrilsecurity.io/en/latest/), a hands-on course to learn how enclaves work and how to create your own mini-KMS

## Introduction
_______________

This section presents a brief overview of the Confidential Computing landscape and covers how BlindBox fits in that space. 

> Check [our intro to Confidential Computing](../getting-started/confidential_computing.md) if you are not familiar with Confidential Computing.


| BlindBox Compatibility | Azure | GCP | AWS |
| :--------------------- | :---- | :-- | :-- |
| `AMD SEV SNP`       | :material-check: Supported  | :material-timer-sand: Under test | :grey_question: Not tested yet | 
| `AWS Nitro Enclave`       | :material-close: NA[^1]  | :material-close:  NA | :material-check: Supported | 
| `Nvidia Confidential GPU`     | :material-timer-sand: Under test | :material-close: NA  | :material-close:  NA |
| `Intel SGX`     | :material-check: Supported (with [BlindAI](../past-projects/blindai.md)) | :material-close: NA  | :material-close:  NA |
| `Intel SGX`     | :grey_question: Not tested yet | :grey_question: Not tested yet | :material-close:  NA |

[^1]: NA: Not available.

## Hardware
_________________

Currently, most hardware providers offer server-side CPUs with confidential computing abilities: 

+ **Intel** was the first with [**SGX/TDX**](https://blindai.mithrilsecurity.io/en/latest/docs/concepts/SGX_vs_Nitro/#intel-sgx) enclaves, available on Xeon. 
+ **AMD** came up with [**SEV**](./amd-sev.md) on EPYC, a solution they call Confidential VMs. 
+ **AWS** provides [**Nitro Enclaves**](./nitro-enclaves.md), a solution at the Hypervisor level which isolate sensitive workloads.
+ **Nvidia** is coming with yet another tech: **Confidential GPUs**. They announced the **H100**, but the software libraries are not stable at the moment[^2].

[^2]: 10 May 2023.

??? question "A Confidential Computing terminology guide 📚"

	<font size="3"> 
	All the technical terms surrounding confidential computing can be confusing. You'll see people referring to **secure enclaves**, preaching **TEEs** and suddenly switching to **Confidential Containers**. 

	+ **Enclaves**: Intel SGX was the first in the space so their *enclave* terminology stuck. But not all everything that calls itself an enclave is actually an enclave (for example, AWS Nitro 'Enclaves' work very differently from Intel SGX). This is why we think *enclave* might end up being the winner terminology to popularize those technologies at a higher level.

	+ **Confidential VMs**:

	+ **Confidential Containers**: it's just another name for Confidential VMs when they specifically are containers. 

	+ **Trusted Execution Environment** (TEE):
	</font>

## Cloud
_____________________

Most major Cloud providers also created their own flavor of Confidential Computing solutions. They allow SaaS vendors to access a machine with the right hardware easily (the 'right' hardware being one of the biggest barrier of entry to use confidential computing).

- **Azure** went with **Azure Confidential Computing**
- **GCP** offers **GCP Confidential Computing**
- **AWS** proposes **AWS Nitro Enclave**

It's important to note that those offers mostly cover the infrastructure level of confidential computing abilities. Developers using them **have to implement** complex security features such as attestation or sealing.


## BlindBox position
_________________

It can be complicated for inexperienced developers to properly implement key confidential computing functions, like isolation, attested TLS with remote attestation and sealing because Confidential Computing uses low-level hardware primitives. 

This is where BlindBox comes in. It provides an easy-to-use secure enclave tooling solution to leverage the confidential infrastructure of Cloud providers. Its abstraction layer allows SaaS vendors to deliver an on-premise level of security and control to users of their software.

![blindbox_position_in_ecosystem](../../assets/BlindBox_ecosystem_place.png)

At the moment, BlindBox is still under development so it's not usable in production and only compatible with Azure Confidential VMs. But we aim for it to be hardware and Cloud agnostic. 
