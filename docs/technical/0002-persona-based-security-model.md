# ADR-0002: Persona-Based Security Model

**Date:** 2026-01-11
**Status:** Accepted

## Context

Odoo's standard security model, based on static `res.groups` records, is insufficient for modeling complex organizational roles. A "Sales Manager" is more than just a security group; it's a role with specific operational boundaries (branches, business units) and authorities (discount limits, approval capabilities). Mapping these complex requirements directly to Odoo groups is cumbersome and inflexible.

## Decision

We will implement a `ops.persona` model to act as a container for organizational roles. A Persona is not a user or a security group, but a role definition that a user can be assigned.

The `ops.persona` model will aggregate:
1.  **Matrix Access:** Allowed branches and business units.
2.  **Job Hierarchy:** Parent/child relationships for escalation.
3.  **Segregation of Duties (SoD) Flags:** Boolean fields like `can_validate_invoices`, `can_execute_payments` that define specific authorities.

A user's final permissions will be a dynamic aggregation of all Personas assigned to them. A background process will synchronize these aggregated permissions to the user's record (`res.users`) for use in record rules and domain filters.

## Consequences

- **Pros:**
  - Highly flexible and realistic security model that mirrors a real-world org chart.
  - Users can be assigned multiple roles (e.g., acting as both a "Branch Manager" and a "Sales Rep").
  - SoD authorities are cleanly separated from standard Odoo permissions.
  - Simplifies user management: administrators assign roles (Personas) instead of dozens of individual permissions.
  - Enables features like temporary delegation of a Persona.

- **Cons:**
  - Adds a layer of abstraction on top of Odoo's native security.
  - Requires a computation/synchronization step to calculate a user's effective permissions.