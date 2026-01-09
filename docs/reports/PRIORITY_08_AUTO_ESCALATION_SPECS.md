# Priority #8: Auto-Escalation - Technical Specifications

**Priority**: #8 - HIGH  
**Estimated Effort**: 1-2 sessions (2-4 hours)  
**Status**: READY FOR DEVELOPMENT  
**Phase-Based Implementation**: Yes (1 phase, incremental)

---

## Overview

Implement automatic escalation of approval requests that remain unapproved beyond configured time limits. Escalate to higher-level approvers and notify all stakeholders to prevent approval bottlenecks.

---

## Business Context

### Problem Statement

Without auto-escalation:
- ❌ Approval requests sit idle when approver is unavailable
- ❌ No systematic follow-up on overdue approvals  
- ❌ Business operations blocked waiting for approval
- ❌ No visibility into approval delays
- ❌ Manual escalation required (slow, inconsistent)

### Solution

**Auto-Escalation System**:
1. **Timeout Configuration**: Set hours per governance rule
2. **Multi-Level Escalation**: L1 → L2 → L3 (CFO/CEO)
3. **Automatic Notifications**: Email + system notifications
4. **Audit Trail**: Log all escalations with timestamps
5. **Dashboard Visibility**: Show overdue approvals

### User Stories

**As a** Sales Representative  
**I want** my approval requests to escalate automatically  
**So that** I don't lose sales due to approval delays

**As a** Purchase Manager  
**I want** to know when my approvals are overdue  
**So that** I can prioritize critical requests

**As a** CFO  
**I want** to see escalated approvals in my dashboard  
**So that** I can intervene on blocked business processes

---

## Core Concepts

### Escalation Flow

```
Approval Request Created
    │
    ↓ After 24 hours (configurable)
    │
Level 1 Escalation
    │ • Email to original approver (reminder)
    │ • Email to escalation approver
    │ • System notification
    │ • Chatter post
    │
    ↓ After another 24 hours
    │
Level 2 Escalation
    │ • Email to L1 escalation approver (reminder)
    │ • Email to L2 escalation approver
    │ • System notification
    │ • Chatter post
    │
    ↓ After another 24 hours
    │
Level 3 Escalation (Final)
    │ • Email to all previous approvers
    │ • Email to CFO/CEO
    │ • High-priority notification
    │ • Chatter post
    │
    ↓
Manual Intervention Required
```

### Escalation Levels

**Level 0 - Original Approver**:
- Initial assignment based on governance rule
- First to receive request
- Gets reminder on L1 escalation

**Level 1 - Department Manager**:
- Typically the original approver's manager
- Receives request after L1 timeout
- Can approve or reassign

**Level 2 - Division Leader**:
- BU Leader or VP-level
- Receives request after L2 timeout
- High authority, can override

**Level 3 - Executive**:
- CFO or CEO
- Final escalation point
- Indicates critical bottleneck

---

## PHASE 1: Auto-Escalation Implementation (Single Session)

### Objectives

1. Add escalation configuration to governance rules
2. Create escalation tracking on approval requests
3. Implement scheduled job to check timeouts
4. Send notifications (email + system)
5. Post to chatter
6. Add dashboard widgets for overdue approvals
7. Testing

### Files to Modify

#### 1. `models/ops_governance_rule.py`

**Add Escalation Fields**:
```python
class OpsGovernanceRule(models.Model):
    _inherit = 'ops.governance.rule'
    
    # Escalation Configuration
    enable_escalation = fields.Boolean(
        'Enable Auto-Escalation',
        default=True,
        help='Automatically escalate if approval takes too long'
    )
    
    escalation_timeout_hours = fields.Float(
        'Escalation Timeout (Hours)',
        default=24.0,
        help='Escalate if not approved within this many hours'
    )
    
    escalation_level_1_persona_id = fields.Many2one(
        'ops.persona',
        'Level 1 Escalation Persona',
        help='Escalate to this persona after timeout'
    )
    
    escalation_level_2_persona_id = fields.Many2one(
        'ops.persona',
        'Level 2 Escalation Persona',
        help='Second escalation level if still not approved'
    )
    
    escalation_level_3_persona_id = fields.Many2one(
        'ops.persona',
        'Level 3 Escalation Persona (Final)',
        help='Final escalation to executive (CFO/CEO)'
    )
```

#### 2. `models/ops_approval_request.py`

