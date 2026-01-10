# OPS Framework - Repository Structure

## Production Files
\`\`\`
ops_framework/
├── README.md                          # Main documentation
├── docker-compose.yml                 # Deployment configuration
├── .gitignore                         # Git ignore rules
│
├── addons/                            # Odoo modules (PRODUCTION)
│   ├── ops_matrix_core/               # Core module
│   │   ├── __manifest__.py
│   │   ├── models/
│   │   ├── views/
│   │   ├── security/
│   │   └── data/
│   ├── ops_matrix_accounting/         # Accounting module
│   │   ├── __manifest__.py
│   │   ├── models/
│   │   ├── views/
│   │   ├── security/
│   │   └── data/
│   ├── ops_matrix_reporting/          # Reporting module
│   │   ├── __manifest__.py
│   │   ├── models/
│   │   └── reports/
│   └── ops_matrix_asset_management/   # Asset module
│       ├── __manifest__.py
│       ├── models/
│       ├── views/
│       └── security/
│
├── config/                            # Configuration files
│   └── odoo.conf
│
├── docs/                              # Documentation
│   ├── QUICK_START.md                 # Quick reference
│   ├── PRODUCTION_READY_FINAL.md      # Production status
│   ├── user/                          # End user docs
│   │   └── USER_MANUAL.md
│   ├── admin/                         # Admin docs
│   │   └── ADMIN_GUIDE.md
│   ├── deployment/                    # Deployment docs
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   └── PRODUCTION_CHECKLIST.md
│   ├── technical/                     # Technical docs
│   │   └── README.md
│   └── screenshots/                   # Sample screenshots
│
└── _archive/                          # Development history
    ├── development/                   # Dev artifacts
    │   ├── claude_files/
    │   └── _backup/
    ├── testing/                       # Test artifacts
    │   ├── screenshots/
    │   ├── results/
    │   └── scripts/
    ├── old_docs/                      # Superseded docs
    │   └── documentations/
    └── logs/                          # Historical logs
\`\`\`

## File Counts

- **Python files:** 200+
- **XML files:** 150+
- **Total modules:** 4
- **Documentation files:** 10+

## What's Included

### Production Ready
✅ 4 complete Odoo modules  
✅ Docker deployment configuration  
✅ Comprehensive documentation  
✅ Configuration templates  

### Archived (Reference)
📦 Development notes and planning  
📦 Test scripts and results  
📦 Historical logs  
📦 Old documentation versions  

## Usage

**For Deployment:** Use files in root and \`addons/\`  
**For Reference:** See \`_archive/\` for development history  
**For Documentation:** See \`docs/\` directory  
