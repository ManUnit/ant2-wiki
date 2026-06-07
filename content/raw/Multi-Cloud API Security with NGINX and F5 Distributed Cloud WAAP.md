---
title: "Multi-Cloud API Security with NGINX and F5 Distributed Cloud WAAP"
source: "https://www.f5.com/company/blog/nginx/multi-cloud-api-security-with-nginx-and-f5-distributed-cloud-waap"
author:
published:
created: 2026-05-06
description: "Navigate the complexity of distributed environments and securely deliver APIs at scale with this three-tier approach to hybrid and multi-cloud architectures."
tags:
  - "clippings"
---
[Andrew Stiefel](https://www.f5.com/company/blog/authors/andrew-stiefel)

The question is no longer if you’re in the cloud, but how many clouds you’re in. Most enterprises today recognize there isn’t a “one cloud fits all” solution and have shifted toward a hybrid or multi-cloud architecture. According to data from F5’s [State of Application Strategy in 2023](https://www.f5.com/resources/reports/state-of-application-strategy-report) report, 85% of enterprises operate applications with two or more different architectures.

For development and API teams, this creates a lot of pressure. They’re tasked with securely delivering APIs at scale in complex, distributed environments. Connections are no longer simply between clients and backend services – they are now between applications deployed in different clouds, regions, data centers, or edge locations. Meanwhile, every API must meet the organization’s security and compliance requirements, regardless of where it is deployed and what tools are used to deliver and secure it.

Securing APIs in these highly distributed environments requires a unique set of capabilities and best practices. I previously wrote about the importance of [a two-pronged approach to API security](https://www.f5.com/company/blog/nginx/prevent-api-attacks-with-essential-tools-and-best-practices-for-api-security.html): “shifting left” to build security in from the start and “shielding right” with a set of global posture management practices. In this blog post, we’ll look at how to put that strategy into practice while securely delivering APIs across cloud, on-premises, and edge environments.

## Hybrid and Multi-Cloud API Security Reference Architecture

Hybrid and multi-cloud architectures have many definite advantages – especially for agility, scalability, and resilience. But they add an extra layer of complexity. In fact, F5’s [State of Application Strategy in 2023](https://www.f5.com/resources/reports/state-of-application-strategy-report) report showed how increased complexity is the most common challenge facing organizations today. The second most common challenge? Applying consistent security.

The problem today is that some security solutions, like certain [WAFs](https://www.nginx.com/resources/glossary/what-is-a-waf/), lack the context and protection APIs need. At the same time, dedicated API security solutions lack the ability to create and enforce policies to stop attacks. You need a solution that treats your architecture and technology as an interconnected stack that spans discovery, observability, management, and enforcement.

Practically, API security needs to be incorporated across three tiers to provide protection as API traffic traverses critical infrastructure points:

- **Global tier** – Edge protection from bot and DoS attacks, as well as discovery and visibility
- **Site tier** – Protection within an individual cloud, data center, or edge deployment
- **App tier** – Fine-grained access control and threat protection deployed near the API runtime

The reference architecture below provides an overview of how [F5 Distributed Cloud Services](https://www.f5.com/cloud) and F5 NGINX work together to provide comprehensive API protection in multi-cloud and hybrid architectures:

![F5 Distributed Cloud provides a global tier of protection across edge, cloud, and on-premises deployments.](https://cdn.studio.f5.com/images/k6fem79d/production/f80a9c390cb274e659682bb3606e9e252a6ac9e2-1024x910.svg)

In this reference architecture, F5 Distributed Cloud provides a global tier of protection across edge, cloud, and on-premises deployments. [NGINX Plus](https://www.nginx.com/products/nginx/api-gateway/) with [NGINX App Protect WAF](https://www.nginx.com/products/nginx-app-protect/web-application-firewall/) provides fine-grained protection at the site tier and/or app tier by integrating into software development lifecycles to enforce runtime security.

Let’s look at the security protections provided by each component of this architecture.

## API Discovery and Monitoring with F5 Distributed Cloud

To start, API traffic from public clients traverses through the [F5 Distributed Cloud Web Application and API Protection (WAAP)](https://www.f5.com/cloud/products/api-security), which is deployed at the edge. Critically, this provides global protection from [DDoS attacks](https://www.nginx.com/resources/glossary/distributed-denial-of-service/), bot abuse, and other exploits. It also provides important global visibility into API traffic entering different clouds, on-premises data centers, and edge deployments.

API traffic is increasing rapidly and most API attacks unfold slowly over weeks or even months. Finding malicious traffic inside the flood of regular API requests and responses can be like finding a needle in a haystack. To solve this problem, F5 Distributed Cloud uses artificial intelligence (AI) and machine learning (ML) to generate insights into API traffic, including API discovery, endpoint mapping, and actively learning and detect ion of anomalies which could represent emerging threats.

Acting as the global tier of app and API security, F5 Distributed Cloud WAAP provides the following benefits:

- **Automatic API** **discovery** – Detects and maps APIs for a complete view into your ecosystem, including visibility into third-party and shadow APIs, authentication status, and more.
- **Sensitive data leak prevention** – Detects, characterizes, and masks sensitive data like social security numbers, credit numbers, and other personally identifiable information (PII) from being exposed.
- **Monitoring and Anomaly Detection** – Continuously inspects and analyzes traffic to detect anomalies and vulnerabilities with AI and ML tools.
- **Enhanced API visibility** – Observes how traffic flows across all API endpoints to understand connectivity across edge APIs, internal services, and third-party integrations.
- **Enforced security across environments** – Uses a positive security model by enforcing schema validation, rate limiting, and blocking of undesirable or malicious traffic.

To get started with F5 Distributed Cloud WAAP, you can request a [free enterprise trial of F5 Distributed Cloud Services](https://www.f5.com/trials/distributed-cloud-services-enterprise-trial), which includes API security, bot defense, edge compute, and multi-cloud networking.

## Access Control and Runtime Protection with F5 NGINX

Once API traffic flows through the global tier, it arrives at the site tier and/or app tiers. While the global tier is typically managed by IT networking and security teams, individual APIs in the site tier and app tier are built and managed by software engineering teams.

When it comes to access control, an [API gateway](https://www.nginx.com/learn/api-gateway/) is a common choice because it enables developers to offload some of the most common security requirements to a shared infrastructure tier above the application. This reduces duplicated effort (e.g., having each developer or team build their own authentication and authorization service).

[F5 NGINX Management Suite API Connectivity Manager](https://www.nginx.com/products/nginx-management-suite/api-connectivity-manager/) enables platform engineering and DevOps teams to provide access to shared infrastructure, such as API gateways and developer portals, without requiring developers to fill out request tickets and other cumbersome systems.

With API Connectivity Manager, you can set security policies to configure NGINX Plus as an API gateway and configure and monitor NGINX App Protect WAF policies. Together, they provide critical API runtime protection, including the ability to:

- **Enforce access control** – Manage fine-grained access (authentication and authorization) to API endpoints and create access control lists to allow or deny traffic based on IP address or JWT claims.
- **Encrypt and mask sensitive data** – Secure communications between APIs with mTLS and end-to-end encryption, and detect and mask sensitive data like credit card numbers in API responses.
- **Detect and block threats** – Go beyond protection from the [OWASP API Security Top 10](https://owasp.org/www-project-api-security/) with advanced protection from more than 7,500 threat campaigns and attack signatures.
- **Monitor WAFs and API traffic at scale** – Visualize API traffic across all your API gateways with NGINX App Protect WAF to detect false positives and potential threats.

You can start a [free 30-day trial of the NGINX API Connectivity Stack](https://www.nginx.com/free-trial-api-connectivity-stack/) to access NGINX Management Suite and its API Connectivity Manager, Instance Manager, and Security Monitoring modules, in addition to NGINX Plus as an API gateway and NGINX App Protect for WAF and DoS protection.

## Conclusion

NGINX provides excellent runtime protection across cloud and on-premises data center environments. When combined with F5 Distributed Cloud, security and platform engineering teams gain continuous visibility into APIs endpoints regardless of where the associated apps are deployed. Together, F5 Distributed Cloud and NGINX provide complete flexibility to both build and secure your architecture in any way you need.

## Additional Resources

- Solution Brief: [API Security for Modern Applications with F5 NGINX](https://www.nginx.com/resources/datasheets/api-security/)
- Technical Whitepaper: [F5 Distributed Cloud WAAP with Comprehensive API Security](https://cdn.studio.f5.com/files/k6fem79d/production/7751b98a82c208959337e908cd0cf7d6f7337c77.pdf)
- eBook: [API Strategy: Best Practices for Platform Engineering Leaders](https://www.nginx.com/resources/library/api-strategy-best-practices-for-platform-engineering-leaders/)
- eBook: [Security as Code](https://www.nginx.com/resources/library/security-as-code/)
- Blog: [Prevent API Attacks with Essential Tools and Best Practices for API Security](https://www.f5.com/company/blog/nginx/prevent-api-attacks-with-essential-tools-and-best-practices-for-api-security.html)

---