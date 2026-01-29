# SIS Canonical Execution Path (LOCKED)

As of v1:

CLI ENTRYPOINT:
- sis-core/src/sis/cli.py

PRIMARY ORCHESTRATOR:
- sis-core/src/sis/scanner.py (SISScanner)

CORE ENGINE (AUTHORITATIVE):
- sis-core/src/sis/engine.py
  - check_condition
  - check_resource_rule
  - validate_resources

NON-CANONICAL / LEGACY / DEAD CODE (DO NOT USE):
- engine.scan() (both definitions)
- engine.parse_terraform_file()
- sis-core/src/sis/main.py (API prototype)

RULE:
Any new feature, business logic, or monetization MUST sit on the canonical path.
