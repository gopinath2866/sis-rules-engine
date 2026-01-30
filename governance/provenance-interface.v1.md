# Provenance Interface v1
# Constitutional Boundary for Evidence Emission

## Purpose

This document defines the **only** interface by which SIS may emit provenance-related data.

This interface exists to allow external systems to observe evidence.
It does not grant authority, require availability, or affect enforcement.

## Interface Semantics (The Vent)

SIS may emit provenance data through a single, append-only mechanism.

Characteristics:

- Fire-and-forget
- Non-blocking
- Best-effort
- Append-only
- One-way

SIS does not wait for completion.
SIS does not receive feedback.
SIS does not branch on success or failure.

Silence is success.

## Failure Tolerance (Mandatory)

The provenance interface must tolerate all failures without impact to SIS behavior.

Including but not limited to:

- Destination unavailable
- Network failure
- Storage full
- Permission denied
- Timeout
- Partial write
- Total loss

All failures are treated as non-events.

**Under no circumstances may provenance emission affect enforcement, exit codes, or findings.**

## Payload Shape (High-Level)

The emitted payload may include:

- Exact exception artifact bytes (as verified)
- Signature block(s)
- Verification metadata
- Temporal anchors
- SIS version identifier
- Execution context identifier (opaque)

The payload shape is informational, not contractual.
No consumer may assume completeness, ordering, or delivery.

No schema is guaranteed at this layer.

## Explicit Non-Requirements

The provenance interface explicitly does NOT provide:

- Acknowledgements
- Delivery guarantees
- Retry semantics
- Ordering guarantees
- Deduplication
- Storage
- Queryability
- Retrieval
- Search
- Indexing
- SLAs of any kind

No part of SIS may depend on these properties.

## Enforcement Invariance

Loss, delay, duplication, or corruption of provenance emission:

- Does not alter enforcement
- Does not revoke risk acceptance
- Does not trigger fallback behavior
- Does not create emergency modes
- Does not justify policy changes

## Constitutional Guarantee

This interface exists to prevent evidence from becoming authority.

Enforcement produces facts.  
Provenance observes facts.  
Observation never controls production.

## Version & Status

**Version:** v1  
**Status:** Frozen  
**Amendment Process:** Constitutional convention required  
**Governs:** All provenance emission mechanisms

*This document defines a boundary, not a feature.*
