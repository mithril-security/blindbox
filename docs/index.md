# 👋 Welcome to BlindBox!
________________________________________________________

<font size="5"><span style="font-weight: 200">
Quickly deploy your SaaS solutions while preserving data privacy!
</font></span>

## ⬛ What is BlindBox?
________________________________________________________

**BlindBox** protects end users' data when using SaaS applications, even from software vendors themselves. We shield the user data sent to applications within **hardware based, highly-isolated** environments with additional customizable layers of protection. SaaS providers can use **BlindBox** to easily deploy their solution within our secure environment and offer their customers **stringent privacy guarantees**.

[Todo: Image]

In a typical SaaS set-up, malicious insiders or attackers who breach a software vendor could access the content of data being analyzed within SaaS applications. BlindBox protects user data against these risks, with data protected at all times, even during analysis.

🗝️ **Key features**:

+ A **CLI tool** for quick deployment of your **app images** within BlindBox. We currently support Docker but future formats will be supported, such as Kubernetes.

+ Applications are deployed within a Trusted Execution Environment (a TEE), a **hardware-based isolated** environment which supports additional security verifications.

+  An additional **isolation layer** to recreate virtual air-gapped network isolation that can be verified by data owners before sending data to the SaaS, allowing SaaS owners to provide **custom security policies** to their app. This will include, for example, selecting who can query the service running in the BlindBox and the range of networking access allowed within the BlindBox.

BlindBox is a generic tool which can be used to deploy any SaaS solution. Our mission is to reinforce any SaaS app to provide the same level of security, isolation and control as on-premise deployment.

With that being said, our primary focus is AI workloads, and more specifically LLM-based apps. We have created an example of how you can deploy an LLM model using BlindBox to protect user data in our quick tour!

> You can check out [the project code on our GitHub](https://github.com/mithril-security/blindbox/).


## 🚀 Getting started
________________________________________________________

- Try our [“Quick tour”](./docs/getting-started/quick-tour.ipynb) API demo
- [Discover](./docs/getting-started/confidential_computing.md) the technologies we use to ensure privacy
- Check out how the BlindBox demo API works [under the hood!](./docs/getting-started/under-the-hood.md)
- [Dive into](./docs/getting-started/why-blindbox.md) why we are developing BlindBox and its possible use cases

## 🙋 Getting help
________________________________________________________

- Go to our [Discord](https://discord.com/invite/TxEHagpWd4) *#support* channel
- Report bugs by [opening an issue on our BlindBox Github](https://github.com/mithril-security/blindbox/issues)
- [Book a meeting](https://calendly.com/contact-mithril-security/15mins?month=2022-11) with us


## 📚 How is the documentation structured?
____________________________________________
<!--
- [Tutorials](./docs/tutorials/core/installation.md) take you by the hand to install and run BlindBox. We recommend you start with the **[Quick tour](./docs/getting-started/quick-tour.ipynb)** and then move on to the other tutorials!  
-->

- [Concepts](./docs/concepts/nitro-enclaves.md) guides discuss key topics and concepts at a high level. They provide useful background information and explanations, especially on cybersecurity.

- [How-to guides](./docs/how-to-guides/deploy-API-server.md) are recipes. They guide you through the steps involved in addressing key problems and use cases. They are more advanced than tutorials and assume some knowledge of how BlindBox works.

<!--
- [API Reference](https://blindai.mithrilsecurity.io/en/latest/blindai/client.html) contains technical references for BlindAI’s API machinery. They describe how it works and how to use it but assume you have a good understanding of key concepts.

- [Security](./docs/security/remote_attestation/) guides contain technical information for security engineers. They explain the threat models and other cybersecurity topics required to audit BlindBox's security standards.

- [Advanced](./docs/how-to-guides/build-from-sources/client/) guides are destined to developers wanting to dive deep into BlindBox and eventually collaborate with us to the open-source code.
-->

- [Past Projects](./docs/past-projects/blindai) informs you of our past audited project BlindAI, of which BlindBox is the evolution. 

## 🔒 Who made BlindBox?

BlindBox was developed by **Mithril Security**. **Mithril Security** is a startup focused on AI privacy solutions based on **Confidential Computing** technology. We provide several **open-source tools** for **querying** and **deploying AI solutions** while **guaranteeing data privacy**.