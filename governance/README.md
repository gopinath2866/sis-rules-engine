# Governance Layer
# Constitutional Constraints for SIS

## Purpose

These documents define the **frozen constitutional boundaries** of SIS.
They do not add features, change behavior, or affect day-to-day usage.

These constraints exist to ensure SIS remains:
- Enforcement-invariant (doesn't change exit codes)
- Authority-external (doesn't resolve identities)
- Monetization-immune (revenue flows around, not through)

## Documents (Frozen)

### 1. Exception Schema (v1)
- `exception-schema.v1.json`
- Formal definition of what constitutes a valid exception
- Frozen: No runtime modifications

### 2. Signing Authority (v1)
- `signing-authority.v1.md`
- Defines who may sign exceptions (HUMAN/ORGANIZATIONAL/GOVERNANCE)
- Frozen: Authority resolution is external

### 3. Provenance & Retention (v1)
- `exception-provenance.v1.md`
- Defines what evidence means and doesn't guarantee
- Frozen: Loss of evidence doesn't change enforcement

### 4. Provenance Interface (v1)
- `provenance-interface.v1.md`
- Defines the fire-and-forget vent for evidence emission
- Frozen: Never blocks, never retries, never fails enforcement

## Usage

These documents are for:
- **Auditors** verifying system invariants
- **Lawyers** reviewing constitutional guarantees
- **Architects** understanding boundary constraints
- **Future maintainers** preventing scope creep

They are not required for:
- Running scans
- Writing rules
- Using exceptions
- Daily operation

## Amendment Process

Any change to these documents requires:
1. Constitutional convention
2. Three-day review period
3. Unanimous consent of maintainers
4. Version increment (v1 → v2)

## Example Artifact

- `exception-example.json`: Example exception showing the schema in practice
  - For testing and documentation only
  - Not used in production

---

**These documents define what SIS cannot do, not what it can do.**
**Their existence prevents feature creep and preserves enforcement purity.**
