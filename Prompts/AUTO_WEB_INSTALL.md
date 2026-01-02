# Autonomous Module Installation via Web UI

## Configuration
- **Module**: [MODULE_NAME]
- **Database**: mz-db
- **Admin User**: admin
- **Admin Password**: admin
- **Max Retries Per Error**: 5
- **Odoo URL**: http://localhost:8069

---

## CRITICAL RULES

1. **Install via WEB UI simulation, NOT CLI `./odoo-bin -i`**
2. **Track each unique error** - if same error occurs 5 times, STOP and report
3. **Fix errors between attempts** - don't just retry blindly
4. **Log every attempt** with timestamp and result

---

## PHASE 1: Environment Setup

```bash
# Stop existing Odoo
pkill -f odoo-bin || true
sleep 3

# Clear Python cache
find /opt/gemini_odoo19/addons/[MODULE_NAME] -name "*.pyc" -delete
find /opt/gemini_odoo19/addons/[MODULE_NAME] -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Start Odoo server with logging
cd /opt/gemini_odoo19
./odoo-bin -c odoo.conf -d mz-db --log-file=/tmp/odoo_install_test.log --log-level=info &
echo $! > /tmp/odoo.pid
sleep 15

# Verify server is running
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login || { echo "Server failed to start"; exit 1; }
echo "Server running"
```

## PHASE 2: Web UI Installation Script

Create and execute `/tmp/web_install_module.py`:

