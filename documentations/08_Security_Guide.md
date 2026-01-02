# OPS Matrix Framework - Security Guide

This comprehensive security guide covers the security architecture, features, and best practices of the OPS Matrix Framework. It provides administrators and developers with the knowledge needed to maintain a secure multi-branch enterprise environment.

## Security Architecture Overview

### Three-Tier Security Model

The OPS Matrix Framework implements a comprehensive three-tier security model:

#### Tier 1: Authentication
- **Odoo Native Authentication**: Username/password with session management
- **API Key Authentication**: Token-based authentication for external systems
- **Multi-Factor Support**: Compatible with Odoo MFA extensions

#### Tier 2: Authorization
- **Persona-Based Access Control**: Role-based permissions with branch/BU assignments
- **Record-Level Security**: Automatic data filtering based on user context
- **Three-Tier Data Isolation**: Branch-level, BU-level, and administrator access

#### Tier 3: Audit & Compliance
- **Comprehensive Audit Logging**: All security-relevant actions tracked
- **Governance Monitoring**: Automated rule enforcement and violation detection
- **SLA Compliance**: Service level agreement monitoring and reporting

## Authentication Mechanisms

### API Key Authentication

#### Key Generation
API keys are generated with cryptographically secure random values:
```python
import secrets

def generate_api_key():
    return secrets.token_urlsafe(32)  # 256-bit key
```

#### Key Storage
- Keys are hashed using SHA-256 before storage
- Original keys are never stored in plain text
- Keys are displayed only once during creation

#### Key Lifecycle
- **Creation**: Admin-only operation with persona assignment
- **Usage Tracking**: Last used timestamp and usage count
- **Expiration**: Optional time-based expiration
- **Revocation**: Immediate deactivation capability

### Session Security

#### Odoo Session Management
- Secure session tokens with configurable timeout
- Automatic logout on inactivity
- Session fixation protection
- Concurrent session limits

#### API Session Handling
- Stateless authentication via API keys
- No session state stored on server
- Request-scoped authentication
- Rate limiting per API key

## Access Control

### Persona-Based Security

#### Persona Definition
Personas define user roles with specific permissions:
```xml
<!-- Example persona configuration -->
<record id="persona_branch_manager" model="ops.persona">
    <field name="name">Branch Manager</field>
    <field name="is_manager">True</field>
    <field name="allowed_branch_ids" eval="[(6, 0, [ref('branch_main'), ref('branch_north')])]"/>
    <field name="allowed_business_unit_ids" eval="[(6, 0, [ref('bu_sales')])]"/>
</record>
```

#### Dynamic Access Calculation
User access rights are calculated dynamically:
```python
class ResUsers(models.Model):
    @api.depends('ops_persona_ids')
    def _compute_allowed_branches(self):
        for user in self:
            branches = user.ops_persona_ids.mapped('allowed_branch_ids')
            user.ops_allowed_branch_ids = branches
```

### Record-Level Security

#### Three-Tier Access Rules

**Branch-Level Access (Regular Users):**
```python
# Domain filter for regular users
[('ops_branch_id', 'in', user.ops_allowed_branch_ids.ids)]
```

**Business Unit Access (Managers):**
```python
# Additional domain for BU managers
[('ops_business_unit_id', 'in', user.ops_allowed_business_unit_ids.ids)]
```

**Administrator Access:**
```python
# Admin bypass (no domain restrictions)
# Groups: base.group_system
```

#### Secure By Default
- All transactional models protected by record rules
- No data leakage between branches
- Automatic enforcement of access policies
- Admin override for emergency access

## Audit & Monitoring

### Comprehensive Audit Logging

#### API Audit Trail
Every API request is logged with:
```json
{
  "timestamp": "2025-12-28T10:00:00Z",
  "api_key_id": "123",
  "endpoint": "/api/v1/ops_matrix/sales_analysis",
  "method": "POST",
  "ip_address": "192.168.1.100",
  "user_agent": "Python/3.10 requests/2.28.1",
  "request_size": 1024,
  "response_status": 200,
  "response_time_ms": 150,
  "error_message": null
}
```

