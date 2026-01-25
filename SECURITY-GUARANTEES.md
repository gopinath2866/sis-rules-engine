# Security Guarantees and Non-Guarantees

This document defines what SIS (Security Inspection System) **does** and **does not** guarantee.

---

## What SIS Does

* Performs **static analysis** on rule files, policy definitions, and configuration logic.
* Detects patterns commonly associated with security risk (e.g. overly permissive rules, missing deny paths, wildcard conditions).
* Allows teams to codify **domain-specific security rules**.
* Helps catch misconfigurations **before deployment**.

---

## What SIS Does NOT Do

* **Not a runtime monitor**
  SIS does not observe or intercept live system behavior.

* **Not a vulnerability scanner**
  SIS does not scan for CVEs, software exploits, or network vulnerabilities.

* **Not a substitute for manual review**
  SIS is an automated aid, not a replacement for expert security audits.

* **Not a guarantee of security**
  Passing SIS checks reduces risk but does not eliminate it.

---

## Intended Use

SIS is designed to be used:

* During development
* In CI/CD pipelines
* As a pre-deployment safety check for rule-based systems

---

## Reporting Security Issues

If you discover a security issue in SIS itself, please:

* Open a GitHub issue with the prefix **[SECURITY]**, or
* Contact the maintainer privately if responsible disclosure is required.

---

*Last updated: 2026-01-25*
