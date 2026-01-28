# ADR-0004: Database Constraint for CR Number Uniqueness

**Date:** 2026-01-19
**Status:** Accepted

## Context

To ensure master data integrity, the Company Registration (CR) number for each customer (`res.partner`) must be unique. Using Odoo's Python-level `_sql_constraints` is the standard approach, but it can sometimes be bypassed, especially during direct data imports or if the constraint is temporarily disabled.

## Decision

We will enforce the uniqueness of the `ops_cr_number` field on the `res_partner` model by applying a native PostgreSQL `UNIQUE` constraint directly to the database table. This provides an unbreakable guarantee of uniqueness at the lowest possible level.

The constraint will be created via a post-init hook in the module.

## Consequences

- **Pros:**
  - Guarantees data integrity. It is impossible to have duplicate CR numbers in the database.
  - The constraint correctly allows multiple `NULL` values, which is the desired behavior for leads or individual customers who do not have a CR number.
  - Odoo's ORM handles the resulting `psycopg2.IntegrityError` gracefully, presenting a user-friendly error message.

- **Cons:**
  - The constraint is applied outside of the standard Odoo `_sql_constraints` mechanism, so developers must be aware of its existence.
  - Requires a post-init hook or manual SQL execution to apply, rather than being purely declarative in the model definition.