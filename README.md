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
    <b>Quickly deploy your SaaS solutions while preserving your user's data privacy.
	<br /><br />
    <a href="https://blindbox.mithrilsecurity.io/en/latest"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://blindbox.mithrilsecurity.io/en/latest/docs/getting-started/quick-tour/">Try the demo</a>
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
    <li><a href="#-license">License</a></li>
    <li><a href="#-contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## 🔒 About The Project

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

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## 🚀 Getting Started

We recommend for you to get started with our [Quick tour](https://blindbox.mithrilsecurity.io/en/latest/docs/getting-started/quick-tour/)!

<!-- GETTING HELP -->
## 🙋 Getting help

* Go to our [Discord](https://discord.com/invite/TxEHagpWd4) #support channel
* Report bugs by [opening an issue on our Blindbox GitHub](https://github.com/mithril-security/blindbox/issues)
* [Book a meeting](https://calendly.com/contact-mithril-security/15mins?month=2023-03) with us


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