**Add Escalation Tracking**:
```python
class OpsApprovalRequest(models.Model):
    _inherit = 'ops.approval.request'
    
    # Escalation Tracking
    escalation_level = fields.Integer(
        'Current Escalation Level',
        default=0,
        help='0=Original, 1=L1 Escalated, 2=L2 Escalated, 3=L3 Escalated'
    )
    
    escalation_date = fields.Datetime(
        'Last Escalation Date',
        help='When the request was last escalated'
    )
    
    escalation_history = fields.Text(
        'Escalation History',
        help='Log of all escalations with timestamps'
    )
    
    is_overdue = fields.Boolean(
        'Overdue',
        compute='_compute_is_overdue',
        store=True,
        help='Request is past escalation timeout'
    )
    
    hours_pending = fields.Float(
        'Hours Pending',
        compute='_compute_hours_pending',
        help='Hours since request creation or last escalation'
    )
    
    next_escalation_date = fields.Datetime(
        'Next Escalation Date',
        compute='_compute_next_escalation_date',
        help='When the next escalation will occur'
    )
    
    @api.depends('request_date', 'escalation_date', 'state')
    def _compute_hours_pending(self):
        """Calculate hours pending approval."""
        for request in self:
            if request.state != 'pending':
                request.hours_pending = 0.0
                continue
            
            start_time = request.escalation_date or request.request_date
            if start_time:
                delta = fields.Datetime.now() - start_time
                request.hours_pending = delta.total_seconds() / 3600.0
            else:
                request.hours_pending = 0.0
    
    @api.depends('hours_pending', 'governance_rule_id.escalation_timeout_hours')
    def _compute_is_overdue(self):
        """Check if request is overdue for escalation."""
        for request in self:
            if request.state != 'pending' or not request.governance_rule_id.enable_escalation:
                request.is_overdue = False
                continue
            
            timeout = request.governance_rule_id.escalation_timeout_hours or 24.0
            request.is_overdue = request.hours_pending >= timeout
    
    @api.depends('escalation_date', 'governance_rule_id.escalation_timeout_hours')
    def _compute_next_escalation_date(self):
        """Calculate when next escalation will occur."""
        for request in self:
            if request.state != 'pending' or not request.governance_rule_id.enable_escalation:
                request.next_escalation_date = False
                continue
            
            start_time = request.escalation_date or request.request_date
            timeout_hours = request.governance_rule_id.escalation_timeout_hours or 24.0
            
            if start_time:
                request.next_escalation_date = start_time + timedelta(hours=timeout_hours)
            else:
                request.next_escalation_date = False
    
    def action_escalate(self):
        """Escalate approval request to next level."""
        self.ensure_one()
        
        if self.state != 'pending':
            return  # Already approved/rejected
        
        rule = self.governance_rule_id
        if not rule.enable_escalation:
            return  # Escalation disabled
        
        # Determine next escalation level
        current_level = self.escalation_level
        next_level = current_level + 1
        
        if next_level > 3:
            _logger.warning(f'Approval request {self.id} already at max escalation level (3)')
            return
        
        # Get next escalation approver
        escalation_persona_field = f'escalation_level_{next_level}_persona_id'
        escalation_persona = getattr(rule, escalation_persona_field, None)
        
        if not escalation_persona:
            _logger.warning(f'No escalation persona configured for level {next_level} on rule {rule.name}')
            return
        
        # Find user with escalation persona
        escalation_user = self.env['res.users'].search([
            ('ops_persona_ids', 'in', escalation_persona.id),
            ('ops_branch_ids', 'in', self.ops_branch_id.ids)
        ], limit=1)
        
        if not escalation_user:
            _logger.warning(f'No user found with persona {escalation_persona.name} in branch {self.ops_branch_id.name}')
            return
        
        # Update request
        original_approver = self.approver_id
        escalation_log = (self.escalation_history or '') + f"\n[{fields.Datetime.now()}] Escalated from L{current_level} ({original_approver.name}) to L{next_level} ({escalation_user.name})"
        
        self.write({
            'approver_id': escalation_user.id,
            'escalation_level': next_level,
            'escalation_date': fields.Datetime.now(),
            'escalation_history': escalation_log,
        })
        
        # Send notifications
        self._send_escalation_notifications(original_approver, escalation_user, next_level)
        
        # Post to chatter
        self.message_post(
            body=_('<p><strong>⚠️ Escalated to Level %s</strong></p>'
                   '<p>Original approver: %s</p>'
                   '<p>New approver: %s</p>'
                   '<p>Reason: Timeout (%s hours)</p>') % (
                next_level,
                original_approver.name,
                escalation_user.name,
                rule.escalation_timeout_hours
            ),
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        _logger.info(f'Escalated approval request {self.id} to level {next_level}, approver: {escalation_user.name}')
    
    def _send_escalation_notifications(self, original_approver, new_approver, escalation_level):
        """Send email and system notifications for escalation."""
        # Email to original approver (reminder)
        self._send_escalation_email(
            recipient=original_approver,
            subject=f'Reminder: Approval Request Overdue - {self.document_ref}',
            body_template='ops_matrix_core.email_template_escalation_reminder'
        )
        
        # Email to new approver
        self._send_escalation_email(
            recipient=new_approver,
            subject=f'Escalated Approval Request - {self.document_ref}',
            body_template='ops_matrix_core.email_template_escalation_new_approver'
        )
        
        # System notification to both
        self._create_notification(
            users=original_approver | new_approver,
            message=f'Approval request {self.document_ref} escalated to Level {escalation_level}',
            priority='high' if escalation_level >= 3 else 'normal'
        )
    
    def _send_escalation_email(self, recipient, subject, body_template):
        """Send escalation email."""
        template = self.env.ref(body_template, False)
        if template:
            template.send_mail(
                self.id,
                email_values={'email_to': recipient.email, 'subject': subject},
                force_send=True
            )
    
    def _create_notification(self, users, message, priority='normal'):
        """Create system notification."""
        # Odoo 19 notification system
        self.env['bus.bus']._sendone(
            users.partner_id,
            'simple_notification',
            {
                'title': 'Approval Escalation',
                'message': message,
                'sticky': priority == 'high',
                'type': 'warning' if priority == 'high' else 'info',
            }
        )
```

