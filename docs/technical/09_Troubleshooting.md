# OPS Matrix Framework - Troubleshooting Guide

This troubleshooting guide provides solutions to common issues encountered when using the OPS Matrix Framework. It covers installation problems, configuration issues, operational errors, and performance concerns.

## Installation Issues

### Module Installation Failures

#### Error: "Module 'ops_matrix_core' not found"
**Symptoms:**
- Module not appearing in Apps list
- Import errors during startup

**Solutions:**
1. **Verify Addons Path:**
   ```bash
   # Check odoo.conf
   grep addons_path /etc/odoo/odoo.conf

   # Ensure path includes OPS modules
   addons_path = /opt/odoo/odoo19/addons,/opt/odoo/ops_matrix_addons
   ```

2. **Check File Permissions:**
   ```bash
   sudo chown -R odoo:odoo /opt/odoo/ops_matrix_addons
   sudo chmod -R 755 /opt/odoo/ops_matrix_addons
   ```

3. **Validate Module Structure:**
   ```bash
   ls -la /opt/odoo/ops_matrix_addons/ops_matrix_core/
   # Should contain: __init__.py, __manifest__.py, models/, views/, etc.
   ```

4. **Restart Odoo:**
   ```bash
   sudo systemctl restart odoo
   # Or for Docker
   docker restart gemini_odoo19
   ```

#### Error: "Module dependencies not satisfied"
**Symptoms:**
- Installation fails due to missing dependencies

**Solutions:**
1. **Install Required Modules First:**
   ```bash
   # Update module list
   odoo -u base --stop-after-init

   # Install dependencies
   odoo -u account,sale,purchase,stock --stop-after-init
   ```

2. **Check Module Sequence:**
   ```bash
   # Install in correct order
   odoo -u ops_matrix_core --stop-after-init
   odoo -u ops_matrix_accounting --stop-after-init
   odoo -u ops_matrix_reporting --stop-after-init
   ```

### Database Connection Issues

#### Error: "FATAL: password authentication failed"
**Symptoms:**
- Cannot connect to PostgreSQL database

**Solutions:**
1. **Verify Database User:**
   ```bash
   sudo -u postgres psql
   \du  # List users
   ALTER USER odoo PASSWORD 'new_password';
   \q
   ```

2. **Update Odoo Configuration:**
   ```ini
   [options]
   db_host = localhost
   db_port = 5432
   db_user = odoo
   db_password = correct_password
   db_name = mz-db
   ```

3. **Test Database Connection:**
   ```bash
   psql -h localhost -U odoo -d mz-db
   ```

### Docker Installation Problems

#### Error: "Container fails to start"
**Symptoms:**
- Docker container exits immediately

**Solutions:**
1. **Check Container Logs:**
   ```bash
   docker logs gemini_odoo19
   ```

2. **Verify Environment Variables:**
   ```bash
   docker run --rm gemini_odoo19 env
   ```

3. **Check Volume Mounts:**
   ```bash
   docker inspect gemini_odoo19 | grep -A 10 Mounts
   ```

4. **Test with Minimal Configuration:**
   ```bash
   docker run -it --rm -p 8089:8069 gemini_odoo19 --help
   ```

## Configuration Issues

### Branch and Business Unit Problems

#### Users Cannot See Expected Data
**Symptoms:**
- Users report missing records or empty lists

**Solutions:**
1. **Verify Persona Assignments:**
   ```sql
   -- Check user personas
   SELECT u.login, p.name as persona_name
   FROM res_users u
   JOIN ops_persona_res_users_rel pur ON pur.res_users_id = u.id
   JOIN ops_persona p ON p.id = pur.ops_persona_id
   WHERE u.login = 'user@example.com';
   ```

2. **Check Branch Access:**
   ```sql
   -- Verify branch assignments
   SELECT u.login, b.name as branch_name
   FROM res_users u
   JOIN ops_persona p ON p.id IN (
       SELECT ops_persona_id FROM ops_persona_res_users_rel
       WHERE res_users_id = u.id
   )
   JOIN ops_branch b ON b.id IN (
       SELECT ops_branch_id FROM ops_persona_allowed_branch_rel
       WHERE ops_persona_id = p.id
   )
   WHERE u.login = 'user@example.com';
   ```

