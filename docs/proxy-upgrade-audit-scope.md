Proxy Upgrade Safety Requirement
All mainnet proxy upgrades (UUPS, Transparent, Beacon) MUST be evaluated using the SIS Proxy Upgrade Gate prior to execution.

The audit scope includes review of the SIS Proxy Upgrade Gate report artifact (sis-proxy-upgrade-report.json) generated in CI for the proposed upgrade. Any HARD FAIL or POLICY REQUIRED status constitutes a blocking issue and must be resolved before deployment.

Once executed, proxy upgrades are assumed irreversible.
Any deviation from this requirement constitutes acceptance of permanent protocol risk.
