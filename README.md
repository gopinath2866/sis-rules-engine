# Static Irreversibility Scanner (SIS) v1.0.0

Deterministic pattern scanner for irreversible infrastructure decisions.

## Overview
The Static Irreversibility Scanner (SIS) is a sealed, deterministic artifact that scans infrastructure-as-code manifests for patterns indicating irreversible decisions, identity bindings, or admin override dependencies.

## Features
- **25 Deterministic Rules**: Pattern-based, no inference
- **Stateless API**: JSON in/out, no persistence
- **Multi-Format Support**: Terraform, CloudFormation, Kubernetes, Docker Compose, ARM
- **Sealed Logic**: No external dependencies, no telemetry

## Quick Start
```bash
docker build -t sis:v1.0.0 .
docker run -p 8000:8000 sis:v1.0.0
## CI/CD Status

| Test Suite | Status |
|------------|--------|
| **Canonical Suite (26 tests)** | ![SIS Canonical](https://github.com/gopinath2866/sis-rules-engine/workflows/SIS%20Rules%20Validation/badge.svg) |
| **Code Quality** | ![Code Quality](https://github.com/gopinath2866/sis-rules-engine/workflows/SIS%20Rules%20Validation/badge.svg?branch=main&event=push) |
| **Compliance Dashboard** | [📊 View Dashboard](https://gopinath2866.github.io/sis-rules-engine/compliance/) |

**Latest Release**: [![GitHub release](https://img.shields.io/github/v/release/gopinath2866/sis-rules-engine)](https://github.com/gopinath2866/sis-rules-engine/releases)
**Docker Image**: [![Docker Pulls](https://img.shields.io/docker/pulls/gopinath2866/sis-validator)](https://ghcr.io/gopinath2866/sis-validator)
## CI/CD Status

| Test Suite | Status |
|------------|--------|
| **Canonical Suite (26 tests)** | ![SIS Canonical](https://github.com/gopinath2866/sis-rules-engine/workflows/SIS%20Rules%20Validation/badge.svg) |
| **Code Quality** | ![Code Quality](https://github.com/gopinath2866/sis-rules-engine/workflows/SIS%20Rules%20Validation/badge.svg?branch=main&event=push) |
| **Compliance Dashboard** | [📊 View Dashboard](https://gopinath2866.github.io/sis-rules-engine/compliance/) |

**Latest Release**: [![GitHub release](https://img.shields.io/github/v/release/gopinath2866/sis-rules-engine)](https://github.com/gopinath2866/sis-rules-engine/releases)
**Docker Image**: [![Docker Pulls](https://img.shields.io/docker/pulls/gopinath2866/sis-validator)](https://ghcr.io/gopinath2866/sis-validator)

## Running Tests Locally

```bash
# Run the canonical test suite
./scripts/run_canonical_suite.py

# Generate compliance report
./scripts/generate_compliance.py --rules rules/canonical.json --test-results junit/ --output docs/compliance/

# Run via docker-compose
docker-compose up --build
## 🔗 Quick Links

- **CI/CD Status**: [![SIS Validation](https://github.com/gopinath2866/sis-rules-engine/actions/workflows/sis-validation.yml/badge.svg)](https://github.com/gopinath2866/sis-rules-engine/actions)
- **Compliance Dashboard**: [![GitHub Pages](https://img.shields.io/badge/docs-GitHub_Pages-blue)](https://gopinath2866.github.io/sis-rules-engine/compliance/)
- **Docker Image**: [![Docker Image](https://img.shields.io/badge/docker-ghcr.io%2Fgopinath2866%2Fsis--validator-blue)](https://ghcr.io/gopinath2866/sis-rules-engine/sis-validator)
- **Latest Release**: [![GitHub release](https://img.shields.io/github/v/release/gopinath2866/sis-rules-engine)](https://github.com/gopinath2866/sis-rules-engine/releases)

## 🚀 Features

✅ **Full CI/CD Pipeline** - Automated testing, linting, and deployment  
✅ **26 Canonical Tests** - Complete test suite for all SIS rules  
✅ **Compliance Dashboard** - Interactive reports on GitHub Pages  
✅ **Docker Ready** - Containerized deployment  
✅ **Multi-Python Support** - Tested on Python 3.9-3.12  
✅ **Production Ready** - Type checking, formatting, and quality gates