3. **Validate Record Rules:**
   ```sql
   -- Check active record rules
   SELECT name, model_id, domain_force
   FROM ir_rule
   WHERE model_id = 'sale.order'
   AND active = true;
   ```

4. **Test with Admin User:**
   - Temporarily assign admin rights to verify data exists
   - Check if issue is permission-related

#### Branch Field Not Populating
**Symptoms:**
- Transactions created without branch assignment

**Solutions:**
1. **Check Default Branch Logic:**
   ```python
   # In sale.order model
   @api.model
   def default_get(self, fields):
       res = super().default_get(fields)
       if 'ops_branch_id' in fields:
           # Auto-assign based on user context
           user_branch = self.env.user.ops_allowed_branch_ids[:1]
           if user_branch:
               res['ops_branch_id'] = user_branch.id
       return res
   ```

2. **Verify User Context:**
   - Ensure user has active persona
   - Check persona has branch assignments
   - Validate user is not locked

### API Key Issues

#### API Authentication Failing
**Symptoms:**
- API calls return 401 Unauthorized

**Solutions:**
1. **Verify API Key Format:**
   ```bash
   # Check header format
   curl -H "X-API-Key: your_key_here" http://localhost:8089/api/v1/ops_matrix/me
   ```

2. **Check Key Status:**
   ```sql
   -- Verify key exists and is active
   SELECT id, name, active, expiration_date
   FROM ops_api_key
   WHERE key_hash = encode(sha256('your_key_here'::bytea), 'hex');
   ```

3. **Validate Persona Permissions:**
   ```sql
   -- Check associated persona
   SELECT p.name, p.active
   FROM ops_api_key k
   JOIN ops_persona p ON p.id = k.persona_id
   WHERE k.id = 'your_key_id';
   ```

4. **Review API Logs:**
   ```sql
   -- Check audit logs
   SELECT timestamp, endpoint, response_status, error_message
   FROM ops_audit_log
   WHERE api_key_id = 'your_key_id'
   ORDER BY timestamp DESC LIMIT 10;
   ```

## Operational Issues

### Performance Problems

#### Slow Dashboard Loading
**Symptoms:**
- Dashboards take >30 seconds to load

**Solutions:**
1. **Check Database Indexes:**
   ```sql
   -- Verify indexes on OPS fields
   SELECT indexname, tablename, indexdef
   FROM pg_indexes
   WHERE tablename LIKE 'sale_order'
   AND indexdef LIKE '%ops_branch_id%';
   ```

2. **Optimize Queries:**
   ```sql
   -- Analyze slow queries
   SELECT query, calls, total_time, mean_time
   FROM pg_stat_statements
   ORDER BY total_time DESC LIMIT 10;
   ```

3. **Clear Cache:**
   ```bash
   # Restart Odoo to clear caches
   sudo systemctl restart odoo
   ```

4. **Check System Resources:**
   ```bash
   # Monitor memory and CPU
   htop
   free -h
   df -h
   ```

#### Large Report Exports Failing
**Symptoms:**
- Excel exports timeout or fail

**Solutions:**
1. **Increase Timeout Settings:**
   ```ini
   # In odoo.conf
   limit_time_cpu = 600  # 10 minutes
   limit_time_real = 1200  # 20 minutes
   ```

2. **Optimize Export Queries:**
   ```python
   # Use background jobs for large exports
   @api.model
   def _export_large_dataset(self):
       # Implement background processing
       job = self.env['queue.job'].create({
           'name': 'Large Excel Export',
           'method': '_generate_excel_background',
           'args': (self.ids,),
       })
       return job
   ```

3. **Implement Pagination:**
   ```python
   # Break large exports into chunks
   def _export_in_batches(self, records, batch_size=1000):
       for i in range(0, len(records), batch_size):
           batch = records[i:i + batch_size]
           self._process_batch(batch)
   ```

### Approval Workflow Issues

