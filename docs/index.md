---
description: "BlindBox: Secure SaaS deployment for data privacy. Features confidential environments and user data protection."
---

# 👋 Welcome to BlindBox!
________________________________________________________

<font size="5"><span style="font-weight: 200">
Deploy and isolate software to preserve your users' data privacy!
</font></span>

## ⬛ What is BlindBox?
________________________________________________________
**BlindBox** is a **SaaS deployment solution** which boosts compliance and improves the security posture of SaaS solutions by shielding SaaS end users' data at all times- even from the SaaS provider itself!

🗝️ **Key features**:

+ A **CLI tool** to deploy **application images** within **BlindBox**. We currently support **Docker** and we are working on other formats, like Kubernetes.

+ Applications are deployed within **Confidential VMs**, a type of confidential computing environment, which support additional security verifications.

+ An **isolation layer** to define **custom security policies** for the application inside the enclave. This will include selecting who can query the service running in the BlindBox and the range of networking access allowed within.

> You can check out [the project code on our GitHub](https://github.com/mithril-security/blindbox/).

!!! warning
	
	BlindBox is still under development. **Do not use in production!**

### How does it work?

BlindBox faciliates the deployment of SaaS applications within **hardware based, highly-isolated** environments with stringent code and environment verification checks by using **confidential computing technologies**. This environment acts as a shield, protecting user data from any outside access, even during computation! We also implement customizable network isolation within this environment so data owners can control what applications can do within the environment.

### Why BlindBox?

+ BlindBox allows SaaS providers to offer their solutions to clients with strict compliance requirements, who previously were unable to benefit from Cloud-based solutions due to the risk of data leakage.
+ Significantly improves cybersecurity posture of SaaS solutions by reducing risk of data exposure.
+ BlindBox makes deployment in a confidential environment simple- we handle the deployment, isolation and attestation processes! All the SaaS provider needs to provide is their application image.

## 🚀 Getting started
________________________________________________________

- Try our [“Quick tour”](./docs/getting-started/quick-tour.ipynb) API demo
- [Discover](./docs/getting-started/confidential_computing.md) the technologies we use to ensure privacy

## 🙋 Getting help
________________________________________________________

- Go to our [Discord](https://discord.com/invite/TxEHagpWd4) *#support* channel
- Report bugs by [opening an issue on our BlindBox Github](https://github.com/mithril-security/blindbox/issues)
- [Book a meeting](https://calendly.com/contact-mithril-security/15mins?month=2022-11) with us

<!--
## 📚 How is the documentation structured?
____________________________________________
<!--
- [Tutorials](./docs/tutorials/core/installation.md) take you by the hand to install and run BlindBox. We recommend you start with the **[Quick tour](./docs/getting-started/quick-tour.ipynb)** and then move on to the other tutorials!  

- [Concepts](./docs/concepts/nitro-enclaves.md) guides discuss key topics and concepts at a high level. They provide useful background information and explanations, especially on cybersecurity.

- [How-to guides](./docs/how-to-guides/deploy-API-server.md) are recipes. They guide you through the steps involved in addressing key problems and use cases. They are more advanced than tutorials and assume some knowledge of how BlindBox works.

- [API Reference](https://blindai.mithrilsecurity.io/en/latest/blindai/client.html) contains technical references for BlindAI’s API machinery. They describe how it works and how to use it but assume you have a good understanding of key concepts.

- [Security](./docs/security/remote_attestation/) guides contain technical information for security engineers. They explain the threat models and other cybersecurity topics required to audit BlindBox's security standards.

- [Advanced](./docs/how-to-guides/build-from-sources/client/) guides are destined to developers wanting to dive deep into BlindBox and eventually collaborate with us to the open-source code.

- [Past Projects](./docs/past-projects/blindai) informs you of our past audited project BlindAI, of which BlindBox is the evolution. 
-->

## ❓ Why trust us?
___________________________

+ **Our core security features are open source.** We believe that transparency is the best way to ensure security and you can inspect the code yourself on our [GitHub page](https://github.com/mithril-security/blindbox).

+ **Our historical project [BlindAI](docs/past-projects/blindai.md) was successfully audited** by Quarkslab. Although both projects differ (BlindAI was meant for the confidential deployment of ONNX models inside Intel SGX enclaves), we want to highlight that we are serious about our security standards and know how to code secure remote attestation.

## 🔒 Who made BlindBox?

BlindBox was developed by **Mithril Security**. **Mithril Security** is a startup focused on AI privacy solutions based on **Confidential Computing** technology. We provide several **open-source tools** for **querying** and **deploying AI solutions** while **guaranteeing data privacy**.