#### 3. Create Scheduled Action

**File**: `data/ir_cron_escalation.xml`

```xml
<odoo>
    <data noupdate="1">
        <!-- Scheduled Action: Check for Overdue Approvals -->
        <record id="ir_cron_escalate_approvals" model="ir.cron">
            <field name="name">OPS: Escalate Overdue Approvals</field>
            <field name="model_id" ref="model_ops_approval_request"/>
            <field name="state">code</field>
            <field name="code">model._cron_escalate_overdue_approvals()</field>
            <field name="interval_number">1</field>
            <field name="interval_type">hours</field>
            <field name="numbercall">-1</field>
            <field name="active" eval="True"/>
            <field name="priority">5</field>
        </record>
    </data>
</odoo>
```

**Add Cron Method to `ops_approval_request.py`**:
```python
@api.model
def _cron_escalate_overdue_approvals(self):
    """Scheduled job to escalate overdue approval requests."""
    # Find overdue pending approvals
    overdue_requests = self.search([
        ('state', '=', 'pending'),
        ('is_overdue', '=', True'),
    ])
    
    _logger.info(f'Found {len(overdue_requests)} overdue approval requests to escalate')
    
    for request in overdue_requests:
        try:
            request.action_escalate()
        except Exception as e:
            _logger.error(f'Failed to escalate approval request {request.id}: {e}')
    
    return True
```

### Views to Create/Modify

#### 1. Governance Rule Form - Add Escalation Configuration

**File**: `views/ops_governance_rule_views.xml`

```xml
<xpath expr="//page[@name='approval']" position="inside">
    <group string="Auto-Escalation">
        <field name="enable_escalation"/>
        <field name="escalation_timeout_hours" 
               attrs="{'invisible': [('enable_escalation', '=', False)]}"/>
        <field name="escalation_level_1_persona_id"
               attrs="{'invisible': [('enable_escalation', '=', False)]}"/>
        <field name="escalation_level_2_persona_id"
               attrs="{'invisible': [('enable_escalation', '=', False)]}"/>
        <field name="escalation_level_3_persona_id"
               attrs="{'invisible': [('enable_escalation', '=', False)]}"/>
    </group>
</xpath>
```

#### 2. Approval Request Form - Show Escalation Info

**File**: `views/ops_approval_request_views.xml`

