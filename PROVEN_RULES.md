
## Architectural Milestone: Nested Block Support

**Date**: $(date)
**Achievement**: Parser now correctly handles nested Terraform blocks as dictionaries

### What Works:
- ✅ Nested blocks: `service_account { ... }` → `{"service_account": {...}}`
- ✅ Multiple levels of nesting
- ✅ Arrays within nested blocks
- ✅ Complex jsonencode() blocks as opaque strings

### Proven Rules Expanded:
1. IRR-DEC-01 (deletion_protection = true)
2. IRR-DEC-02 (lifecycle.prevent_destroy = true)  
3. IRR-IDENT-04 (assume_role_policy + managed_policy_arns)
4. IRR-IDENT-07 (service_account block existence)

### Test Coverage:
- 5 golden tests passing
- Clean files correctly pass
- Multiple violations in one file
- Nested block structure preserved

## Current Limitations:

### Parser Limitations:
1. ✅ Nested blocks (service_account, lifecycle, etc.)
2. ✅ Simple key-value pairs
3. ✅ Arrays
4. ⚠️  Function calls (jsonencode, file(), etc.) - partially supported
   - Simple function calls as opaque strings work
   - Multi-line function calls may not preserve all content

### Rule-Specific Notes:
- IRR-IDENT-04: Works with simple IAM roles (string values)
- IRR-IDENT-04: May not work with complex jsonencode() blocks
- All other rules work as expected

### Architecture Decision:
The parser intentionally treats complex function calls as opaque strings to:
1. Avoid parsing Terraform/HCL2 expressions
2. Maintain simplicity and performance
3. Focus on structural invariants over semantic analysis

This means rules should be written to check for:
- Existence of fields (EXISTS operator)
- Simple equality checks (EQUALS operator)
- Avoid deep inspection of complex expressions
