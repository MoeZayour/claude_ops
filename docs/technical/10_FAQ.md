# OPS Matrix Framework - Frequently Asked Questions

This FAQ covers the most common questions about the OPS Matrix Framework. If you don't find your answer here, check the relevant guide or contact support.

## General Questions

### What is the OPS Matrix Framework?

**Answer:** The OPS Matrix Framework is a comprehensive enterprise extension for Odoo 19 Community Edition that provides multi-branch, multi-business unit capabilities. It enables organizations to operate across multiple locations while maintaining strict data isolation, automated governance, and centralized analytics.

**Key features include:**
- Multi-branch architecture with data siloing
- Persona-based security and access control
- Automated approval workflows and governance
- Real-time dashboards and reporting
- RESTful API for system integration

### What versions of Odoo are supported?

**Answer:** The OPS Matrix Framework is specifically designed for Odoo 19 Community Edition. It is not compatible with Odoo Enterprise or earlier versions of Odoo Community Edition.

### Is the framework free to use?

**Answer:** Yes, the OPS Matrix Framework is provided as open-source software under the same license as Odoo Community Edition. However, implementation services, custom development, and support may involve additional costs depending on your requirements.

### How many branches and business units can I have?

**Answer:** There are no technical limitations on the number of branches or business units. The framework is designed to scale to hundreds or thousands of branches, limited only by your database and hardware capabilities.

## Installation and Setup

### Do I need to modify my existing Odoo installation?

**Answer:** No major modifications are required to your core Odoo installation. The OPS Matrix Framework adds new modules that extend existing functionality. However, you will need to configure branches, business units, and user permissions after installation.

### Can I install OPS Matrix on an existing Odoo database?

**Answer:** Yes, but it's recommended to install on a fresh database for initial testing. If installing on an existing database, ensure all users are logged out during the installation process, and perform a full backup first.

### What are the system requirements?

**Answer:**
- **Operating System:** Linux (Ubuntu 20.04+, CentOS 7+, or equivalent)
- **Python:** Version 3.10 or higher
- **Database:** PostgreSQL 14 or higher
- **Memory:** Minimum 4GB RAM (8GB recommended)
- **Storage:** 20GB+ free disk space

### Can I use OPS Matrix with Docker?

**Answer:** Yes, the framework is fully compatible with Docker deployments. Docker Compose files are provided for easy containerized deployment.

## Security and Access Control

### How does data isolation work between branches?

**Answer:** The framework implements strict data isolation through record-level security rules. Users can only see and modify data from branches they are assigned to via their personas. Managers can see data across their business unit, while administrators have unrestricted access.

### Can users be assigned to multiple branches?

**Answer:** Yes, users can be assigned multiple personas, each granting access to different branches and business units. This allows for complex organizational structures where employees work across multiple locations.

### What happens if a user needs emergency access to another branch's data?

**Answer:** Emergency access can be granted by temporarily assigning additional personas or by administrators using their unrestricted access. All emergency access is logged in the audit trail for compliance purposes.

### Are API keys secure?

**Answer:** Yes, API keys use cryptographically secure random generation and are stored as SHA-256 hashes. Keys are displayed only once during creation and cannot be recovered if lost. Each key is tied to specific personas and inherits their access rights.

## Features and Functionality

### Can I customize approval workflows?

**Answer:** Yes, the governance engine allows extensive customization of approval workflows. You can define rules based on amount thresholds, specific conditions, user roles, and sequential or parallel approval processes.

### How does the SLA monitoring work?

**Answer:** SLA templates define time commitments for various business processes (like order processing or approvals). The system automatically creates SLA instances and monitors them, sending alerts when breaches occur and providing dashboards for performance tracking.

### Can I export data to Excel?

**Answer:** Yes, the framework includes comprehensive Excel export capabilities. You can export data from any list view with custom column selection, and large datasets are handled through background processing to prevent timeouts.

### Does the framework support multi-currency?

**Answer:** Yes, multi-currency support is inherited from Odoo. Financial reports can display amounts in different currencies, and exchange rates are managed through Odoo's built-in currency functionality.

## Performance and Scaling

### How does the framework perform with large datasets?

**Answer:** The framework is designed for enterprise-scale operations. It uses database indexing, efficient queries, and background processing for heavy operations. Performance depends on your hardware and database optimization, but it can handle millions of records across hundreds of branches.

### Can I use the framework on mobile devices?

