# OPS Matrix Framework - Quick Start Guide

This guide provides a step-by-step walkthrough to get you started with the OPS Matrix Framework quickly. We'll cover the essential setup and basic operations to have your multi-branch system running in minutes.

## Prerequisites

- OPS Matrix Framework installed and running
- Administrator access to Odoo
- Basic understanding of your organizational structure

## Step 1: Initial Login and Setup

### Access the System
1. Open your web browser and navigate to your Odoo instance (e.g., `http://localhost:8089`)
2. Log in with the administrator credentials (default: admin/admin)

### Update Apps List
1. Go to **Apps** menu
2. Click **Update Apps List** to ensure all modules are available
3. Verify OPS Matrix modules are installed and up-to-date

## Step 2: Configure Company Structure

### Set Up Your Main Company
1. Navigate to **Settings → Companies**
2. Click **Create** if no company exists
3. Fill in basic company information:
   - Company Name
   - Address details
   - Tax information
   - Currency settings

### Create Branches
1. Navigate to **Settings → Companies**
2. Open your main company record
3. Go to the **Operational Branches** tab
4. Click **Add a line** to add your first branch
5. Enter branch details:

   - **Name**: Branch display name
   - **Code**: Unique branch identifier
   - **Company**: Link to parent company
   - **Branch Manager**: Assign responsible user
   - **Address**: Branch location details

6. Repeat for additional branches

Additional branch management options are available at **OPS Matrix → Branches**.

### Create Business Units
1. Navigate to **OPS Matrix → Business Units**
2. Click **Create** for each business unit
3. Configure:
   - **Name**: BU display name
   - **Code**: Unique identifier
   - **Company**: Parent company
   - **BU Leader**: Responsible executive
   - **Description**: BU purpose and scope

## Step 3: Set Up User Roles and Security

### Create Personas
1. Go to **OPS Matrix → Personas**
2. Click **Create** to define user roles
3. Configure persona details:
   - **Name**: Role name (e.g., "Branch Manager", "Sales Rep")
   - **Allowed Branches**: Select accessible branches
   - **Allowed Business Units**: Select accessible BUs
   - **Is Manager**: Enable for management roles
   - **Description**: Role responsibilities

### Create Users and Assign Personas
1. Navigate to **Settings → Users & Companies → Users**
2. Click **Create** for each user
3. Basic user setup:
   - **Name**: Full user name
   - **Login**: Username/email
   - **Email**: Contact email
   - **Password**: Temporary password
4. Assign personas:
   - Go to **OPS Matrix** tab
   - Add persona assignments
   - Specify active date ranges if needed

## Step 4: Configure Basic Governance

### Set Up Simple Approval Rules
1. Navigate to **OPS Matrix → Governance → Rules**
2. Click **Create** for basic approval workflows
3. Example Sales Order Approval:
   - **Name**: "Sales Order Approval"
   - **Model**: sale.order
   - **Conditions**: amount_total > 5000
   - **Approvers**: Branch Manager
   - **Auto-approve below threshold**: Enable

### Configure SLA Templates
1. Go to **OPS Matrix → Governance → SLA Templates**
2. Click **Create** for response time commitments
3. Basic SLA Example:
   - **Name**: "Sales Order Processing"
   - **Model**: sale.order
   - **Stages**: draft → confirmed
   - **Time Limit**: 24 hours
   - **Warning Threshold**: 80%

## Step 5: Test Basic Operations

### Create a Test Sales Order
1. Switch to a user with Sales persona
2. Navigate to **Sales → Orders → Orders**
3. Click **Create**
4. Fill in order details:
   - **Customer**: Select or create customer
   - **Order Lines**: Add products and quantities
   - **Branch**: Should auto-populate based on user
   - **Business Unit**: Select appropriate BU

5. **Save** the order
6. If approval required, submit for approval
7. Verify approval workflow triggers

### Test Branch Isolation
1. Log in as different users from different branches
2. Verify they can only see their branch's data
3. Confirm cross-branch data is properly isolated

### Test Dashboard Access
1. Navigate to **OPS Matrix → Dashboards**
2. Verify appropriate dashboards load
3. Check data accuracy and real-time updates

## Step 6: API Integration (Optional)

### Generate API Key
1. Go to **OPS Matrix → API Keys**
2. Click **Create**
3. Select a persona for the API key
4. **Save** (key will be displayed once - copy it securely)

### Test API Access
```bash
# Test health endpoint
curl -X POST http://localhost:8089/api/v1/ops_matrix/health

# Test authenticated endpoint
curl -X POST http://localhost:8089/api/v1/ops_matrix/me \
  -H "X-API-Key: your_api_key_here"
```

## Step 7: Basic Reporting

### Run Sales Analysis
1. Navigate to **OPS Matrix → Reporting → Sales Analysis**
2. Apply filters:
   - Date range
   - Branch selection
   - Product categories
3. View charts and export to Excel

### Check Financial Reports
1. Go to **Accounting → Accounting → General Ledger**
2. Select branch-specific journals
3. Run reports by branch or consolidated view

## Common Quick Start Issues

### Users Can't See Data
**Issue**: New users cannot access expected records
**Solution**:
- Verify persona assignments
- Check branch/BU access rights
- Ensure user is not locked

### Approval Workflows Not Triggering
**Issue**: Transactions not going through approval process
**Solution**:
- Check governance rule conditions
- Verify rule is active
- Test with values that meet thresholds

### Dashboard Not Loading
**Issue**: Dashboard pages showing errors
**Solution**:
- Clear browser cache
- Check user permissions
- Verify module dependencies

### API Authentication Failing
**Issue**: API calls returning authentication errors
**Solution**:
- Verify X-API-Key header format
- Check API key is active and not expired
- Confirm persona has appropriate access

## Next Steps

### Immediate Actions
1. **Create all branches** in your organization
2. **Define personas** for all user roles
3. **Set up users** and assign appropriate access
4. **Configure critical governance rules**
5. **Test key business processes**

### Advanced Configuration
1. Review the [User Guide](04_User_Guide.md) for detailed feature usage
2. Configure advanced approval workflows
3. Set up automated SLA monitoring
4. Implement budget controls
5. Configure advanced reporting

### Training and Adoption
1. Train branch managers on dashboard usage
2. Educate users on approval workflows
3. Demonstrate reporting capabilities
4. Establish governance procedures

## Support Resources

- [User Guide](04_User_Guide.md) - Detailed feature documentation
- [Administrator Guide](05_Administrator_Guide.md) - System management
- [API Reference](06_API_Reference.md) - Integration details
- [Troubleshooting](09_Troubleshooting.md) - Common issues and solutions
- [FAQ](10_FAQ.md) - Frequently asked questions

## Getting Help

If you encounter issues during quick start:
1. Check the [Troubleshooting](09_Troubleshooting.md) guide
2. Review error logs in Odoo
3. Verify user permissions and configurations
4. Contact your system administrator

The OPS Matrix Framework is now ready for your organization's multi-branch operations!