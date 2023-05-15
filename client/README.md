<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Apache License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/mithril-security/blindbox">
    <img src="https://github.com/mithril-security/blindai/raw/main/docs/assets/logo.png" alt="Logo" width="80" height="80">
  </a>

<h1 align="center">Blindbox</h1>

[![Website][website-shield]][website-url]
[![Blog][blog-shield]][blog-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

  <p align="center">
    <b>Quickly deploy your SaaS solutions while preserving your users' data privacy.
	<br /><br />
    <a href="https://blindbox.mithrilsecurity.io/en/latest"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://blindbox.mithrilsecurity.io/en/latest/docs/getting-started/quick-tour/">Get started</a>
    ·
    <a href="https://github.com/mithril-security/blindbox/issues">Report Bug</a>
    ·
    <a href="https://github.com/mithril-security/blindbox/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#-about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#-getting-started">Getting Started</a>
    </li>
    <li><a href="#-getting-help">Getting Help</a></li>
	<li><a href="#-why-trust-us">Why trust us?</a></li>
    <li><a href="#-license">License</a></li>
    <li><a href="#-contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## 🔒 About The Project

**BlindBox** is a **privacy deployment** solution for **SaaS applications** which preserves the **data confidentiality** of end users, even from the software provider. To guarantee that privacy, we deploy those applications within **hardware based, highly-isolated** environments, a technology often referred to as **confidential computing**.

| ⚠️ **WARNING:** BlindBox is still under development. **Do not use in production!** |
| --- |

🗝️ **Key features**:

+ A **CLI tool** to deploy **application images** within **BlindBox**. We currently support **Docker** and we are working on other formats, like Kubernetes.

+ Applications are deployed within **Confidential VMs**, a type of confidential computing environment, which support additional security verifications.

+ An **isolation layer** to define **custom security policies** for the application inside the enclave. This will include selecting who can query the service running in the BlindBox and the range of networking access allowed within.

> You can check out [the project code on our GitHub](https://github.com/mithril-security/blindbox/).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## 🚀 Getting Started

We recommend for you to get started with our [Quick tour](https://blindbox.mithrilsecurity.io/en/latest/docs/getting-started/quick-tour/)!

<!-- GETTING HELP -->
## 🙋 Getting help

* Go to our [Discord](https://discord.com/invite/TxEHagpWd4) #support channel
* Report bugs by [opening an issue on our BlindBox GitHub](https://github.com/mithril-security/blindbox/issues)
* [Book a meeting](https://calendly.com/contact-mithril-security/15mins?month=2023-03) with us

<!-- TRUST US -->
## ❓ Why trust us?

* **Our core security features are open source.** We believe that transparency is the best way to ensure security and you can inspect the code yourself on our [GitHub page](https://github.com/mithril-security/blindbox).

* **Our historical project [BlindAI](https://blindbox.mithrilsecurity.io/en/latest/docs/past-projects/blindai/) was successfully audited** by Quarkslab. Although both projects differ (BlindAI was meant for the confidential deployment of ONNX models inside Intel SGX enclaves), we want to highlight that we are serious about our security standards and know how to code secure remote attestation.


<!-- LICENSE -->
## 📜 License

Distributed under the Apache License, version 2.0. See [`LICENSE.md`](https://www.apache.org/licenses/LICENSE-2.0) for more information.


<!-- CONTACT -->
## 📇 Contact

Mithril Security - [@MithrilSecurity](https://twitter.com/MithrilSecurity) - contact@mithrilsecurity.io

Project Link: [https://github.com/mithril-security/blindbox](https://github.com/mithril-security/blindbox)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://github.com/alexandresanlim/Badges4-README.md-Profile#-blog- -->
[contributors-shield]: https://img.shields.io/github/contributors/mithril-security/blindbox.svg?style=for-the-badge
[contributors-url]: https://github.com/mithril-security/blindbox/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/mithril-security/blindbox.svg?style=for-the-badge
[forks-url]: https://github.com/mithril-security/blindbox/network/members
[stars-shield]: https://img.shields.io/github/stars/mithril-security/blindbox.svg?style=for-the-badge
[stars-url]: https://github.com/mithril-security/blindbox/stargazers
[issues-shield]: https://img.shields.io/github/issues/mithril-security/blindbox.svg?style=for-the-badge
[issues-url]: https://github.com/mithril-security/blindbox/issues
[license-shield]: https://img.shields.io/github/license/mithril-security/blindbox.svg?style=for-the-badge
[license-url]: https://github.com/mithril-security/blindbox/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-Jobs-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/company/mithril-security-company/
[website-url]: https://www.mithrilsecurity.io
[website-shield]: https://img.shields.io/badge/website-000000?style=for-the-badge&colorB=555
[blog-url]: https://blog.mithrilsecurity.io/
[blog-shield]: https://img.shields.io/badge/Blog-000?style=for-the-badge&logo=ghost&logoColor=yellow&colorB=555
[product-screenshot]: images/screenshot.png
[Python]: https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue
[Python-url]: https://www.python.org/
[Rust]: https://img.shields.io/badge/rust-FFD43B?style=for-the-badge&logo=rust&logoColor=black
[Rust-url]: https://www.rust-lang.org/fr
[Intel-SGX]: https://img.shields.io/badge/SGX-FFD43B?style=for-the-badge&logo=intel&logoColor=black
[Intel-sgx-url]: https://www.intel.fr/content/www/fr/fr/architecture-and-technology/software-guard-extensions.html
[Tract]: https://img.shields.io/badge/Tract-FFD43B?style=for-the-badge
[tract-url]: https://github.com/mithril-security/tract/tree/6e4620659837eebeaba40ab3eeda67d33a99c7cf

<!-- Done using https://github.com/othneildrew/Best-README-Template -->