#### User Action Tracking
- Create, read, update, delete operations logged
- Login/logout events recorded
- Permission changes audited
- Critical business transactions tracked

#### Governance Violations
Automatic detection and logging of:
- Approval rule violations
- Budget limit breaches
- SLA non-compliance
- Security policy infractions

### Monitoring Dashboards

#### Security Dashboard
- Failed authentication attempts
- Unusual access patterns
- Governance violation trends
- API usage analytics

#### Real-Time Alerts
- Immediate notification of security events
- Escalation procedures for critical incidents
- Automated response workflows
- Integration with external monitoring systems

## Threat Mitigation

### SQL Injection Protection

#### ORM Usage
All database queries use Odoo's ORM:
```python
# Safe query construction
records = self.env['sale.order'].search([
    ('ops_branch_id', '=', branch_id),
    ('state', '=', 'sale'),
    ('date_order', '>=', date_from)
])
```

#### Parameterized Queries
No raw SQL execution in application code:
```python
# Avoid this:
self._cr.execute("SELECT * FROM sale_order WHERE name = '%s'" % user_input)

# Use this:
self._cr.execute("SELECT * FROM sale_order WHERE name = %s", (user_input,))
```

### Cross-Site Scripting (XSS) Protection

#### Input Sanitization
- All user inputs validated and sanitized
- HTML content properly escaped
- JavaScript injection prevented
- Content Security Policy (CSP) headers

#### Safe Template Rendering
```xml
<!-- Safe field rendering -->
<t t-esc="record.name"/>  <!-- Escaped output -->
<t t-raw="record.safe_html"/>  <!-- Only for trusted content -->
```

### Cross-Site Request Forgery (CSRF) Protection

#### Token-Based Protection
- CSRF tokens required for state-changing operations
- Automatic token generation and validation
- Protection for both web UI and API endpoints

### Access Control Bypass Prevention

#### Defense in Depth
- Multiple layers of access control
- No single point of failure
- Regular security assessments
- Automated testing of access rules

## Data Protection

### Encryption

#### Data at Rest
- PostgreSQL native encryption capabilities
- File system encryption for attachments
- Secure backup encryption
- Database connection encryption (SSL/TLS)

#### Data in Transit
- HTTPS required for all web access
- TLS 1.3 support for API communications
- Certificate-based authentication
- Perfect forward secrecy

### Backup Security

#### Encrypted Backups
```bash
# Database backup with encryption
pg_dump -Fc mz-db | gpg --encrypt --recipient backup-key > backup.gpg

# File store backup
tar -czf filestore.tar.gz /opt/odoo/data/filestore
gpg --encrypt --recipient backup-key filestore.tar.gz
```

#### Secure Storage
- Off-site backup storage
- Access controls on backup files
- Backup integrity verification
- Regular restore testing

## Source Code Protection

### Vault Build System

#### Compilation to Binary
```bash
# Build vault to protect source code
./scripts/build_vault.sh

# Result: .py files → .so shared objects
# Source code becomes unreadable
```

#### Platform-Specific Binaries
- Linux x86_64 architecture
- Python 3.10+ compatibility
- Odoo 19 CE compatibility
- Platform-specific optimization

#### Protection Benefits
- Intellectual property protection
- Prevention of unauthorized code inspection
- Reduced file size after compilation
- Performance improvements (2-5x typical)

## Operational Security

### Secure Configuration

#### Environment Variables
```bash
# Secure configuration - never in code
ODOO_DB_PASSWORD=secure_password_here
ODOO_ADMIN_PASSWORD=complex_admin_password
API_ENCRYPTION_KEY=256_bit_encryption_key
```

#### File Permissions
```bash
# Secure file permissions
sudo chown -R odoo:odoo /opt/odoo
sudo chmod -R 750 /opt/odoo
sudo chmod 600 /etc/odoo/odoo.conf
```

### Network Security

#### Firewall Configuration
```bash
# UFW firewall rules
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP (redirect to HTTPS)
sudo ufw allow 443/tcp # HTTPS
sudo ufw allow 8089/tcp # Odoo (internal only)
sudo ufw --force enable
```

