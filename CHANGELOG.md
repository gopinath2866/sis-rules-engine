# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [1.0.0] - 2026-01-25

### Added

* Initial stable release of SIS (Security Inspection System).
* Core static scanner engine for rule and policy analysis.
* Extensible rule definitions using YAML and JSON.
* CLI interface for scanning configuration and policy files.
* Deterministic analysis with no runtime dependencies.

### Security

* No known critical vulnerabilities in the scanner itself at release time.
* Static analysis only; no execution or mutation of target systems.

## [1.1.0] - 2026-01-28

### Fixed
- Array existential semantics for security rules (critical false-negative fix)
- Nested array path resolution
- Empty array handling

### Added
- Formal array semantics documentation
- Semantic stability guarantees
- Critical regression tests
