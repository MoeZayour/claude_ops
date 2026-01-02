# OPS Matrix Framework - User Guide

This comprehensive guide covers all features and functionality available to users of the OPS Matrix Framework. Whether you're a branch manager, sales representative, or business unit leader, this guide will help you effectively use the system for your daily operations.

## Navigation and Interface

### Main Menu Structure

The OPS Matrix Framework adds several new menus to your Odoo interface:

- **OPS Matrix**: Core framework features
  - Branches: Branch management and configuration
  - Business Units: BU management and oversight
  - Personas: Role definitions and assignments
  - Dashboards: Real-time analytics and KPIs
  - Governance: Rules, approvals, and SLAs
  - API Keys: API access management

### Dashboard Overview

Access real-time dashboards from **OPS Matrix → Dashboards**:

- **Executive Dashboard**: Company-wide performance metrics
- **Branch Dashboard**: Branch-specific KPIs and operations
- **Business Unit Dashboard**: BU-level consolidation and analysis
- **Sales Dashboard**: Sales pipeline and performance tracking
- **Approval Dashboard**: Pending approvals and workflow status

## Branch and Business Unit Management

### Working with Branches

#### Viewing Branch Information
1. Navigate to **OPS Matrix → Branches**
2. View your assigned branches (filtered by permissions)
3. Access branch details:
   - Contact information and address
   - Branch manager and key personnel
   - Operating hours and location details
   - Associated business units

#### Branch-Specific Operations
- Sales orders automatically tagged with your branch
- Inventory levels show branch-specific stock
- Financial reports filtered by branch
- Approval workflows respect branch hierarchy

### Business Unit Operations

#### BU-Level Access
If you have BU-level permissions (managers):
- View data across multiple branches within your BU
- Access consolidated financial reports
- Manage cross-branch approvals and workflows
- Monitor BU-wide performance metrics

#### BU Dashboard Features
- Revenue and profit consolidation across branches
- Cross-branch sales performance comparison
- Budget utilization tracking
- Resource allocation and productivity metrics

## Sales and Order Management

### Creating Sales Orders

1. Navigate to **Sales → Orders → Orders**
2. Click **Create**
3. Fill in customer and order details:
   - **Customer**: Select existing or create new customer
   - **Order Lines**: Add products, quantities, and pricing
   - **Branch**: Automatically populated based on your assignment
   - **Business Unit**: Select appropriate BU
   - **Delivery Date**: Requested delivery timeline
   - **Payment Terms**: Customer payment conditions

4. **Save** the order
5. If approval required, click **Submit for Approval**

### Order Approval Workflow

#### For Regular Users
1. Create and save sales order
2. System automatically checks governance rules
3. If approval needed, order status shows "Waiting for Approval"
4. Notification sent to approvers
5. Monitor approval status in **OPS Matrix → Approvals**

#### For Approvers
1. Navigate to **OPS Matrix → Approvals**
2. Review pending orders requiring your approval
3. Click **Approve** or **Reject** with comments
4. Orders automatically advance through workflow

### Order Processing
- **Confirmed**: Order approved and ready for fulfillment
- **Delivery**: Partial or full delivery status
- **Invoiced**: Order fully processed and billed
- **Done**: Order completed successfully

## Purchase and Procurement

### Creating Purchase Orders

1. Navigate to **Purchase → Orders → Orders**
2. Click **Create**
3. Configure purchase details:
   - **Vendor**: Select approved supplier
   - **Branch**: Your assigned branch
   - **Business Unit**: Appropriate BU
   - **Order Lines**: Required items and quantities
   - **Delivery Date**: Expected delivery
   - **Incoterms**: Shipping and delivery terms

4. **Save** and submit for approval if required

### Purchase Approval Process
Similar to sales orders, purchases may require:
- Budget approval for large amounts
- Manager approval for specific vendors
- Multi-level approvals for high-value purchases

## Inventory and Stock Management

### Branch-Specific Inventory

#### Viewing Stock Levels
1. Navigate to **Inventory → Products → Products**
2. View products available in your branch
3. Check quantities across locations
4. Monitor stock movements and transfers

#### Inventory Transactions
- **Stock Moves**: Automatic tracking of inventory changes
- **Branch Isolation**: Users see only their branch's inventory
- **Inter-Branch Transfers**: Controlled movement between branches

