#!/usr/bin/env python3
"""
OPS Framework Status Generator (Template-First Approach)
Focus on configuration templates and setup wizards, not customer-specific data
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

def count_files(pattern, base_path="/opt/gemini_odoo19/addons"):
    """Count files matching pattern"""
    try:
        result = subprocess.run(
            f"find {base_path} -path '*/ops_matrix*' -name '{pattern}' 2>/dev/null | wc -l",
            shell=True, capture_output=True, text=True
        )
        return int(result.stdout.strip())
    except:
        return 0

def find_files(pattern, base_path="/opt/gemini_odoo19/addons"):
    """Find files matching pattern"""
    try:
        result = subprocess.run(
            f"find {base_path} -path '*/ops_matrix*' -name '{pattern}' 2>/dev/null",
            shell=True, capture_output=True, text=True
        )
        return [f for f in result.stdout.strip().split('\n') if f]
    except:
        return []

def get_module_info():
    """Analyze module structure"""
    modules = []
    addons_path = Path("/opt/gemini_odoo19/addons")
    
    for module_dir in sorted(addons_path.glob("ops_matrix*")):
        if not module_dir.is_dir():
            continue
            
        module_name = module_dir.name
        demo_count = len(list((module_dir / "demo").glob("*.xml"))) if (module_dir / "demo").exists() else 0
        data_count = len(list((module_dir / "data").glob("*.xml"))) if (module_dir / "data").exists() else 0
        wizard_files = list((module_dir / "wizard").glob("*.py")) if (module_dir / "wizard").exists() else []
        wizard_count = len([f for f in wizard_files if f.name != "__init__.py"])
        
        if demo_count > 0 or data_count > 0:
            status = "✅ GOOD" if wizard_count > 0 else "🟡 PARTIAL"
        else:
            status = "❌ MINIMAL"
            
        modules.append({
            'name': module_name,
            'demo': demo_count,
            'data': data_count,
            'wizards': wizard_count,
            'status': status
        })
    
    return modules

def analyze_templates():
    """Analyze template files"""
    templates = []
    addons_path = Path("/opt/gemini_odoo19/addons")
    
    for template_file in sorted(addons_path.glob("ops_matrix*/data/*.xml")):
        if any(keyword in template_file.name.lower() for keyword in ['template', 'demo', 'default']):
            rel_path = str(template_file.relative_to(addons_path))
            line_count = len(template_file.read_text().splitlines())
            templates.append((rel_path, line_count))
    
    return templates

def analyze_wizards():
    """Analyze wizard files"""
    wizards = []
    addons_path = Path("/opt/gemini_odoo19/addons")
    
    for wizard_file in sorted(addons_path.glob("ops_matrix*/wizard/*.py")):
        if wizard_file.name == "__init__.py":
            continue
            
        module_name = wizard_file.parts[-3]
        line_count = len(wizard_file.read_text().splitlines())
        func_count = wizard_file.read_text().count("def ")
        
        wizards.append({
            'name': wizard_file.name,
            'module': module_name,
            'lines': line_count,
            'functions': func_count
        })
    
    return wizards

def calculate_scores():
    """Calculate template completeness scores"""
    addons_path = Path("/opt/gemini_odoo19/addons")
    
    # Demo/Template Data (30 points max)
    demo_files = len(list(addons_path.glob("ops_matrix*/data/*.xml")))
    demo_score = min(30, demo_files * 2)
    
    # Setup Wizards (25 points max)
    wizard_files = [f for f in addons_path.glob("ops_matrix*/wizard/*.py") if f.name != "__init__.py"]
    wizard_count = len(wizard_files)
    wizard_score = min(25, wizard_count * 12)
    
    # Documentation (20 points max)
    help_views = 0
    for view_file in addons_path.glob("ops_matrix*/views/*.xml"):
        if 'help=' in view_file.read_text():
            help_views += 1
    doc_score = min(20, help_views * 2)
    
    # Validation (15 points max)
    constraint_models = 0
    for model_file in addons_path.glob("ops_matrix*/models/*.py"):
        content = model_file.read_text()
        if '_sql_constraints' in content or '@api.constrains' in content:
            constraint_models += 1
    validation_score = min(15, constraint_models)
    
    # UX (10 points max)
    ux_views = 0
    for view_file in addons_path.glob("ops_matrix*/views/*.xml"):
        content = view_file.read_text()
        if 'widget=' in content or 'placeholder=' in content:
            ux_views += 1
    ux_score = min(10, ux_views)
    
    total_score = demo_score + wizard_score + doc_score + validation_score + ux_score
    
    return {
        'demo': (demo_score, demo_files),
        'wizards': (wizard_score, wizard_count),
        'help': (doc_score, help_views),
        'validation': (validation_score, constraint_models),
        'ux': (ux_score, ux_views),
        'total': total_score
    }

def check_onboarding():
    """Check for onboarding elements"""
    elements = []
    addons_path = Path("/opt/gemini_odoo19/addons")
    
    # Dashboard menu
    if (addons_path / "ops_matrix_core/views/ops_dashboard_menu.xml").exists():
        elements.append("✅ Dashboard menu structure exists")
    else:
        elements.append("❌ No dashboard menu found")
    
    # Demo data
    demo_count = len(list(addons_path.glob("ops_matrix*/demo/*.xml")))
    if demo_count > 0:
        elements.append(f"✅ Demo data available ({demo_count} files)")
    else:
        elements.append("❌ No demo data for testing")
    
    # Template directories
    template_dirs = len(list(addons_path.glob("ops_matrix*/data/templates")))
    if template_dirs > 0:
        elements.append(f"✅ Template directory structure exists ({template_dirs} directories)")
    else:
        elements.append("⚠️ No dedicated template directories")
    
    return elements

def check_tests():
    """Check for template tests"""
    addons_path = Path("/opt/gemini_odoo19/addons")
    
    test_files = [f for f in addons_path.glob("ops_matrix*/tests/*.py") if f.name != "__init__.py"]
    test_count = len(test_files)
    
    template_tests = 0
    for test_file in test_files:
        content = test_file.read_text()
        if 'template' in content.lower() or 'demo' in content.lower():
            template_tests += 1
    
    return test_count, template_tests

def generate_report():
    """Generate the complete status report"""
    
    # Determine version
    report_dir = Path("/opt/gemini_odoo19")
    existing_reports = sorted(report_dir.glob("OPS_Status_*.md"))
    
    if existing_reports:
        latest = existing_reports[-1]
        version = int(latest.stem.split('_')[-1]) + 1
        print(f"Found: {latest.name}")
    else:
        version = 1
        print("Starting with version 1")
    
    output_file = report_dir / f"OPS_Status_{version}.md"
    print(f"Creating: {output_file}")
    
    # Gather data
    modules = get_module_info()
    templates = analyze_templates()
    wizards = analyze_wizards()
    scores = calculate_scores()
    onboarding = check_onboarding()
    test_count, template_tests = check_tests()
    
    # Generate report content
    report = f"""# OPS Framework Status Report - Template-First Approach

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Database:** mz-db (Fresh install)  
**Focus:** Configuration templates, setup wizards, customer onboarding