#### Reverse Proxy Setup
```nginx
# Nginx configuration with security headers
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    location / {
        proxy_pass http://127.0.0.1:8089;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Compliance Considerations

### GDPR Compliance

#### Data Processing
- Lawful basis for data processing documented
- Data minimization principles applied
- User consent mechanisms implemented
- Right to erasure (deletion) supported

#### Data Subject Rights
- Access to personal data
- Data portability features
- Rectification capabilities
- Automated decision-making transparency

### SOX Compliance

#### Financial Controls
- Segregation of duties enforced
- Approval workflows documented
- Audit trails maintained
- Change management procedures

#### Access Controls
- Role-based access to financial data
- Multi-level approval requirements
- Transaction authorization limits
- Exception reporting

### Industry-Specific Compliance

#### PCI DSS (Payment Processing)
- Secure transmission of cardholder data
- Encryption of sensitive information
- Access control measures
- Regular security testing

#### HIPAA (Healthcare)
- Protected health information safeguards
- Access logging and monitoring
- Breach notification procedures
- Business associate agreements

## Incident Response

### Security Incident Classification

#### Severity Levels
- **Critical**: Active breach, data loss, system compromise
- **High**: Attempted breach, unusual activity, policy violation
- **Medium**: Suspicious activity, configuration error
- **Low**: Potential vulnerability, minor policy violation

#### Response Procedures
1. **Detection**: Identify and assess incident
2. **Containment**: Isolate affected systems
3. **Investigation**: Determine root cause and impact
4. **Recovery**: Restore normal operations
5. **Lessons Learned**: Document and improve processes

### Breach Notification

#### Internal Notification
- Security team alerted immediately
- Management notified within 1 hour
- IT operations mobilized
- Legal counsel consulted if required

#### External Notification
- Regulatory authorities notified as required
- Affected customers informed promptly
- Public relations coordinated
- Credit monitoring offered to affected parties

## Security Testing

### Vulnerability Assessment

#### Automated Scanning
```bash
# Regular vulnerability scans
nessus -q -x -T html localhost > security_scan.html

# Dependency vulnerability checking
safety check --full-report
```

#### Penetration Testing
- External penetration testing quarterly
- Internal vulnerability assessments monthly
- Code review security analysis
- Configuration compliance testing

### Security Audits

#### Regular Audits
- Annual comprehensive security audit
- Quarterly vulnerability assessments
- Monthly configuration reviews
- Continuous monitoring and alerting

#### Audit Checklist
- [ ] Access controls verified
- [ ] Encryption implemented
- [ ] Audit logging enabled
- [ ] Backup security confirmed
- [ ] Incident response tested
- [ ] Security training completed

## Best Practices

### Security Awareness Training

#### User Training
- Annual security awareness training
- Phishing simulation exercises
- Password policy education
- Incident reporting procedures

#### Administrator Training
- System hardening procedures
- Security monitoring techniques
- Incident response training
- Compliance requirements

### Continuous Improvement

#### Security Metrics
- Track security incidents over time
- Monitor compliance status
- Measure response times
- Audit finding trends

#### Regular Updates
- Security patch management
- Framework updates applied promptly
- Third-party component updates
- Configuration reviews

## Support and Resources

### Security Resources
- [OWASP Guidelines](https://owasp.org/) - Web application security
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) - Security standards
- [Odoo Security Documentation](https://www.odoo.com/security) - Platform security
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html) - Database security

### Getting Help
- Immediate security incidents: Contact security team
- Technical questions: Review administrator guide
- Compliance issues: Consult legal counsel
- General inquiries: Check FAQ and troubleshooting

### Emergency Contacts
- **Security Incidents**: security@company.com (24/7)
- **System Administration**: admin@company.com
- **Legal/Compliance**: legal@company.com
- **Executive Management**: ceo@company.com

Remember, security is an ongoing process. Regular assessment, monitoring, and improvement are essential to maintaining the security posture of your OPS Matrix Framework implementation.