# OPS Matrix Framework - Installation Guide

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+, CentOS 7+, or equivalent)
- **Python**: Version 3.10 or higher
- **Database**: PostgreSQL 14 or higher
- **Web Server**: Compatible with Odoo 19 CE
- **Memory**: Minimum 4GB RAM (8GB recommended for production)
- **Storage**: 20GB+ free disk space

### Software Dependencies
- Odoo 19 Community Edition
- Python libraries: `Cython` (optional, for vault build), `secrets`, `datetime`
- System packages: `python3-dev`, `build-essential`, `postgresql-server-dev-all`

## Installation Steps

### 1. Prepare the Environment

#### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Create Database User
```bash
sudo -u postgres psql
CREATE USER odoo WITH PASSWORD 'your_password';
ALTER USER odoo CREATEDB;
\q
```

#### Install Python Dependencies
```bash
# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip

# Install system dependencies for Odoo
sudo apt install python3-dev build-essential libxml2-dev libxslt-dev libldap2-dev libsasl2-dev libssl-dev
```

### 2. Install Odoo 19 CE

#### Download and Install Odoo
```bash
# Create Odoo user
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# Download Odoo 19
sudo -u odoo git clone https://github.com/odoo/odoo.git /opt/odoo/odoo19 -b 19.0

# Create virtual environment
sudo -u odoo python3 -m venv /opt/odoo/odoo19-venv
sudo -u odoo /opt/odoo/odoo19-venv/bin/pip install -r /opt/odoo/odoo19/requirements.txt
```

#### Configure Odoo
Create configuration file `/etc/odoo/odoo.conf`:
```ini
[options]
admin_passwd = your_admin_password
db_host = localhost
db_port = 5432
db_user = odoo
db_password = your_db_password
addons_path = /opt/odoo/odoo19/addons,/opt/odoo/ops_matrix_addons
logfile = /var/log/odoo/odoo.log
```

### 3. Install OPS Matrix Framework Modules

#### Download the Modules
```bash
# Create addons directory
sudo mkdir -p /opt/odoo/ops_matrix_addons

# Copy OPS Matrix modules (assuming they are in your workspace)
sudo cp -r /opt/gemini_odoo19/addons/ops_matrix_core /opt/odoo/ops_matrix_addons/
sudo cp -r /opt/gemini_odoo19/addons/ops_matrix_accounting /opt/odoo/ops_matrix_addons/

# Set proper permissions
sudo chown -R odoo:odoo /opt/odoo/ops_matrix_addons
```

#### Install Required Dependencies
```bash
# Install additional Python packages if needed
sudo -u odoo /opt/odoo/odoo19-venv/bin/pip install Cython xlwt xlrd
```

### 4. Initialize the Database

#### Create Database
```bash
# Create the database
sudo -u odoo createdb -O odoo mz-db
```

#### Start Odoo and Install Modules
```bash
# Start Odoo with module installation
sudo -u odoo /opt/odoo/odoo19-venv/bin/python /opt/odoo/odoo19/odoo-bin \
  -c /etc/odoo/odoo.conf \
  -d mz-db \
  --init=ops_matrix_core,ops_matrix_accounting \
  --stop-after-init
```

### 5. Configure System Services

#### Create Systemd Service
Create `/etc/systemd/system/odoo.service`:
```ini
[Unit]
Description=Odoo 19 with OPS Matrix Framework
Requires=postgresql.service
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo
PermissionsStartOnly=true
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo19-venv/bin/python /opt/odoo/odoo19/odoo-bin -c /etc/odoo/odoo.conf
StandardOutput=journal+console

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo
```

### 6. Optional: Build Vault (Source Code Protection)

#### Install Cython
```bash
sudo apt install cython3 python3-cython
```