```xml
<!-- Add escalation indicator -->
<xpath expr="//field[@name='state']" position="after">
    <field name="escalation_level" 
           widget="badge"
           decoration-warning="escalation_level == 1"
           decoration-danger="escalation_level >= 2"
           attrs="{'invisible': [('escalation_level', '=', 0)]}"/>
    <field name="is_overdue" widget="boolean" attrs="{'invisible': [('state', '!=', 'pending')]}"/>
</xpath>

<!-- Add escalation banner -->
<xpath expr="//sheet" position="before">
    <div class="alert alert-warning" role="alert"
         attrs="{'invisible': ['|', ('escalation_level', '=', 0), ('state', '!=', 'pending')]}">
        <strong>⚠️ Escalated to Level <field name="escalation_level" readonly="1" nolabel="1"/></strong>
        <p>This approval has been escalated due to timeout.</p>
        <field name="escalation_history" readonly="1" nolabel="1" widget="text"/>
    </div>
    
    <div class="alert alert-danger" role="alert"
         attrs="{'invisible': ['|', ('is_overdue', '=', False), ('state', '!=', 'pending')]}">
        <strong>🔔 Overdue for <field name="hours_pending" readonly="1" nolabel="1"/> hours</strong>
        <p>Next escalation: <field name="next_escalation_date" readonly="1" nolabel="1"/></p>
    </div>
</xpath>

<!-- Add escalation tab -->
<xpath expr="//notebook" position="inside">
    <page name="escalation" string="Escalation" attrs="{'invisible': [('escalation_level', '=', 0)]}">
        <group>
            <field name="escalation_date" readonly="1"/>
            <field name="hours_pending" readonly="1"/>
            <field name="next_escalation_date" readonly="1"/>
            <field name="escalation_history" readonly="1" nolabel="1" widget="text"/>
        </group>
    </page>
</xpath>
```

#### 3. Approval Dashboard Widget - Overdue Requests

**File**: `views/ops_approval_dashboard_views.xml`

```xml
<!-- Add to existing approval dashboard -->
<xpath expr="//kanban" position="inside">
    <field name="is_overdue"/>
    <field name="escalation_level"/>
    <field name="hours_pending"/>
</xpath>

<xpath expr="//templates/t[@t-name='kanban-box']" position="inside">
    <div t-if="record.is_overdue.raw_value" class="ribbon ribbon-top-right">
        <span class="bg-danger">Overdue</span>
    </div>
    <div t-if="record.escalation_level.raw_value > 0" class="mt-2">
        <span class="badge badge-warning">L<t t-esc="record.escalation_level.raw_value"/> Escalated</span>
        <span class="text-muted ml-2"><t t-esc="record.hours_pending.value"/> hrs pending</span>
    </div>
</xpath>

<!-- Add filter for overdue -->
<xpath expr="//search" position="inside">
    <filter name="overdue" string="Overdue" domain="[('is_overdue', '=', True)]"/>
    <filter name="escalated" string="Escalated" domain="[('escalation_level', '>', 0)]"/>
    <separator/>
    <filter name="level_1" string="Level 1" domain="[('escalation_level', '=', 1)]"/>
    <filter name="level_2" string="Level 2" domain="[('escalation_level', '=', 2)]"/>
    <filter name="level_3" string="Level 3" domain="[('escalation_level', '=', 3)]"/>
</xpath>
```

### Email Templates

#### 1. Escalation Reminder (Original Approver)

**File**: `data/email_templates.xml`

```xml
<record id="email_template_escalation_reminder" model="mail.template">
    <field name="name">OPS: Escalation Reminder</field>
    <field name="model_id" ref="model_ops_approval_request"/>
    <field name="subject">Reminder: Approval Request Overdue - ${object.document_ref}</field>
    <field name="email_from">${object.company_id.email or ''}</field>
    <field name="body_html" type="html">
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #f0ad4e;">⚠️ Approval Request Overdue</h2>
            
            <p>Hello ${object.approver_id.name},</p>
            
            <p>The following approval request has been <strong>escalated</strong> due to timeout:</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Document:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${object.document_ref}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Requested By:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${object.requester_id.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Request Date:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${object.request_date}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Hours Pending:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${object.hours_pending:.1f} hours</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Escalation Level:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">Level ${object.escalation_level}</td>
                </tr>
            </table>
            
            <p>This request has been escalated to <strong>${object.approver_id.name}</strong>.</p>
            
            <p style="margin: 30px 0;">
                <a href="${object.get_base_url()}/web#id=${object.id}&model=ops.approval.request&view_type=form"
                   style="background-color: #f0ad4e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                    View Approval Request
                </a>
            </p>
            
            <p style="color: #666; font-size: 12px; margin-top: 40px;">
                This is an automated notification from the OPS Framework.
            </p>
        </div>
    </field>
</record>
```