### Inter-Branch Transfers

#### Requesting Stock Transfers
1. Navigate to **OPS Matrix → Inter-Branch Transfers**
2. Click **Create Transfer Request**
3. Specify:
   - **Source Branch**: Where stock is located
   - **Destination Branch**: Where stock is needed
   - **Products and Quantities**: Items to transfer
   - **Reason**: Business justification

4. Submit for approval

#### Processing Transfers
- Transfers require approval based on governance rules
- Automatic stock move generation
- Tracking through delivery orders
- Cost allocation between branches

## Asset Management

### Managing Assets

#### Asset Lifecycle
Assets follow a structured lifecycle:
- **Draft**: New asset creation and configuration
- **Running**: Active asset in use with depreciation tracking
- **Closed/Sold**: Asset disposal or sale

#### Creating Assets
1. Navigate to **Accounting → Assets → Assets**
2. Click **Create**
3. Configure asset details:
   - **Name**: Asset identifier
   - **Category**: Hierarchical asset classification
   - **Purchase Value**: Acquisition cost
   - **Branch**: Branch assignment
   - **Business Unit**: BU assignment
   - **Depreciation Method**: Straight-line or declining balance

4. **Save** and transition to Running state

#### Manual Depreciation
1. Access asset record
2. Navigate to **Depreciation** tab
3. Click **Add Depreciation Line**
4. Enter manual depreciation amounts
5. System calculates accumulated depreciation automatically

## Financial Management

### Branch-Level Accounting

#### Viewing Financial Data
1. Navigate to **Accounting → Accounting → Journal Entries**
2. Filter by your branch
3. View transactions and account balances
4. Access branch-specific financial reports

#### Key Financial Features
- **Branch-specific journals**: Segregated transaction recording
- **Automatic posting**: System-generated entries for operations
- **Budget tracking**: Monitor spending against allocated budgets
- **Cost centers**: Track expenses by department or project

### Post-Dated Checks (PDC)

#### Managing PDCs
1. Navigate to **Accounting → PDC Management**
2. View received checks: **Received** → **Deposited** → **Cleared**
3. Track check status and collection dates
4. Generate PDC reports by branch

#### PDC Workflow
- **Received**: Check received from customer
- **Deposited**: Check submitted to bank
- **Cleared**: Funds successfully collected
- **Bounced**: Check returned unpaid

## Reporting and Analytics

### Sales Analytics

#### Accessing Sales Reports
1. Navigate to **OPS Matrix → Reporting → Sales Analysis**
2. Apply filters:
   - **Date Range**: Specific time periods
   - **Branch**: Your branch or BU branches
   - **Product Categories**: Focus on specific products
   - **Customer Segments**: Target customer groups

3. View metrics:
   - Revenue trends and growth
   - Product performance ranking
   - Customer profitability analysis
   - Sales representative performance

#### Export Capabilities
- **Excel Export**: One-click export to Excel
- **Custom Columns**: Select specific data fields
- **Filtered Exports**: Export only filtered results
- **Scheduled Reports**: Automated report generation

### Financial Analysis

#### Consolidated Financial Reports
1. Navigate to **Accounting → Accounting → General Ledger**
2. Generate reports:
   - **Profit & Loss**: By branch or consolidated
   - **Balance Sheet**: Branch-level or company-wide
   - **Cash Flow**: Operating, investing, financing activities
   - **Budget vs Actual**: Performance against budgets

#### Advanced Analytics
- **Multi-branch comparison**: Side-by-side performance analysis
- **Trend analysis**: Historical performance patterns
- **Variance reporting**: Budget and forecast variances
- **Cost center analysis**: Department-level profitability

### Inventory Analysis

#### Stock Analytics
1. Navigate to **OPS Matrix → Reporting → Inventory Analysis**
2. Monitor:
   - **Stock turnover rates**: How quickly inventory moves
   - **Dead stock identification**: Slow-moving inventory
   - **Reorder point analysis**: When to replenish stock
   - **Valuation reports**: Inventory value by branch

## Governance and Compliance

### Approval Workflows

