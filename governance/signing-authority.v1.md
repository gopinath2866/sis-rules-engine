# Signing Authority v1
# Constitutional Framework for Risk Acceptance

## Purpose of Signing in SIS

A signature in SIS does one thing only:

**It binds a human or institution to the acknowledgment of a specific risk, at a specific time, for a specific scope.**

It does not:

- Grant permission
- Change enforcement  
- Reduce severity
- Create "approval"
- Allow merging
- Override policy

If anyone internally describes signing as "approval" or "permission," that's a constitutional violation.

## The Only Question Signing Answers

**"Who explicitly accepted responsibility for this risk?"**

That's it.

Everything else is downstream.

## Authority Classes (Frozen at Three)

There are exactly three authority classes in v1.

Do not add more. Do not make them configurable. These are semantic classes, not RBAC.

### 1. HUMAN_SIGNER (Default)

**Who:**
- Named individual
- Engineer, security lead, protocol owner
- Real human with identity

**Identity Examples:**
- PGP fingerprint
- DID (Decentralized Identifier)
- Corporate SSO ID hash
- Verified email/identity hash

**What it signals:**
- "A real person accepted this risk."

**This is enough for:**
- Internal teams
- Early-stage products  
- Open-source projects
- Startups

### 2. ORGANIZATIONAL_SIGNER

**Who:**
- Company
- Foundation
- Legal entity
- Institution

**Identity Examples:**
- Org signing key
- Legal Entity Identifier (LEI)
- Corporate PKI identity
- Notarized entity proof

**What it signals:**
- "This risk acceptance is institutionally backed."

**This is where:**
- Procurement starts listening
- Legal teams engage
- Audits become structured
- Enterprise compliance begins

### 3. GOVERNANCE_SIGNER (DAO/Multisig)

**Who:**
- On-chain governance
- Multisig
- Timelock-controlled entity
- Formal governance process

**Identity Examples:**
- Safe/Multisig address
- Governor contract address
- Governance proposal hash
- Snapshot space fingerprint

**What it signals:**
- "Risk acceptance followed formal governance process."

**This is:**
- Auditor-grade provenance
- Regulatory-grade evidence
- Institutional accountability

## What SIS Must and Must Not Do

### ❌ Constitutional Prohibitions

SIS must **not**:

1. Decide if a signer is "authorized"
2. Maintain allowlists or blocklists
3. Fetch, validate, or resolve external identities
4. Judge legitimacy of signing entities
5. Understand or interpret governance processes
6. Act as an identity provider or registry
7. Make policy decisions based on signer class
8. Store or manage signing keys

### ✅ Constitutional Responsibilities

SIS only ever verifies:

1. **Cryptographic validity** (optional, mechanical)
2. **Schema correctness** (formal validation)
3. **Scope match** (exception applies to this context)
4. **Expiry** (temporal bounds)

**Authority resolution is external. Always.**

## Why Money Shows Up Here (Not Before)

The moment signatures exist, inevitable questions appear:

- "Who is allowed to sign?"
- "Can we require multiple signers?"
- "Can a Safe sign?"
- "Can we prove signer validity at time T?"
- "Can we retain and query historical attestations?"
- "Can auditors pull verifiable chains of responsibility?"

Notice the pattern:

**None of these belong in SIS.**

They belong in:

- Hosted governance services
- Compliance and legal tooling
- Enterprise workflow integrations
- Audit and provenance systems
- Identity verification providers
- Retention and archival services

**SIS stays clean. Revenue wraps around it.**

This is how we avoid becoming "yet another policy engine."

## Implementation Boundaries (Technical)

### CLI Contract
- `--public-key` verifies cryptographic signatures
- Never resolves "who" the key belongs to
- Never checks if signer is "allowed"
- Never modifies behavior based on signer class

### Exception Schema
- `signer_identity` field is opaque string
- No enum for authority classes
- No validation beyond format
- No external resolution

### Storage
- No key management
- No identity storage
- No allowlist persistence
- No historical authority tracking

## Constitutional Guarantees

1. **Neutrality:** SIS treats all valid signatures equally
2. **Opacity:** SIS doesn't understand signer semantics  
3. **Externality:** Authority lives outside the system
4. **Immutability:** Signed exceptions are evidence, not policy
5. **Accountability:** Signatures bind, they don't permit

## Next Evolution: Provenance & Retention

Once this model is frozen, the only remaining constitutional move is:

**Exception provenance & retention** — who stores them, for how long, under what guarantees.

That is where:
- SaaS pricing appears naturally
- Enterprise contracts form
- Audit SLAs become valuable
- Compliance tooling integrates

But we don't go there yet. This document must be ratified first.

---
**Version:** v1  
**Status:** Frozen
**Ratified:** $(date +%Y-%m-%d)
**Amendment Process:** Requires constitutional convention
**Supersedes:** No previous authority model
**Governs:** All signing implementations in SIS

*This document is for auditors, lawyers, and future maintainers.*
*It exists to prevent scope creep and preserve system integrity.*
