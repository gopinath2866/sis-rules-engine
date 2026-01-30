# Provenance Collector v1
# First Paid SKU for SIS

## Product Definition

The Provenance Collector is an external service that:
1. Listens to SIS provenance emissions (the vent)
2. Stores them durably with cryptographic proof
3. Provides query and export capabilities
4. Never interacts with or affects SIS enforcement

## Constitutional Alignment

This SKU respects all constitutional boundaries:

- **Non-interference**: Never touches SIS core
- **Observation-only**: Listens to the vent, doesn't inject
- **Failure-tolerant**: SIS doesn't depend on collector availability
- **Enforcement-invariant**: Collector status never affects SIS behavior

## Technical Implementation

### Collector Architecture
SIS CLI → vent (stdout/stderr) → Collector Daemon → Immutable Storage

text

### Storage Guarantees
- Append-only write-once storage
- Cryptographic hashing for tamper evidence
- Configurable retention periods
- Geographic replication (optional)

### Query Capabilities
- Search by: signer, rule, target, timeframe
- Filter by: verification status, expiration
- Export formats: JSON, CSV, PDF (audit-ready)
- API access with rate limiting

### Integration Methods
1. **CLI Pipe**: `sis scan ... 2> | collector ingest`
2. **File Watch**: Collector watches stderr log file
3. **HTTP Endpoint**: SIS can be configured to emit to HTTP (future)

## Pricing Model

### Tier 1: Developer (Free)
- 100 provenance events/month
- 30-day retention
- Basic query interface
- Community support

### Tier 2: Team ($99/month)
- 10,000 provenance events/month
- 1-year retention
- Advanced query & filtering
- Email support
- Audit export (PDF)

### Tier 3: Enterprise ($999/month)
- Unlimited events
- 7-year retention (regulatory compliance)
- Custom retention policies
- SIEM integration (Splunk, Elastic)
- Dedicated support
- Legal hold capabilities
- SOC2 compliance reports

## Deployment Options

### SaaS
- Fully managed service
- Automatic updates
- 99.9% uptime SLA
- Daily backups

### Self-Hosted
- Docker container
- Kubernetes helm chart
- On-premise deployment
- Bring-your-own storage (S3, GCS, Azure Blob)

## Compliance & Certifications

- GDPR compliant (data processor agreement)
- SOC2 Type II (in progress)
- HIPAA compliant (optional BAA)
- FedRAMP Moderate (roadmap)

## Sales Arguments (Non-Corrupting)

1. **For Auditors**: "Prove what was accepted, by whom, when"
2. **For Compliance**: "Demonstrate policy adherence over time"
3. **For Legal**: "Evidence chain for liability protection"
4. **For Engineering**: "Zero performance impact, no code changes"

## Constitutional Safeguards

1. **No Feature Creep**: Collector cannot request SIS changes
2. **No Emergency Access**: No backdoor to modify SIS behavior
3. **No Enforcement Coupling**: SIS works identically with or without collector
4. **Transparent Pricing**: No "compliance tax" hidden in core product

## Implementation Timeline

### Phase 1 (Now)
- Collector daemon (Go/Python)
- File-based ingestion
- Basic query API
- Developer tier (free)

### Phase 2 (Q2)
- HTTP ingestion endpoint
- Advanced query capabilities
- Team & Enterprise tiers
- SaaS offering

### Phase 3 (Q3)
- SIEM integrations
- Compliance reporting
- Self-hosted deployment
- Enterprise features

## Support & SLAs

### Community Support
- GitHub issues
- Documentation
- Community forum

### Professional Support
- 24-hour response time
- Priority bug fixes
- Designated support engineer

### Enterprise Support
- 1-hour response time
- Dedicated account manager
- Custom integration support
- Training & onboarding

## Success Metrics

### Business Metrics
- MRR growth
- Customer acquisition cost
- Lifetime value
- Churn rate

### Technical Metrics
- Ingestion latency (<100ms)
- Query performance (<1s)
- Storage efficiency
- Uptime (99.9%)

### Compliance Metrics
- Audit completion time
- Evidence retrieval time
- Report generation time
- Regulatory coverage

## Risks & Mitigations

### Technical Risks
- **Data loss**: Multi-region replication, regular backups
- **Performance impact**: Async ingestion, load balancing
- **Scalability**: Horizontal scaling, sharding

### Business Risks
- **Commoditization**: Focus on compliance integration
- **Pricing pressure**: Value-based pricing, enterprise features
- **Market timing**: Start with early adopters, expand gradually

### Constitutional Risks
- **Scope creep**: Strict interface adherence, regular audits
- **Enforcement coupling**: Quarterly constitutional review
- **Authority leakage**: Clear separation in all documentation

## Exit Strategy

If discontinued:
1. Open source core collector
2. Data export tools
3. 12-month sunset period
4. Migration assistance to alternatives

## Version & Status

**Version:** v1  
**Status:** Active  
**Pricing Model:** Tiered subscription  
**Constitutional Compliance:** Verified  
**Target Audience:** Security teams, compliance officers, auditors

*This SKU represents the first revenue-generating product built around SIS*
*without corrupting its core enforcement principles.*
EOF