#### Managing Approvals
1. Navigate to **OPS Matrix → Approvals**
2. View **Pending Approvals**: Items waiting for your decision
3. Review **Approval History**: Past approvals and rejections
4. Access **Approval Analytics**: Workflow performance metrics

#### Approval Types
- **Sales Order Approvals**: Large or special orders
- **Purchase Approvals**: Budget and vendor approvals
- **Transfer Approvals**: Inter-branch stock movements
- **Budget Amendments**: Changes to allocated budgets

### SLA Monitoring

#### Viewing SLA Status
1. Navigate to **OPS Matrix → Governance → SLA Instances**
2. Monitor active SLAs:
   - **On Track**: Meeting time commitments
   - **Warning**: Approaching breach thresholds
   - **Breached**: Exceeded time limits

#### SLA Types
- **Order Processing**: Time to confirm orders
- **Delivery Commitments**: On-time delivery targets
- **Approval Times**: Maximum approval processing time
- **Response Times**: Customer service commitments

## Product and Customer Management

### Product Management

#### Branch-Specific Products
- View products available in your branch
- Manage branch-specific pricing
- Track product availability and stock levels
- Request products from other branches

#### Product Requests
1. Navigate to **OPS Matrix → Product Requests**
2. Create request for unavailable products
3. Specify quantity and delivery requirements
4. Submit for approval and processing

### Customer Management

#### Customer Data Access
- View customers associated with your branch
- Access customer history and preferences
- Manage customer-specific pricing agreements
- Track customer interactions and orders

#### Customer Analytics
- Customer profitability analysis
- Purchase patterns and trends
- Customer lifetime value metrics
- Segmentation and targeting insights

## Mobile and Remote Access

### Web Interface Features
- **Responsive Design**: Works on tablets and mobile devices
- **Touch-Friendly**: Optimized for touch interactions
- **Offline Viewing**: Limited offline capabilities for key data
- **Push Notifications**: Real-time alerts for important events

### API Integration
For external system integration:
- Generate personal API keys
- Access RESTful endpoints
- Retrieve real-time data
- Automated data synchronization

## Best Practices

### Daily Operations
1. **Check Dashboards**: Start each day reviewing key metrics
2. **Review Approvals**: Process pending approvals promptly
3. **Monitor SLAs**: Ensure service level commitments are met
4. **Update Tasks**: Keep customer and order information current

### Data Entry Standards
1. **Complete Information**: Fill all required fields accurately
2. **Consistent Naming**: Use standard product and customer names
3. **Proper Classification**: Assign correct branches and business units
4. **Timely Entry**: Record transactions as they occur

### Security Practices
1. **Secure Credentials**: Never share login information
2. **Regular Logouts**: Log out when not using the system
3. **Report Issues**: Notify administrators of suspicious activity
4. **Follow Approval Rules**: Do not bypass required approvals

### Performance Optimization
1. **Use Filters**: Narrow searches to relevant data
2. **Batch Operations**: Process multiple items together when possible
3. **Regular Cleanup**: Archive completed transactions
4. **Monitor Usage**: Be aware of system performance impacts

## Common User Tasks

### Monthly Reporting
1. Generate sales reports for your branch
2. Review budget utilization
3. Analyze inventory turnover
4. Prepare management summaries

### Customer Management
1. Review customer order history
2. Identify upsell opportunities
3. Monitor payment patterns
4. Update customer contact information

### Inventory Control
1. Review stock levels daily
2. Process incoming shipments
3. Initiate inter-branch transfers as needed
4. Monitor product availability

### Approval Management
1. Review pending approvals daily
2. Prioritize by urgency and amount
3. Communicate with requestors as needed
4. Document approval decisions

## Getting Help

### Self-Service Resources
- **In-App Help**: Click help icons for context-sensitive assistance
- **Tooltips**: Hover over fields for additional information
- **Search**: Use global search for features and data
- **Documentation**: Access this user guide and others

### Support Channels
- **Supervisor**: Contact your branch manager or BU leader
- **Help Desk**: Submit tickets for technical issues
- **Training**: Attend scheduled training sessions
- **Administrator**: Contact system administrators for configuration issues

Remember, the OPS Matrix Framework is designed to streamline your multi-branch operations while maintaining strict governance and compliance. Regular use of the dashboards and following established approval processes will ensure smooth operations across your organization.