```python
#!/usr/bin/env python3
"""
Autonomous Web UI Module Installer
Simulates human browser installation with auto-fix capability
"""

import requests
import time
import re
import subprocess
import json
from datetime import datetime

# Configuration
ODOO_URL = "http://localhost:8069"
DB = "mz-db"
USERNAME = "admin"
PASSWORD = "admin"
MODULE_NAME = "[MODULE_NAME]"  # Replace with actual module
MAX_RETRIES_SAME_ERROR = 5
LOG_FILE = "/tmp/install_attempts.log"

# Track errors
error_history = {}
attempt_count = 0

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def get_session():
    """Authenticate and get session"""
    session = requests.Session()
    
    # Get CSRF token
    resp = session.get(f"{ODOO_URL}/web/login")
    
    # Login
    login_data = {
        "login": USERNAME,
        "password": PASSWORD,
        "db": DB,
        "redirect": "/web",
    }
    resp = session.post(f"{ODOO_URL}/web/login", data=login_data)
    
    if "login" in resp.url:
        raise Exception("Login failed")
    
    log("✓ Authenticated successfully")
    return session

def trigger_module_install(session):
    """Trigger module installation via web RPC"""
    
    # First, update module list
    log("Updating module list...")
    session.post(f"{ODOO_URL}/web/dataset/call_kw", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.module.module",
            "method": "update_list",
            "args": [],
            "kwargs": {}
        },
        "id": 1
    })
    time.sleep(3)
    
    # Find module ID
    log(f"Finding module: {MODULE_NAME}")
    resp = session.post(f"{ODOO_URL}/web/dataset/call_kw", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.module.module",
            "method": "search_read",
            "args": [[["name", "=", MODULE_NAME]]],
            "kwargs": {"fields": ["id", "name", "state"]}
        },
        "id": 2
    })
    
    result = resp.json().get("result", [])
    if not result:
        raise Exception(f"Module {MODULE_NAME} not found")
    
    module_id = result[0]["id"]
    module_state = result[0]["state"]
    log(f"✓ Found module ID: {module_id}, State: {module_state}")
    
    if module_state == "installed":
        log("Module already installed, triggering upgrade...")
        action = "button_immediate_upgrade"
    else:
        log("Installing module...")
        action = "button_immediate_install"
    
    # Trigger installation/upgrade
    resp = session.post(f"{ODOO_URL}/web/dataset/call_kw", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.module.module",
            "method": action,
            "args": [[module_id]],
            "kwargs": {}
        },
        "id": 3
    })
    
    return resp.json()

def check_for_errors():
    """Check Odoo log for errors"""
    time.sleep(5)  # Wait for logs to flush
    
    result = subprocess.run(
        ["tail", "-100", "/tmp/odoo_install_test.log"],
        capture_output=True, text=True
    )
    
    log_content = result.stdout
    
    # Look for errors
    error_patterns = [
        r"(Error.*?)\n",
        r"(Exception.*?)\n", 
        r"(Traceback.*?)(?=\d{4}-\d{2}-\d{2}|\Z)",
        r"(ParseError.*?)\n",
        r"(ValueError.*?)\n",
        r"(KeyError.*?)\n",
        r"(AttributeError.*?)\n",
        r"(psycopg2\..*?Error.*?)\n",
    ]
    
    errors = []
    for pattern in error_patterns:
        matches = re.findall(pattern, log_content, re.DOTALL | re.IGNORECASE)
        errors.extend(matches)
    
    return errors, log_content

def get_error_signature(error):
    """Create unique signature for error to track duplicates"""
    # Extract key parts: error type and location
    sig = re.sub(r'line \d+', 'line X', str(error)[:200])
    sig = re.sub(r'0x[0-9a-f]+', '0xXXX', sig)
    return sig

def attempt_auto_fix(error, log_content):
    """Attempt to automatically fix common errors"""
    log(f"Attempting auto-fix for: {error[:100]}...")
    
    # Pattern 1: Missing field in view
    if "Field" in error and "does not exist" in error:
        match = re.search(r"Field `(\w+)` does not exist.*model `([\w.]+)`", error)
        if match:
            field_name, model_name = match.groups()
            log(f"Missing field '{field_name}' in model '{model_name}'")
            # Could add field or remove from view - report for now
            return False
    
    # Pattern 2: External ID not found
    if "External ID not found" in error:
        match = re.search(r"External ID not found.*: ([\w.]+)", error)
        if match:
            ext_id = match.group(1)
            log(f"Missing External ID: {ext_id}")
            # Need to create the record or fix reference
            return False
    
    # Pattern 3: XML syntax error
    if "ParseError" in error or "XMLSyntaxError" in error:
        match = re.search(r"file ['\"](.+?\.xml)['\"].*line (\d+)", error, re.IGNORECASE)
        if match:
            file_path, line_num = match.groups()
            log(f"XML error in {file_path} at line {line_num}")
            # Run xmllint for details
            subprocess.run(["xmllint", "--noout", file_path])
            return False
    
    # Pattern 4: branch_id vs ops_branch_id
    if "branch_id" in error and "does not exist" in error:
        log("Detected branch_id naming issue, fixing...")
        subprocess.run([
            "find", f"/opt/gemini_odoo19/addons/{MODULE_NAME}",
            "-name", "*.xml", "-exec",
            "sed", "-i", "s/branch_id/ops_branch_id/g", "{}", ";"
        ])
        subprocess.run([
            "find", f"/opt/gemini_odoo19/addons/{MODULE_NAME}",
            "-name", "*.py", "-exec",
            "sed", "-i", "s/'branch_id'/'ops_branch_id'/g", "{}", ";"
        ])
        return True
    
    # Pattern 5: Access rights
    if "AccessError" in error or "access rights" in error.lower():
        log("Access rights issue detected")
        return False
    
    log("No auto-fix available for this error")
    return False

def verify_installation(session):
    """Verify module is properly installed"""
    resp = session.post(f"{ODOO_URL}/web/dataset/call_kw", json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": "ir.module.module",
            "method": "search_read",
            "args": [[["name", "=", MODULE_NAME]]],
            "kwargs": {"fields": ["state"]}
        },
        "id": 4
    })
    
    result = resp.json().get("result", [])
    if result and result[0]["state"] == "installed":
        return True
    return False

def main():
    global attempt_count, error_history
    
    log("="*60)
    log(f"STARTING AUTONOMOUS WEB INSTALLATION: {MODULE_NAME}")
    log("="*60)
    
    # Clear previous log
    open("/tmp/odoo_install_test.log", "w").close()
    
    while True:
        attempt_count += 1
        log(f"\n--- ATTEMPT {attempt_count} ---")
        
        try:
            session = get_session()
            result = trigger_module_install(session)
            
            # Check result
            if "error" in result:
                error_msg = str(result["error"])
                log(f"✗ Installation returned error: {error_msg[:200]}")
            else:
                # Check logs for errors
                errors, log_content = check_for_errors()
                
                if not errors:
                    # Verify installation
                    if verify_installation(session):
                        log("\n" + "="*60)
                        log("✓✓✓ INSTALLATION SUCCESSFUL ✓✓✓")
                        log("="*60)
                        return True
                
                if errors:
                    error = errors[-1]  # Most recent error
                    sig = get_error_signature(error)
                    
                    error_history[sig] = error_history.get(sig, 0) + 1
                    
                    log(f"Error signature count: {error_history[sig]}/{MAX_RETRIES_SAME_ERROR}")
                    
                    if error_history[sig] >= MAX_RETRIES_SAME_ERROR:
                        log("\n" + "="*60)
                        log("⚠️  STOPPING: Same error occurred 5 times")
                        log("="*60)
                        log("HUMAN INTERVENTION REQUIRED")
                        log(f"Error: {error}")
                        log(f"\nFull log: /tmp/odoo_install_test.log")
                        log(f"Attempt log: {LOG_FILE}")
                        return False
                    
                    # Attempt auto-fix
                    fixed = attempt_auto_fix(error, log_content)
                    
                    if fixed:
                        log("Fix applied, restarting server...")
                        subprocess.run(["pkill", "-f", "odoo-bin"])
                        time.sleep(3)
                        subprocess.Popen([
                            "/opt/gemini_odoo19/odoo-bin",
                            "-c", "/opt/gemini_odoo19/odoo.conf",
                            "-d", DB,
                            "--log-file=/tmp/odoo_install_test.log"
                        ])
                        time.sleep(15)
                    else:
                        log("Auto-fix failed, will retry...")
                        time.sleep(5)
                    
        except Exception as e:
            log(f"✗ Exception: {e}")
            time.sleep(5)
    
    return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
```

## PHASE 3: Execute Installation

```bash
# Make executable and run
chmod +x /tmp/web_install_module.py
python3 /tmp/web_install_module.py
```

## PHASE 4: If Auto-Fix Fails

When the script stops after 5 retries of same error:

1. Read `/tmp/install_attempts.log` for attempt history
2. Read `/tmp/odoo_install_test.log` for full Odoo log
3. Report to human with:
   - Error message
   - File and line number (if identifiable)
   - What auto-fixes were attempted
   - Recommendation for manual fix

---

## STOP CONDITIONS

STOP and report to human if:
- [ ] Same error occurs 5 consecutive times
- [ ] Python syntax error that can't be auto-fixed
- [ ] Missing external dependency (Python package)
- [ ] Database connection error
- [ ] Permission/security error requiring config change