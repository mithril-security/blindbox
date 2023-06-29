# Attestation

??? abstract "Learn more about Confidential Computing 📖" 

	+ [Our intro to Confidential Computing](../getting-started/confidential_computing.md)
	+ [Discover the Confidential Computing ecosystem](../concepts/ecosystem.md)
	+ [A guide to AMD SEV](../concepts/amd-sev.md)
	+ [Confidential Computing Explained](https://confidential-computing-explained.mithrilsecurity.io/en/latest/), a hands-on course to learn how enclaves work and how to create your own mini-KMS

The aim of this advanced guide is to cover [attestation](https://blindbox.mithrilsecurity.io/en/latest/docs/getting-started/confidential_computing/) and discuss how we implement it in BlindBox. 

!!! warning "Disclaimer"

	We currently only support the deployment of BlindBoxes on AMD SEV-SNP confidential VMs with Azure, so this guide will focus on attestation for these machines. We will update this guide as and when new platforms are supported.

## Who is responsible for attestation?

The attestation process is an **automated** process managed by BlindBox. Attestation is set-up to be performed by default whenever an end user starts a new connection to a BlindBox- from a customer perspective, no additional actions are required. If any of our attestation checks fail, the end user will be unable to connect to the BlindBox.

The BlindBox attestation process makes use of the Microsoft Azure Attestation service and Microsoft client-side attestation application, which in turn requests and leverages a attestation report produced by AMD SEV-SNP.

![att_architecture_light](../../assets/att_architecture_light.png#only-light)
![att_architecture_dark](../../assets/att_architecture_dark.png#only-dark)

## What do we attest?

The **Microsoft Azure Attestation service** attests the **validity of the AMD SEV-SNP report** by verifying the reports hardware-derived signature.

**BlindBox** attests that the **JWT attestation token response** we get back from the Microsoft Azure Attestation service has **not been tampered with** by verifying the token’s signature, validity and some runtime information.

BlindBox then uses the information provided in JWT attestation response to verify that:

+ We are **communicating** with a genuine **AMD SEV-SNP confidential VM**.
+ We are **communicating** with a **genuine Azure-compliant VM**.
+ The VM is **running** in **production mode** and *not* debug mode.

## The attestation workflow

Let’s walk through the whole life cycle of the attestation process from the moment an end user starts a new connection with a SaaS application deployed with BlindBox.

1. The end user queries the application. This triggers a new connection request, which in turn triggers the attestation process. 
2. BlindBox requests attestation using the Microsoft attestation library.
3. The Microsoft attestation library requests an attestation report from AMD SEV-SNP. This report is signed by a hardware-derived key. For more details about this report [here](#amd-sev-snp-attestation-report).
4. This report is then sent to the Microsoft Azure Attestation (MAA) Service.
5. MAA verifies the signature on this report, confirming that it was generated by genuine AMD SEV-SNP hardware. If this check is successful, MAA returns a signed JWT attestation token containing details about the SEV-SNP environment to the Microsoft attestation library. For more details about this report [here](#maa-attestation-token).
6. This token is then returned to BlindBox.
7. BlindBox verifies the validity of this token before using the report to perform the checks detailed above.
8. BlindBox returns an error if any of these checks are unsuccessful. If not, the end user will successfully connect to the BlindBox application and their query will be processed.

## What happens when attestation fails?

Let's take a look at what happens if the attestation process is not successful.

For an **interactive demo of the attestation process**, check out our [**Gradio demo**](https://huggingface.co/spaces/mithril-security/BlindBox).

### Non-compliant Azure VM

*Query:*
```python
res = requests.post(url=f"http://{CONFIDENTIAL_VM_IP_ADDRESS}/generate", json={"input_text": "def print_hello_world():"})
```

*Response:*
```bash
$ __main__.NonCompliantUvm: Attestation validation failed (non-compliant uvm). Exiting.
```

### Debug mode

*Query:*
```python
res = requests.post(url=f"http://{CONFIDENTIAL_VM_IP_ADDRESS}/generate", json={"input_text": "def print_hello_world():"})
```

*Response:*
```bash
$ __main__.DebugMode: Attestation validation failed (enclave is in debug mode). Exiting.
```

## Attestation reports

### AMD SEV-SNP Attestation Report

The AMD SEV-SNP attestation report contains information relating to the confidential environment our application is running within. It is signed by a Versioned Chip Endorsement Key (VCEK), which is derived from chip- unique secrets and a TCB_VERSION. 

To get all an outline of all the fields provided in the report, see page 44 of [AMD SEV-SNP’s technical documentation](https://www.amd.com/system/files/TechDocs/56860.pdf). The documentation also contains more information on the signature. 

### MAA Attestation Token

The attestation token response generated by the Microsoft Azure Attestation (MAA) service is a signed JSON Web Token containing information related to the Azure VM our application is deployed on and the confidential environment our application is running within. The latter information is taken from the AMD SEV-SNP attestation report once its signature has been verified by the MAA service. The attestation token is signed with a self-signed certificate with subject name matching the AttestUri element of the attestation provider.

Here is an example of a MAA attestation token:

```python
{
  "exp": 1653021894,
  "iat": 1652993094,
  "iss": "https://sharedeus.eus.test.attest.azure.net",
  "jti": "df7d7ed26168e8f550cac34c8f9a227da664429f5df50bf72db60b19621a9d55",
  "nbf": 1652993094,
  "secureboot": true,
  "x-ms-attestation-type": "azurevm",
  "x-ms-azurevm-attestation-protocol-ver": "2.0",
  "x-ms-azurevm-attested-pcrs": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    11,
    12,
    13
  ],
  "x-ms-azurevm-bootdebug-enabled": false,
  "x-ms-azurevm-dbvalidated": true,
  "x-ms-azurevm-dbxvalidated": true,
  "x-ms-azurevm-debuggersdisabled": true,
  "x-ms-azurevm-default-securebootkeysvalidated": true,
  "x-ms-azurevm-elam-enabled": true,
  "x-ms-azurevm-flightsigning-enabled": false,
  "x-ms-azurevm-hvci-policy": 0,
  "x-ms-azurevm-hypervisordebug-enabled": false,
  "x-ms-azurevm-is-windows": true,
  "x-ms-azurevm-kerneldebug-enabled": false,
  "x-ms-azurevm-osbuild": "NotApplicable",
  "x-ms-azurevm-osdistro": "Microsoft",
  "x-ms-azurevm-ostype": "Windows",
  "x-ms-azurevm-osversion-major": 10,
  "x-ms-azurevm-osversion-minor": 0,
  "x-ms-azurevm-signingdisabled": true,
  "x-ms-azurevm-testsigning-enabled": false,
  "x-ms-azurevm-vmid": "2DEDC52A-6832-46CE-9910-E8C9980BF5A7",
  "x-ms-isolation-tee": {
    "x-ms-attestation-type": "sevsnpvm",
    "x-ms-compliance-status": "azure-compliant-cvm",
    "x-ms-runtime": {
      "keys": [
        {
          "e": "AQAB",
          "key_ops": [
            "encrypt"
          ],
          "kid": "HCLAkPub",
          "kty": "RSA",
          "n": "r6rCrAAAxuVmTsLPG9Em43Ley0MHbjTNrbWfyczxo5yLs4obtrY7Gm0Cme4uPxFlEtL1tpFuCv8tg9DikczxjVmuMs9wZdsplIp9k559Wcb4jkaXjnbCx2YbXjIZHzueSRKkPg_JsiUOb0bD7I9S0gYgeKl5TZ-SXbJB2xkk3NpAu6CN4UPLBRuK_2giN-VIE0bu9P_9lleutmJtLmKo2-JXrafF605mKAwRlKYnkbZN0ZcICot1taa7L3W7gL8fPXJmyZIC8GMni22XGH484-u_gM3N-WadrZMLfK8sC9UCbmJUDzMwo1niKNGLkyl9y1ssdBuZER8NHbQ6LFslkQ"
        }
      ],
      "vm-configuration": {
        "console-enabled": true,
        "current-time": 1652993091,
        "secure-boot": true,
        "tpm-enabled": true,
        "vmUniqueId": "2DEDC52A-6832-46CE-9910-E8C9980BF5A7"
      }
    },
    "x-ms-sevsnpvm-authorkeydigest": "000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "x-ms-sevsnpvm-bootloader-svn": 2,
    "x-ms-sevsnpvm-familyId": "01000000000000000000000000000000",
    "x-ms-sevsnpvm-guestsvn": 1,
    "x-ms-sevsnpvm-hostdata": "0000000000000000000000000000000000000000000000000000000000000000",
    "x-ms-sevsnpvm-idkeydigest": "cd7cee161cad4160b883c9440db0920507aaab03ca6903fed8be467cf9d27b7ad0c69411a2c714ea5581f7fde86696fc",
    "x-ms-sevsnpvm-imageId": "02000000000000000000000000000000",
    "x-ms-sevsnpvm-is-debuggable": false,
    "x-ms-sevsnpvm-launchmeasurement": "fe353d3026450365d599293bf0ed9b97defc3976602750dff3e087d88b9bbde05031b356f8d9296b8b138ae6000d0370",
    "x-ms-sevsnpvm-microcode-svn": 55,
    "x-ms-sevsnpvm-migration-allowed": false,
    "x-ms-sevsnpvm-reportdata": "2065309a0fa9c05222a4455ecd25945995ee5f51952afb22e5661796d2704ee30000000000000000000000000000000000000000000000000000000000000000",
    "x-ms-sevsnpvm-reportid": "1d5a776d6997b1b2207f3858e6b4bfd18e5bca9e292eb86fd49d0b9fe99eafaf",
    "x-ms-sevsnpvm-smt-allowed": true,
    "x-ms-sevsnpvm-snpfw-svn": 2,
    "x-ms-sevsnpvm-tee-svn": 0,
    "x-ms-sevsnpvm-vmpl": 0
  },
  "x-ms-policy-hash": "wm9mHlvTU82e8UqoOy1Yj1FBRSNkfe99-69IYDq9eWs",
  "x-ms-runtime": {
    "keys": [
      {
        "e": "AQAB",
        "key_ops": [
          "encrypt"
        ],
        "kid": "TpmEphemeralEncryptionKey",
        "kty": "RSA",
        "n": "3j6coAAAH_rEZn4n2nAcPpGPF3i-c8OptjkPqzpLGCfwJAHCnYMzAKyhHqhBSx9PZIift3PY1ecbUUZjhAFM98e7EpRtGgMggql0itQf_tr2fy6tVJXv4w6kwCB4dX3Lnr2TKH4T-6TsbzEK-uTZLxbS5kzldYx5WRJBGhE1BW4jJXOB-QGHmCyH7jHIEP61RunHOEy8pmZcAcgvGHCt3AK2s166g0YolD-t9s4F3Kr3bnVh9hdc548DkHdGK0WLAq8wa2cXujzzWdRCnM8e3t95GbZFpwVQCOJm3dGm2yYlQe53W1Egdfll6ccipHQ1lCOWpFTOzOjPovQFkwpoaQ"
      }
    ]
  },
  "x-ms-ver": "1.0"
}
```

Here is a key to help you understand the fields we see in this token:

#### Initial fields

| Field | Description |
| --------- |---|
| **exp (Expiration)** | Time after which the JWT must not be accepted for processing |
| **iat (Issued at)** | The time at which the JWT was issued at |
| **iss (Issuer)** | The principal that issued the JWT |
| **jti (JWT ID)** | Unique identifier for the JWT |
| **nbf (Not Before)** | Time before which the JWT must not be accepted for processing |
| **secureboot** | Boolean value showing if VM is running in secure boot mode |
| **x-ms-attestation-type** | Attestation type |

#### x-ms-azurevm fields

Details relating to the configuration of the Azure VM.

#### x-ms-isolation-tee fields

Details relating to the TEE running on the Azure VM, including:

+ **x-ms-attestation-type**:  TEE type/provider
+ **x-ms-compliance-status**: Azure compliance status

#### x-ms-sevsnpvm fields

These are the fields relating to the AMD SEV-SNP attestation report. MAA parses this report and returns the following fields:

| Field | Description |
| --------- |---|
| **x-ms-sevsnpvm-authorkeydigest** | SHA384 hash of the author signing key |
| **x-ms-sevsnpvm-bootloader-svn** | AMD boot loader security version number (SVN) |
| **x-ms-sevsnpvm-familyId Host** | Compatibility Layer (HCL) family identification string |
| **x-ms-sevsnpvm-guestsvn** | HCL security version number (SVN) |
| **x-ms-sevsnpvm-hostdata** | Arbitrary data defined by the host at VM launch time |
| **x-ms-sevsnpvm-idkeydigest** | SHA384 hash of the identification signing key |
| **x-ms-sevsnpvm-imageId** | HCL image identification |
| **x-ms-sevsnpvm-is-debuggable** | Boolean value indicating whether AMD SEV-SNP debugging is enabled |
| **x-ms-sevsnpvm-launchmeasurement** | Measurement of the launched guest image |
| **x-ms-sevsnpvm-microcode-svn** | AMD microcode security version number (SVN) |
| **x-ms-sevsnpvm-migration-allowed** | Boolean value indicating whether AMD SEV-SNP migration support is enabled |
| **x-ms-sevsnpvm-reportdata** | Data passed by HCL to include with report, to verify that transfer key and VM configuration are correct |
| **x-ms-sevsnpvm-reportid** | Report ID of the guest |
| **x-ms-sevsnpvm-smt-allowed** | Boolean value indicating whether SMT is enabled on the host |
| **x-ms-sevsnpvm-snpfw-svn** | AMD firmware security version number (SVN) |
| **x-ms-sevsnpvm-tee-svn** | AMD trusted execution environment (TEE) security version number (SVN) |
|  **x-ms-sevsnpvm-vmpl** | Virtual Machine Privilege Levels (VMPL) that generated this report |

#### Final fields

| Field | Description |
| --------- |---|
| **x-ms-policy-hash** | Hash of Azure Attestation evaluation policy computed as BASE64URL(SHA256(UTF8(BASE64URL(UTF8(policy text))))) |
| **x-ms-runtime** | JSON object containing "claims" that are defined and generated within the attested environment |
| **x-ms-ver** | JWT schema version (expected to be "1.0") |

## Conclusions

This concludes our advanced guide into how attestation is implemented in BlindBox.

We have seen:

+ The role of each concerned party in attestation
+ What details are verified during the attestation process
+ The life cycle of the attestation process
+ What to expect if attestation fails

If you have any further questions, please get in touch! 