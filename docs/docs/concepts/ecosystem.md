# The Confidential Computing ecosystem
_______________________________

??? abstract "Learn more about Confidential Computing 📖" 

	+ [Our intro to Confidential Computing](../getting-started/confidential_computing.md)
	+ [A guide to AMD-SEV](./amd-sev.md)
	+ [Confidential Computing Explained](https://confidential-computing-explained.mithrilsecurity.io/en/latest/), a hands-on course to learn how enclaves work and how to create your own mini-KMS

This section presents a brief overview of the Confidential Computing landscape and covers how BlindBox fits in that space. 

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

> Check [our intro to Confidential Computing](../getting-started/confidential_computing.md) if you are not familiar with Confidential Computing.

Currently, most hardware providers provide server-side CPUs with confidential computing abilities. Intel has Intel SGX/TDX available on Xeon. AMD offers AMD SEV on AMD EPYC. 

Currently, most CPU providers, such as Intel and AMD, provide server-side CPUs with secure enclave ability, called Intel SGX/TDX, available on Xeon, or AMD SEV on AMD EPYC.

Confidential GPUs from Nvidia are coming with the H100, but the software libraries are not stable at the moment of this writing (May 2023).

AWS provides Nitro Enclaves, a hardware-based solution at the Hypervisor level to isolate sensitive workloads.

## Cloud
_____________________

Each major Cloud provider provides its own flavor of Confidential Computing for SaaS vendors to access a machine with the right hardware easily.

- Azure Confidential Computing
- GCP Confidential Computing
- AWS Nitro Enclave

While those offers exist on the main Cloud providers, they are mostly at the infrastructure level, with for instance, Confidential VMs, but developers have to implement complex security features such as attestation or sealing.


## BlindBox compatibility
_________________

BlindBox is a secure enclave tooling providing an abstraction layer for software vendors to provide an on-prem level of security and control to users of their SaaS.

As Confidential Computing uses low-level hardware primitives, it can be complicated for inexperienced developers to properly implement key functions, like proper isolation, attested TLS with remote attestation, sealing, and so on.

That is why BlindBox provides an easy-to-use solution to easily harden SaaS workloads for SaaS vendors. BlindBox aims to be hardware and Cloud agnostic. It is made to leverage the Confidential infrastructure of those Cloud vendors, for instance, with a solution able to deploy workloads on Azure Confidential Containers.



Mithril Security provides the tooling for SaaS vendors to provide a Virtual Private SaaS that provides an on-prem level of security. Our objective is not to be a trusted third party in the usual sense where we see data, but rather to provide the security layer for SaaS vendors to address directly demanding organizations with our software.