#### Approvals Not Triggering
**Symptoms:**
- Transactions not entering approval workflow

**Solutions:**
1. **Check Governance Rules:**
   ```sql
   -- Verify active rules
   SELECT name, model_name, conditions, active
   FROM ops_governance_rule
   WHERE model_name = 'sale.order' AND active = true;
   ```

2. **Validate Rule Conditions:**
   ```python
   # Test rule evaluation
   def _test_rule_conditions(self, record):
       rule = self.env['ops.governance.rule'].search([
           ('model_name', '=', record._name)
       ])
       return rule._evaluate_conditions(record)
   ```

3. **Check User Permissions:**
   - Verify user can create approval requests
   - Confirm approver assignments are valid

#### Stuck Approvals
**Symptoms:**
- Approval requests not progressing

**Solutions:**
1. **Check Approver Availability:**
   ```sql
   -- Verify approvers exist and are active
   SELECT u.login, u.active
   FROM ops_approval_request ar
   JOIN res_users u ON u.id = ar.approver_id
   WHERE ar.id = 'request_id';
   ```

2. **Review Escalation Rules:**
   ```sql
   -- Check for escalation settings
   SELECT escalation_hours, auto_approve
   FROM ops_governance_rule
   WHERE id = 'rule_id';
   ```

3. **Manual Intervention:**
   - Use admin privileges to force approval
   - Document reason for manual override

### SLA Issues

#### SLA Breaches Not Detected
**Symptoms:**
- Overdue tasks not flagged

**Solutions:**
1. **Verify SLA Templates:**
   ```sql
   -- Check active SLA templates
   SELECT name, model_name, time_limit_hours, active
   FROM ops_sla_template
   WHERE active = true;
   ```

2. **Check Cron Jobs:**
   ```sql
   -- Verify SLA monitoring is running
   SELECT cron_name, active
   FROM ir_cron
   WHERE cron_name LIKE '%sla%';
   ```

3. **Manual SLA Check:**
   ```python
   # Force SLA evaluation
   sla_instances = self.env['ops.sla.instance'].search([
       ('state', '=', 'active')
   ])
   sla_instances._check_sla_breaches()
   ```

## Security Issues

### Access Denied Errors

#### Unauthorized Data Access
**Symptoms:**
- Users cannot access expected records

**Solutions:**
1. **Audit User Permissions:**
   ```sql
   -- Check user group memberships
   SELECT g.name
   FROM res_users u
   JOIN res_groups_users_rel gur ON gur.uid = u.id
   JOIN res_groups g ON g.id = gur.gid
   WHERE u.login = 'user@example.com';
   ```

2. **Verify Record Rules:**
   ```sql
   -- Test record rule evaluation
   SELECT *
   FROM ir_rule
   WHERE model_id = 'sale.order'
   AND active = true
   AND groups IN (
       SELECT gid FROM res_groups_users_rel WHERE uid = 'user_id'
   );
   ```

3. **Check Branch/BU Assignments:**
   - Validate user-persona relationships
   - Confirm branch/BU access rights
   - Test with different user roles

### API Security Problems

#### Rate Limiting Issues
**Symptoms:**
- API calls returning 429 Too Many Requests

**Solutions:**
1. **Check Rate Limits:**
   ```sql
   -- Review API key usage
   SELECT usage_count, last_used, rate_limit
   FROM ops_api_key
   WHERE id = 'key_id';
   ```

2. **Adjust Limits:**
   ```python
   # Modify rate limiting settings
   self.env['ir.config_parameter'].set_param(
       'ops_matrix.api_rate_limit_per_hour', '2000'
   )
   ```

3. **Implement Backoff:**
   ```python
   # Client-side rate limit handling
   import time
   import requests

   def api_call_with_retry(url, headers, max_retries=3):
       for attempt in range(max_retries):
           response = requests.get(url, headers=headers)
           if response.status_code == 429:
               retry_after = int(response.headers.get('Retry-After', 60))
               time.sleep(retry_after)
               continue
           return response
       raise Exception("Rate limit exceeded")
   ```

## Data Issues

### Data Synchronization Problems