**Answer:** Yes, Odoo's responsive web interface works on tablets and mobile devices. The framework includes mobile-optimized dashboards and approval workflows for on-the-go access.

### What are the API rate limits?

**Answer:** Default rate limits are 1000 requests per hour per user and 10,000 requests per hour per IP address. These can be configured per your needs, and burst limits (100 requests per minute) provide additional flexibility.

## Integration and APIs

### Can I integrate OPS Matrix with other systems?

**Answer:** Yes, the RESTful API provides comprehensive integration capabilities. You can read and write data, trigger workflows, and access real-time analytics from external systems.

### What programming languages support the API?

**Answer:** The API is RESTful and works with any HTTP client. Official SDKs are available for Python, and examples are provided for JavaScript/Node.js, Java, and other languages.

### Can I use webhooks for real-time notifications?

**Answer:** While not included in the base framework, webhooks can be implemented through custom development using the API and Odoo's server actions functionality.

## Maintenance and Support

### How do I update the framework?

**Answer:** Updates should be applied following Odoo's module upgrade procedures. Always backup your database before upgrading, and test in a staging environment first.

### Is there a way to protect my source code?

**Answer:** Yes, the vault build script compiles Python source code to binary .so files, making the code unreadable while maintaining full functionality. This is recommended for production deployments.

### What backup strategy is recommended?

**Answer:** Daily database and filestore backups, weekly full system backups, and monthly archive backups. Implement off-site storage and regular restore testing.

### How do I monitor system health?

**Answer:** Use Odoo's built-in monitoring, check API audit logs, review governance violation reports, and monitor dashboard performance. The framework includes comprehensive logging and alerting capabilities.

## Troubleshooting

### Users can't see expected data - what should I check?

**Answer:** Check persona assignments, branch/BU access rights, and record rule configurations. Use the troubleshooting guide to verify user permissions and data visibility.

### API calls are failing - what could be wrong?

**Answer:** Verify API key validity, check rate limits, confirm endpoint URLs, and review the audit logs for specific error messages.

### Reports are running slowly - how can I improve performance?

**Answer:** Check database indexes, optimize queries, clear caches, and consider background processing for large reports. Review system resources and consider hardware upgrades if needed.

### Approvals aren't working - what should I check?

**Answer:** Verify governance rules are active and properly configured, check user permissions for creating approvals, and ensure approvers are properly assigned.

## Compliance and Security

### Is the framework GDPR compliant?

**Answer:** The framework includes features to support GDPR compliance, including data minimization, audit trails, and user consent mechanisms. However, complete compliance requires proper configuration and organizational policies.

### Can I use OPS Matrix for SOX compliance?

**Answer:** Yes, the framework supports SOX compliance through segregation of duties, approval workflows, comprehensive audit trails, and financial controls.

### How secure is the data isolation?

**Answer:** Data isolation is enforced at the database level through record rules. Extensive testing has confirmed zero cross-branch data leakage in properly configured systems.

### What encryption is used?

**Answer:** API keys are hashed with SHA-256, database connections can use SSL/TLS, and file storage encryption is supported. The vault build provides source code protection through binary compilation.

## Development and Customization

### Can I extend the framework with custom modules?

**Answer:** Yes, the framework is designed for extensibility. You can add custom models, views, workflows, and API endpoints following standard Odoo development practices.

### What programming languages can I use for custom development?

**Answer:** Python is the primary language for backend development. JavaScript is used for frontend components. XML is used for views and data definitions.

### Is there a developer community or support?

**Answer:** While the framework is open-source, development support is available through documentation, code comments, and professional services. The developer guide provides comprehensive information for customization.

### Can I contribute to the framework development?

**Answer:** Yes, contributions are welcome following standard open-source practices. Please review the developer guide and submit pull requests for bug fixes, enhancements, or new features.

## Licensing and Legal

### What license is the framework under?

**Answer:** The OPS Matrix Framework is released under the same LGPL-3 license as Odoo Community Edition.

### Can I use it for commercial purposes?

**Answer:** Yes, you can use, modify, and distribute the framework for commercial purposes, subject to the LGPL-3 license terms.

### Do I need to open-source my customizations?

**Answer:** No, you can keep your customizations proprietary. Only modifications to the core framework files would be subject to the LGPL-3 copyleft provisions.

For questions not covered in this FAQ, please consult the relevant guide or contact your system administrator/support team.