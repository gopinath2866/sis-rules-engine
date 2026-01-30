# Exception Provenance & Retention v1
# Constitutional Boundary for Artifact Preservation

## Purpose of Provenance in SIS

Provenance refers to the ability to prove the existence, authenticity, and history of a risk acknowledgment.

It does not:

- Grant authority
- Extend validity
- Modify enforcement
- Create obligations

If anyone describes provenance as "audit trail" or "compliance proof," that's acceptable only if they understand: it's evidence, not permission.

## What Must Be Retained (Conceptual Minimum)

For any exception to be considered provable, the following must be retainable:

### 1. Exception Artifact (Exact Bytes)
- The complete JSON artifact as signed
- No modifications, no normalization
- Byte-for-byte identical to what was verified

### 2. Signature Block(s)
- Complete signature section
- `signer_identity` (opaque string)
- `signature_hash` (base64 encoded)
- No parsing, no interpretation

### 3. Verification Metadata
- Algorithm identifier (e.g., "RSA-PSS-SHA256")
- Public key fingerprint (if available)
- Verification result (boolean)
- Verification timestamp

### 4. Temporal Anchors
- `created_at` (from artifact)
- `signed_at` (when signature was applied)
- `expires_at` (from artifact)
- `verified_at` (when SIS verified it)

## What SIS Explicitly Does NOT Guarantee

SIS is not a storage system. SIS does not guarantee:

1. **Availability**
   - Artifacts may not be retrievable
   - No SLA for access

2. **Durability**
   - Artifacts may be lost
   - No backup guarantees

3. **Completeness**
   - Not all exceptions will be retained
   - Retention may be partial

4. **Discoverability**
   - No search API
   - No indexing
   - No query interface

5. **Historical Recovery**
   - Cannot reconstruct past states
   - Cannot prove what was not retained

**No "best effort" language. No softening.**

## What Downstream Systems May Provide

External systems **may** provide (not "should"):

1. **Immutable Storage**
   - Write-once, read-many storage
   - Cryptographic proof of existence

2. **Queryability**
   - Search by signer, rule, target, timeframe
   - Filtering and aggregation

3. **Audit Exports**
   - Regulatory formats (JSON, CSV, PDF)
   - Period-based reporting

4. **Retention SLAs**
   - Guaranteed retention periods
   - Geographic replication

5. **Legal Holds**
   - Preservation during litigation
   - Chain-of-custody logging

6. **Regulatory Mappings**
   - SOC2, ISO27001, GDPR mappings
   - Control framework alignment

These are **commercial surfaces**, not requirements.

## The Non-Negotiable Sentence

**"Loss of provenance does not alter SIS enforcement behavior."**

This means:

- If an exception cannot be proven to exist, enforcement remains unchanged
- Missing evidence ≠ revoked risk acceptance
- Storage failure ≠ policy change
- No emergency overrides based on availability

This sentence prevents coercion by:
- Enterprises demanding "just this one" policy bypass
- Regulators requiring retroactive adjustments
- Internal pressure to "fix" missing records
- Sales promises that distort core behavior

## Implementation Boundaries (Technical)

### SIS Core Contract
- May output provenance data (structured, machine-readable)
- Never stores provenance data internally
- Never depends on provenance for decisions
- Never fails if provenance cannot be recorded

### External Systems Contract
- May consume provenance data
- May transform, store, index, analyze
- Must not require SIS modifications
- Must not affect SIS execution

### Failure Modes
- Provenance system down → SIS continues
- Storage full → SIS continues  
- Network partition → SIS continues
- Corruption → SIS continues

## Constitutional Guarantees

1. **Separation of Concerns**
   - Enforcement ≠ Evidence
   - Validation ≠ Storage
   - Decision ≠ Record

2. **No Single Point of Coercion**
   - No one can force policy change via provenance
   - No "emergency access" to modify behavior

3. **Monetization Without Corruption**
   - Revenue can flow around evidence management
   - No feature creep into enforcement core

## Next Evolution: Commercial Interfaces

Once this boundary is frozen, natural commercial surfaces emerge:

1. **Provenance as a Service**
   - Hosted retention with SLAs
   - Pay-per-artifact or subscription

2. **Audit Compliance Packages**
   - Pre-built regulatory mappings
   - Auditor-friendly exports

3. **Enterprise Integration**
   - SIEM integrations
   - GRC platform connectors

4. **Legal & Forensic Support**
   - Chain-of-custody certification
   - Expert testimony packages

None of these require:
- Changing gates
- Changing rules  
- Changing exit codes
- Changing enforcement

## Version & Status

**Version:** v1  
**Status:** Frozen  
**Ratified:** $(date +%Y-%m-%d)  
**Amendment Process:** Constitutional convention required  
**Supersedes:** No previous provenance model  
**Governs:** All provenance-related implementations

*This document is for system designers, commercial teams, and auditors.*  
*It exists to prevent scope creep and preserve enforcement purity.*