#### Run Vault Build Script
```bash
# Copy the build script
sudo cp /opt/gemini_odoo19/scripts/build_vault.sh /opt/odoo/

# Make executable
sudo chmod +x /opt/odoo/build_vault.sh

# Run test build first
sudo -u odoo /opt/odoo/build_vault.sh --test-mode

# Run full build
sudo -u odoo /opt/odoo/build_vault.sh
```

## Docker Installation (Alternative)

### Using Docker Compose
Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: mz-db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  odoo:
    image: odoo:19
    depends_on:
      - db
    ports:
      - "8089:8069"
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_USER: odoo
      DB_PASSWORD: odoo
      DB_NAME: mz-db
    volumes:
      - ./addons:/mnt/extra-addons
      - odoo_data:/var/lib/odoo

volumes:
  postgres_data:
  odoo_data:
```

#### Start Services
```bash
docker-compose up -d
```

#### Install OPS Modules via Web Interface
1. Access Odoo at `http://localhost:8089`
2. Log in with admin/admin
3. Go to Apps → Update Apps List
4. Search and install:
   - OPS Matrix Core
   - OPS Matrix Accounting

## Post-Installation Configuration

### 1. Set Up Initial Data

#### Create Company Structure
1. Navigate to **Settings → Companies**
2. Configure your main company
3. On the **Operational Branches** tab, set up branches linked to the company

#### Configure Branches
Branches are configured via the Operational Branches tab in the company form. Additional branch management is available at **OPS Matrix → Branches**.

#### Set Up Business Units
1. Navigate to **OPS Matrix → Business Units**
2. Create BU records
3. Assign BU leaders

#### Set Up Business Units
1. Navigate to **OPS Matrix → Business Units**
2. Create BU records
3. Assign BU leaders

### 2. Configure Security

#### Create Personas
1. Go to **OPS Matrix → Personas**
2. Create role definitions
3. Assign branch/BU access rights

#### Set Up Users
1. Navigate to **Settings → Users**
2. Create user accounts
3. Assign personas to users

### 3. Configure Governance Rules

#### Set Up Approval Rules
1. Go to **OPS Matrix → Governance → Rules**
2. Create approval workflows
3. Configure thresholds and conditions

#### Configure SLA Templates
1. Navigate to **OPS Matrix → Governance → SLA Templates**
2. Define service level agreements
3. Set up monitoring rules

## Verification

### Check Module Installation
```bash
# Verify modules are installed
curl -X POST http://localhost:8089/api/v1/ops_matrix/health
```

### Test Basic Functionality
1. Log in to Odoo web interface
2. Verify OPS Matrix menus are available
3. Test creating a branch
4. Test creating a persona
5. Verify dashboards load

### Run Health Checks
```bash
# Check database connections
sudo -u odoo psql -d mz-db -c "SELECT version();"

# Check Odoo logs
sudo tail -f /var/log/odoo/odoo.log

# Test API endpoints
curl -H "X-API-Key: your_test_key" http://localhost:8089/api/v1/ops_matrix/me
```

## Troubleshooting Installation Issues

### Common Issues

#### Module Not Found Error
```
Error: Module 'ops_matrix_core' not found
```
**Solution**: Verify addons path in `odoo.conf` and check file permissions.

#### Database Connection Failed
```
Error: FATAL: password authentication failed for user "odoo"
```
**Solution**: Check PostgreSQL user credentials and database permissions.

#### Import Errors
```
ImportError: No module named 'cython'
```
**Solution**: Install missing Python dependencies in the virtual environment.

#### Permission Errors
```
Permission denied: '/opt/odoo/addons'
```
**Solution**: Ensure proper ownership and permissions for Odoo directories.

## Next Steps

After successful installation:
1. Follow the [Quick Start Guide](03_Quick_Start_Guide.md) for initial setup
2. Review the [Administrator Guide](05_Administrator_Guide.md) for system management
3. Configure users and security according to your organizational structure
4. Set up governance rules and approval workflows
5. Train users on the new system features

For additional help, refer to the [Troubleshooting](09_Troubleshooting.md) guide or check the [FAQ](10_FAQ.md).