#### Branch Data Inconsistencies
**Symptoms:**
- Data discrepancies between branches

**Solutions:**
1. **Audit Data Integrity:**
   ```sql
   -- Check for orphaned records
   SELECT COUNT(*) as orphaned_sales
   FROM sale_order
   WHERE ops_branch_id NOT IN (SELECT id FROM ops_branch);
   ```

2. **Rebuild Computed Fields:**
   ```python
   # Recalculate user access rights
   users = self.env['res.users'].search([])
   users._compute_allowed_branches()
   users._compute_allowed_business_units()
   ```

3. **Validate Foreign Keys:**
   ```sql
   -- Check referential integrity
   SELECT conname, conrelid::regclass, confrelid::regclass
   FROM pg_constraint
   WHERE contype = 'f'
   AND conrelid::regclass::text LIKE '%ops%';
   ```

### Missing Data Issues

#### Records Not Appearing
**Symptoms:**
- Expected data not visible in searches

**Solutions:**
1. **Check Domain Filters:**
   ```python
   # Debug domain evaluation
   def debug_domain(self, model, domain):
       records = self.env[model].search(domain)
       _logger.info(f"Domain {domain} returned {len(records)} records")
       return records
   ```

2. **Verify Record Rules:**
   ```sql
   -- Test rule application
   SELECT ir_rule.name, ir_rule.domain_force
   FROM ir_rule
   JOIN ir_model m ON m.id = ir_rule.model_id
   WHERE m.model = 'your.model'
   AND ir_rule.active = true;
   ```

3. **Clear User Cache:**
   ```python
   # Force permission recalculation
   self.env.user.clear_caches()
   ```

## System Monitoring

### Log Analysis

#### Reading Odoo Logs
```bash
# View recent errors
tail -f /var/log/odoo/odoo.log | grep ERROR

# Search for specific issues
grep "ops_matrix" /var/log/odoo/odoo.log | tail -20
```

#### API Debug Logging
```python
# Enable debug logging
import logging
logging.getLogger('ops_matrix').setLevel(logging.DEBUG)

# Log API requests
_logger = logging.getLogger(__name__)
def log_api_request(self, endpoint, request_data):
    _logger.debug(f"API Request to {endpoint}: {request_data}")
```

### Performance Monitoring

#### Database Performance
```sql
-- Check slow queries
SELECT pid, now() - pg_stat_activity.query_start AS duration,
       query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Index usage analysis
SELECT schemaname, tablename, indexname,
       idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

#### System Resources
```bash
# Memory usage
ps aux --sort=-%mem | head -10

# Disk usage
df -h
du -sh /opt/odoo/data/filestore

# Network connections
netstat -tlnp | grep :8069
```

## Emergency Procedures

### System Recovery

#### Database Restore
```bash
# Stop Odoo
sudo systemctl stop odoo

# Drop and recreate database
sudo -u postgres dropdb mz-db
sudo -u postgres createdb -O odoo mz-db

# Restore from backup
sudo -u postgres pg_restore -d mz-db /path/to/backup.dump

# Restart Odoo
sudo systemctl start odoo
```

#### Module Reinstallation
```bash
# Force module reinstall
odoo -d mz-db -u ops_matrix_core,ops_matrix_accounting,ops_matrix_reporting --stop-after-init

# Clear caches
odoo -d mz-db --stop-after-init
```

### Contacting Support

#### Information to Provide
1. **System Information:**
   - Odoo version and OPS Matrix version
   - Operating system and PostgreSQL version
   - Hardware specifications

2. **Error Details:**
   - Exact error messages
   - Steps to reproduce
   - When the issue started

3. **Configuration:**
   - Relevant configuration files (sanitized)
   - Custom modifications
   - Recent changes

4. **Logs:**
   - Odoo log excerpts
   - Database logs
   - System logs

#### Escalation Paths
- **Minor Issues:** Check documentation and FAQs first
- **Major Issues:** Contact system administrator immediately
- **Security Issues:** Follow security incident procedures
- **Data Loss:** Initiate emergency backup recovery

Remember to document all issues and their resolutions to build a knowledge base for future troubleshooting.