#### 2. New Approver Notification

```xml
<record id="email_template_escalation_new_approver" model="mail.template">
    <field name="name">OPS: Escalation - New Approver</field>
    <field name="model_id" ref="model_ops_approval_request"/>
    <field name="subject">Escalated Approval Request - ${object.document_ref}</field>
    <field name="email_from">${object.company_id.email or ''}</field>
    <field name="body_html" type="html">
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #d9534f;">🔔 Escalated Approval Request</h2>
            
            <p>Hello ${object.approver_id.name},</p>
            
            <p>An approval request has been <strong>escalated to you</strong>:</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Document:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${object.document_ref}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Requested By:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${object.requester_id.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Request Date:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${object.request_date}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Hours Pending:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${object.hours_pending:.1f} hours</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Escalation Level:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">Level ${object.escalation_level}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>Reason:</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">${object.reason or 'N/A'}</td>
                </tr>
            </table>
            
            <p style="background-color: #fff3cd; border-left: 4px solid #f0ad4e; padding: 12px; margin: 20px 0;">
                <strong>Action Required:</strong> Please review and approve/reject this request as soon as possible.
            </p>
            
            <p style="margin: 30px 0;">
                <a href="${object.get_base_url()}/web#id=${object.id}&model=ops.approval.request&view_type=form"
                   style="background-color: #5cb85c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin-right: 10px;">
                    Approve
                </a>
                <a href="${object.get_base_url()}/web#id=${object.id}&model=ops.approval.request&view_type=form"
                   style="background-color: #d9534f; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                    Reject
                </a>
            </p>
            
            <p style="color: #666; font-size: 12px; margin-top: 40px;">
                This is an automated notification from the OPS Framework.
            </p>
        </div>
    </field>
</record>
```

### Testing Checklist

**Escalation Configuration**:
- [ ] Enable escalation on governance rule
- [ ] Set timeout hours (e.g., 24)
- [ ] Assign L1, L2, L3 personas
- [ ] Save and verify

**Escalation Triggering**:
- [ ] Create approval request
- [ ] Wait for timeout (or manually trigger cron)
- [ ] Verify escalation to L1
- [ ] Verify approver changed
- [ ] Check chatter post

**Notifications**:
- [ ] Original approver receives reminder email
- [ ] New approver receives notification email
- [ ] System notifications appear
- [ ] Email content correct

**Multiple Levels**:
- [ ] L1 escalation after first timeout
- [ ] L2 escalation after second timeout
- [ ] L3 escalation after third timeout
- [ ] No further escalation after L3

**Dashboard**:
- [ ] Overdue filter shows overdue requests
- [ ] Escalated filter shows escalated requests
- [ ] Level filters work correctly
- [ ] Badge displays on kanban cards

**Approval After Escalation**:
- [ ] Escalated approver can approve
- [ ] Escalated approver can reject
- [ ] Escalation history preserved
- [ ] Original requester notified

---

## Integration Points

### With Existing Systems

1. **Governance Rules**
   - Configure escalation per rule
   - Different timeouts per rule type

2. **Approval Requests**
   - Track escalation level
   - Update approver on escalation

3. **Email System**
   - Send escalation notifications
   - Template-based emails

4. **Chatter**
   - Log all escalations
   - Audit trail

5. **Dashboard**
   - Show overdue approvals
   - Filter by escalation level

---

## Success Metrics

**Feature Success If**:
- ✅ 90%+ of approvals completed before escalation
- ✅ Escalated approvals resolved faster (50%+ improvement)
- ✅ Approval bottlenecks visible in dashboard
- ✅ Average approval time reduced by 30%+
- ✅ User satisfaction with approval speed improved

---

## Future Enhancements (Out of Scope)

1. **Smart Escalation**
   - Escalate based on urgency, not just time
   - Business hours vs calendar hours

2. **Escalation Patterns**
   - Learn from history
   - Auto-assign to fastest approvers

3. **Escalation Analytics**
   - Which approvers cause bottlenecks
   - Which rules escalate most

4. **Mobile Push Notifications**
   - Real-time alerts on mobile
   - One-tap approve/reject

---

## READY FOR DEVELOPMENT

**Phases**: Single phase implementation  
**Effort**: 2-4 hours (1-2 sessions)  
**Impact**: Eliminates approval bottlenecks  

**All requirements defined. Ready for RooCode!** 🚀