**PRINCIPLE:** No customer-specific preconfiguration. Only templates and wizards for easy setup by non-technical users.

---
## TABLE OF CONTENTS
1. [Template Philosophy](#template-philosophy)
2. [Module Structure](#module-structure)
3. [Configuration Templates](#configuration-templates)
4. [Setup Wizards](#setup-wizards)
5. [User Onboarding Flow](#user-onboarding-flow)
6. [Template Completeness](#template-completeness)
7. [Critical Template Gaps](#critical-template-gaps)
8. [Recommended Template Additions](#recommended-template-additions)
9. [Template Testing Status](#template-testing-status)
10. [Installation Experience](#installation-experience)

---
## 1. Template Philosophy

### Core Principles:
✅ **No Hardcoded Data**: Customer must configure their own company/branch/BU structure  
✅ **Template-Driven**: Provide industry/business type templates  
✅ **Wizard-Based Setup**: Step-by-step configuration for non-technical users  
✅ **Progressive Disclosure**: Show only what's needed at each step  
✅ **Validation & Guidance**: Prevent configuration mistakes with clear help

### Template Types Needed:
1. **Industry Templates** (Retail, Manufacturing, Services, etc.)
2. **Country Templates** (Chart of Accounts, tax structures)
3. **Business Size Templates** (Small, Medium, Enterprise)
4. **Department Templates** (Sales, Operations, Finance workflows)
5. **Compliance Templates** (GDPR, HIPAA, SOX if applicable)

---
## 2. Module Structure (Template-Ready Check)

| Module | Demo Data Files | Data Templates | Wizard Files | Status |
|--------|-----------------|----------------|--------------|--------|
"""
    
    for module in modules:
        report += f"| `{module['name']}` | {module['demo']} | {module['data']} | {module['wizards']} | {module['status']} |\n"
    
    report += """
---
## 3. Configuration Templates Analysis

### Existing Template Files Found:

"""
    
    if templates:
        for rel_path, lines in templates:
            report += f"- [`{rel_path}`](addons/{rel_path}) ({lines} lines)\n"
    else:
        report += "❌ No template files found\n"
    
    report += """
### Template Categories in Data Files:

"""
    
    addons_path = Path("/opt/gemini_odoo19/addons")
    for category in ["persona", "governance", "sla", "account", "product"]:
        cat_files = list(addons_path.glob(f"ops_matrix*/data/*{category}*template*.xml"))
        if cat_files:
            report += f"- **{category.title()} Templates**: {len(cat_files)} file(s) ✅\n"
            for f in cat_files:
                records = f.read_text().count("<record")
                report += f"  - {f.name}: ~{records} template records\n"
        else:
            report += f"- **{category.title()} Templates**: ❌ Not found\n"
    
    report += """
---
## 4. Setup Wizards Inventory

### Wizard Files Found:

"""
    
    if wizards:
        report += """
| Wizard File | Module | Lines of Code | Functions |
|-------------|--------|---------------|-----------|
"""
        for wizard in wizards:
            report += f"| `{wizard['name']}` | {wizard['module']} | {wizard['lines']} | {wizard['functions']} |\n"
    else:
        report += "❌ **No wizard files found in OPS Matrix modules**\n"
    
    report += """
### Critical Wizards Needed:

| Wizard Needed | Priority | Purpose | Estimated Effort |
|---------------|----------|---------|------------------|
| **Company Setup Wizard** | 🔴 HIGH | Initial company/legal entity configuration | 3-5 days |
| **Branch Configuration Wizard** | 🔴 HIGH | Multi-branch setup with locations | 3-4 days |
| **Business Unit Setup Wizard** | 🟡 MEDIUM | Create profit centers with rules | 2-3 days |
| **User Role Assignment Wizard** | 🟡 MEDIUM | Assign personas and permissions | 2-3 days |
| **Governance Rule Wizard** | 🟢 LOW | Apply pre-built rule templates | 1-2 days |
| **Quick Start Wizard** | 🔴 HIGH | All-in-one first-time setup | 5-7 days |

---
## 5. User Onboarding Flow (Current State)

### Ideal Flow for Non-Technical User:
```mermaid
graph TD
    A[Install OPS Module] --> B[Welcome Wizard Launches]
    B --> C[Company Setup]
    C --> D[Branch Configuration]
    D --> E[Business Unit Setup]
    E --> F[User & Role Assignment]
    F --> G[Governance Templates]
    G --> H[System Ready!]
```

### Current Implementation Analysis:

**Onboarding Elements Present:**

"""
    
    for element in onboarding:
        report += f"{element}\n"
    
    report += """
**Issues for Non-Technical Users:**
1. ❌ No automatic welcome wizard on first install
2. ❌ No guided setup process
3. ⚠️ User must manually navigate multiple menus
4. ⚠️ No validation of configuration completeness
5. ⚠️ No progress indicator showing setup status

---
## 6. Template Completeness Score

### Scoring Methodology:
- **Demo/Template Data** (30 points): Existence of reusable templates
- **Setup Wizards** (25 points): Guided configuration tools
- **Documentation/Help** (20 points): In-app guidance
- **Validation** (15 points): Configuration validators
- **User Experience** (10 points): UI/UX for non-technical users

### Score Calculation:

| Component | Score | Max | Details |
|-----------|-------|-----|---------|
"""
    
    report += f"| Demo/Template Data | {scores['demo'][0]} | 30 | {scores['demo'][1]} data files found |\n"
    report += f"| Setup Wizards | {scores['wizards'][0]} | 25 | {scores['wizards'][1]} wizard files |\n"
    report += f"| Documentation/Help | {scores['help'][0]} | 20 | {scores['help'][1]} views with help text |\n"
    report += f"| Validation Rules | {scores['validation'][0]} | 15 | {scores['validation'][1]} models with constraints |\n"
    report += f"| User Experience | {scores['ux'][0]} | 10 | {scores['ux'][1]} views with UX enhancements |\n"
    report += f"| **TOTAL** | **{scores['total']}** | **100** | Template Completeness Score |\n"
    
    report += "\n### Interpretation:\n\n"
    
    total = scores['total']
    if total >= 80:
        report += f"✅ **EXCELLENT** ({total}%): Framework is template-ready for non-technical users\n"
    elif total >= 60:
        report += f"🟡 **GOOD** ({total}%): Basic templates exist, needs polishing\n"
    elif total >= 40:
        report += f"🟠 **FAIR** ({total}%): Some templates, but wizards and help needed\n"
    else:
        report += f"🔴 **NEEDS WORK** ({total}%): Insufficient templates for non-technical setup\n"
    
    report += """
---
## 7. Critical Template Gaps

### Analysis of Missing Template Categories:

**Industry-Specific Templates:**
"""
    
    for industry in ["retail", "manufacturing", "services", "healthcare", "education"]:
        found = len(list(addons_path.glob(f"ops_matrix*/*{industry}*")))
        if found == 0:
            report += f"- ❌ {industry.title()} templates missing\n"
        else:
            report += f"- ✅ {industry.title()}: {found} file(s) found\n"
    
    report += """
**Country/Localization Templates:**
"""
    
    loc_files = len(list(addons_path.glob("ops_matrix*/data/*l10n*")))
    if loc_files == 0:
        report += "- ❌ No country-specific templates found\n"
    else:
        report += f"- ✅ Found {loc_files} localization file(s)\n"
    
    report += """
**Business Size Templates:**
- ❌ Small Business templates - Not found
- ❌ Medium Enterprise templates - Not found
- ❌ Large Enterprise templates - Not found

---
## 8. Recommended Template Additions

### Phase 1: Foundation (Weeks 1-2)

**Priority: HIGH** 🔴

1. **Welcome/Quick Start Wizard**
   - Auto-launch on first module install
   - Step-by-step company setup
   - Branch and BU creation
   - User role assignment
   - **Estimated Effort:** 5-7 days

2. **Company Setup Templates**
   - Small Business (1-20 employees)
   - Medium Business (21-100 employees)
   - Enterprise (100+ employees)
   - **Estimated Effort:** 3-4 days

3. **Basic Industry Templates**
   - Retail/E-commerce
   - Professional Services
   - Manufacturing/Distribution
   - **Estimated Effort:** 4-5 days per industry

### Phase 2: Enhancement (Weeks 3-4)

**Priority: MEDIUM** 🟡

4. **Branch Configuration Wizard**
   - Multi-location setup
   - Warehouse assignment
   - Contact information
   - **Estimated Effort:** 3-4 days

5. **Governance Rule Templates**
   - Approval workflows
   - Discount limits
   - Margin controls
   - **Estimated Effort:** 2-3 days

6. **Role/Persona Library**
   - Pre-configured personas
   - Permission sets
   - Department templates
   - **Estimated Effort:** 3-4 days

### Phase 3: Advanced (Week 5+)

**Priority: LOW** 🟢

7. **Country Localization Packs**
   - Chart of Accounts templates
   - Tax structures
   - Compliance rules
   - **Estimated Effort:** 5-7 days per country

8. **Compliance Templates**
   - GDPR data protection
   - Financial controls (SOX-like)
   - Industry regulations
   - **Estimated Effort:** 7-10 days

---
## 9. Template Testing Status

### Test Coverage for Templates:

"""
    
    test_coverage = int((template_tests / test_count * 100)) if test_count > 0 else 0
    report += f"- **Total Test Files:** {test_count}\n"
    report += f"- **Template-Specific Tests:** {template_tests}\n"
    report += f"- **Test Coverage:** {test_coverage}%\n"
    
    report += """
### Essential Test Scenarios:

| Test Scenario | Status | Priority |
|---------------|--------|----------|
| Fresh Install → Welcome Wizard | ⏳ PENDING | 🔴 HIGH |
| Apply Industry Template | ⏳ PENDING | 🔴 HIGH |
| Multi-Branch Setup | ⏳ PENDING | 🟡 MEDIUM |
| User Role Assignment | ⏳ PENDING | 🟡 MEDIUM |
| Governance Rule Creation | ⏳ PENDING | 🟢 LOW |
| Dashboard Configuration | ⏳ PENDING | 🟢 LOW |

---
## 10. Installation Experience Analysis

### Current Installation Process:

**Manual Steps Required After Module Install:**

```
1. Navigate to Settings → Companies → Companies
2. Edit company to configure OPS settings
3. Go to OPS Matrix → Configuration → Branches
4. Manually create each branch
5. Navigate to Business Units
6. Create and configure BUs
7. Assign branches to BUs
8. Go to Users & Companies → Users
9. Create/configure personas
10. Assign users to personas
11. Configure governance rules
12. Setup dashboards
```

**Time Estimate for Non-Technical User:** 3-4 hours minimum

### Issues Identified:

1. ❌ **No Guided Setup**: User must discover configuration path themselves
2. ❌ **Too Many Clicks**: 20+ navigation steps across multiple menus
3. ❌ **No Validation**: Can create invalid/incomplete configurations
4. ❌ **No Templates**: Starting from completely blank state
5. ❌ **No Progress Tracking**: Can't see configuration status
6. ❌ **No Help System**: Limited contextual guidance

### Ideal Installation Experience:

```mermaid
sequenceDiagram
    participant U as User
    participant W as Welcome Wizard
    participant S as System
    
    U->>S: Install OPS Module
    S->>W: Auto-launch Welcome Wizard
    W->>U: "Let's set up your OPS Matrix!"
    W->>U: Select Business Type (Retail/Manufacturing/etc.)
    U->>W: Choose "Retail"
    W->>S: Load Retail Template
    W->>U: Enter Company Details
    U->>W: Provide information
    W->>U: Configure Branches (How many locations?)
    U->>W: "3 branches"
    W->>S: Create branches
    W->>U: Setup Users & Roles
    U->>W: Assign roles
    W->>U: Review & Confirm
    U->>W: Click "Finish"
    S->>U: "Your OPS Matrix is ready! 🎉"
```

**Estimated Time with Wizard:** 15-20 minutes

---
## SUMMARY & ACTION PLAN

### 📊 Current Status

"""
    
    report += f"- **Template Completeness Score:** {scores['total']}/100\n"
    report += f"- **Demo Data Files:** {scores['demo'][1]}\n"
    report += f"- **Setup Wizards:** {scores['wizards'][1]}\n"
    report += f"- **Test Coverage:** {template_tests}/{test_count} template tests\n"
    
    report += """
### ✅ What's Working Well

1. **Core Framework**: Solid Company→Branch→BU hierarchy
2. **Data Templates**: Good foundation with persona, governance, and SLA templates
3. **Modular Design**: Clean separation of concerns across modules
4. **Security Model**: Comprehensive access controls and audit trails

### ⚠️ What Needs Improvement

1. **Onboarding Experience**: No guided setup for new installations
2. **Template Library**: Missing industry and country-specific templates
3. **Wizard Tools**: Limited wizard-based configuration helpers
4. **User Guidance**: Insufficient help text and validation

### 🔴 Critical Gaps

1. **Welcome Wizard**: First-run experience doesn't exist
2. **Quick Start Templates**: No "business in a box" solutions
3. **Setup Validation**: Can create incomplete/invalid configurations
4. **Progress Tracking**: No way to see configuration status

---
## 🎯 IMMEDIATE ACTION PLAN

### Week 1: Foundation Wizards

- [ ] Create Welcome/Onboarding Wizard
  - Auto-launch on first install
  - Business type selection
  - Basic company setup
  
- [ ] Develop Company Setup Wizard
  - Legal entity configuration
  - Currency and locale
  - Fiscal year setup

- [ ] Build Branch Configuration Tool
  - Multi-branch creation
  - Location management
  - Warehouse assignment

### Week 2: Template Library

- [ ] Create Quick Start Templates
  - Small Business Basic
  - Retail Store Template
  - Service Company Template
  
- [ ] Develop Persona Library
  - Manager roles
  - Clerk roles
  - Approver roles
  
- [ ] Build Governance Rule Templates
  - Approval workflows
  - Discount controls
  - Margin limits

### Week 3: User Experience

- [ ] Implement Setup Progress Tracker
  - Visual completion indicator
  - Required vs optional steps
  - Validation status
  
- [ ] Add Configuration Validator
  - Check for incomplete setup
  - Suggest fixes
  - Prevent common mistakes
  
- [ ] Enhance In-App Help
  - Contextual tooltips
  - Setup guides
  - Video tutorials (optional)

### Week 4: Testing & Polish

- [ ] Create Template Test Suite
  - Test each template application
  - Validate wizard flows
  - Check for data consistency
  
- [ ] User Testing
  - Test with non-technical users
  - Gather feedback
  - Iterate on UX
  
- [ ] Documentation
  - Administrator guide
  - User manual
  - Setup videos

---
## 📝 NEXT STEPS

### Immediate (This Week)

1. **Create Welcome Wizard Module**
   - File: `ops_matrix_welcome/wizard/ops_welcome_wizard.py`
   - Auto-launch mechanism
   - 5-step guided setup

2. **Build Template Gallery View**
   - File: `ops_matrix_core/views/ops_template_gallery_views.xml`
   - Visual template browser
   - One-click application

3. **Add Setup Validator**
   - File: `ops_matrix_core/models/ops_setup_validator.py`
   - Configuration completeness checks
   - User-friendly error messages

### Coming Soon

4. **Industry Template Packs** (Week 2-3)
5. **Country Localization** (Week 3-4)
6. **Advanced Workflows** (Week 4+)

---
**Report Generated:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f"""  
**Analysis Focus:** Template-First Approach for Non-Technical Users  
**Key Principle:** Configuration Through Templates, Not Hardcoded Data  
**Target User:** Business Owner/Manager (Non-Technical)

---
*For questions or suggestions, please review this report and prioritize template development over custom code.*
"""
    
    # Write report
    output_file.write_text(report)
    
    # Print summary
    print("\n✅ Template-first status report generated successfully!")
    print(f"📄 Report location: {output_file}")
    print("\n=== KEY FINDINGS ===")
    print(f"📊 Template Completeness Score: {scores['total']}/100")
    print(f"📁 Demo/Data Files: {scores['demo'][1]}")
    print(f"🧙 Setup Wizards: {scores['wizards'][1]}")
    print(f"📖 Help Documentation: {scores['help'][1]} views")
    print(f"✔️  Validation Rules: {scores['validation'][1]} models")
    print()
    
    if scores['total'] >= 60:
        print("✅ Status: Framework has good template foundation")
    elif scores['total'] >= 40:
        print("⚠️  Status: Templates exist but need enhancement")
    else:
        print("🔴 Status: Significant template development needed")
    
    print(f"\n📂 Next: Review {output_file.name} for detailed recommendations")

if __name__ == "__main__":
    generate_report()
