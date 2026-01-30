# Roadmap v1.1.0

## Goal

Enable the first paid tier by making SIS indispensable for teams operating rule-based or policy-driven systems.

---

## Planned Features

1. **Rule Pack: AWS IAM**
   Pre-built rules for common IAM misconfigurations (wildcards, overly broad permissions, risky service combinations).

2. **GitHub Action**
   One-line CI integration for pull request and main-branch scanning.

3. **Output Formats**

   * SARIF (GitHub Code Scanning)
   * JUnit (CI systems like Jenkins)
   * Slack webhook notifications

4. **Rule Authoring Helper**
   Interactive rule creation via:

   ```bash
   sis rule create --interactive
   ```

---

## Monetization Path

* Core engine remains **open-source (Apache 2.0)**.
* Paid offerings:

  * Curated rule packs (AWS, Kubernetes, cloud IAM, SaaS platforms)
  * Enterprise features (dashboards, audit logs, team management)
* Services:

  * Custom rule development
  * Architecture and policy reviews

---

## Timeline

* Target: **v1.1.0 in ~6 weeks**
* Input driven by early adopters and free audit participants
