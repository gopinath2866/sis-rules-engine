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
| **Canonical Suite (26 tests)** | ![SIS Canonical](https://github.com/your-org/sis-rules-engine/workflows/SIS%20Rules%20Validation/badge.svg) |
| **Code Quality** | ![Code Quality](https://github.com/your-org/sis-rules-engine/workflows/SIS%20Rules%20Validation/badge.svg?branch=main&event=push) |
| **Compliance Dashboard** | [📊 View Dashboard](https://your-org.github.io/sis-rules-engine/compliance/) |

**Latest Release**: [![GitHub release](https://img.shields.io/github/v/release/your-org/sis-rules-engine)](https://github.com/your-org/sis-rules-engine/releases)
**Docker Image**: [![Docker Pulls](https://img.shields.io/docker/pulls/your-org/sis-validator)](https://ghcr.io/your-org/sis-validator)