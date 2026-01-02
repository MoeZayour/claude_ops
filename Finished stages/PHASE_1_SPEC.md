# 📋 Phase 1: Foundation - Implementation Spec

**Objective:** Build the skeleton of `ops_matrix_core` and implement the 3 core models.

## 1. Module Structure
- **Technical Name:** `ops_matrix_core`
- **Dependencies:** `base`, `sale_management`, `account`

## 2. Model Specifications

### A. `ops.branch` (New Model)
- **Description:** Geographic/Administrative Branches.
- **Fields:**
    - `name` (Char, Required)
    - `code` (Char, Required, Size 5, Unique per Company)
    - `manager_id` (Many2one -> res.users)
    - `company_id` (Many2one -> res.company, Default: current)
    - `sequence` (Integer, Default 10)

### B. `ops.business.unit` (New Model)
- **Description:** Functional/P&L Units.
- **Fields:**
    - `name` (Char, Required)
    - `code` (Char, Required, Size 5, Unique per Company)
    - `leader_id` (Many2one -> res.users)
    - `company_id` (Many2one -> res.company, Default: current)
    - `sequence` (Integer, Default 10)

### C. `res.users` (Inheritance)
- **Description:** Add Matrix assignment fields.
- **Fields:**
    - `default_branch_id` (Many2one -> ops.branch)
    - `default_business_unit_id` (Many2one -> ops.business.unit)
    - `allowed_business_unit_ids` (Many2many -> ops.business.unit)
- **Logic:**
    - `@api.onchange('default_business_unit_id')`: If a user sets a default unit, automatically add it to their `allowed_business_unit_ids` list.

## 3. UI Requirements (XML)
- **Menus:**
    - Branches: `Settings > Users & Companies > Branches`
    - Business Units: `Sales > Configuration > Business Units`
- **Views:** Tree and Form views for both new models.
- **User Form:** Add a new tab "Matrix Assignment" inside the User form.

## 4. Security
- **CSV:** Grant full access to `base.group_system`.
- **CSV:** Grant Read-only access to `base.group_user`.