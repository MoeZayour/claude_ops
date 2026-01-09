# OPS Matrix Framework - API Reference

This comprehensive API reference provides detailed documentation for integrating with the OPS Matrix Framework via its RESTful API. The API enables external systems to interact with multi-branch operations, access real-time data, and automate business processes.

## API Overview

### Base URL
```
http://your-odoo-server:port/api/v1/ops_matrix
```

### Authentication
All API requests (except health check) require 256-bit token authentication:
```
X-API-Key: your_256_bit_token_here
```

### Request/Response Format
- **Content-Type**: `application/json`
- **Accept**: `application/json`
- **Response Format**: JSON with consistent structure

### Common Response Structure
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully",
  "timestamp": "2025-12-28T10:00:00Z",
  "request_id": "req_123456"
}
```

### Error Response Structure
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* additional error context */ }
  },
  "timestamp": "2025-12-28T10:00:00Z",
  "request_id": "req_123456"
}
```

## Authentication & Security

### API Key Generation
API keys are generated through the Odoo web interface:
1. Navigate to **OPS Matrix → API Keys**
2. Create new key linked to a persona
3. Copy the generated key (shown only once)

### Security Features
- **Rate Limiting**: Configurable per-user limits
- **IP Whitelisting**: Optional IP-based access control
- **Audit Logging**: All API requests are logged
- **Persona-Based Access**: Keys inherit user permissions

## Core Endpoints

### 1. Health Check
**Endpoint**: `GET/POST /health`
**Authentication**: Not required
**Description**: Check API availability and system status

#### Request
```bash
curl -X GET http://localhost:8089/api/v1/ops_matrix/health
```

#### Response
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "19.0.1.3",
    "timestamp": "2025-12-28T10:00:00Z",
    "uptime": "7 days, 14 hours"
  }
}
```

### 2. Current User Information
**Endpoint**: `POST /me`
**Authentication**: Required
**Description**: Get current user information and permissions

#### Request
```bash
curl -X POST http://localhost:8089/api/v1/ops_matrix/me \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json"
```

#### Response
```json
{
  "success": true,
  "data": {
    "user_id": 123,
    "name": "John Doe",
    "email": "john.doe@company.com",
    "personas": [
      {
        "id": 456,
        "name": "Branch Manager",
        "branches": [1, 2],
        "business_units": [1]
      }
    ],
    "allowed_branches": [1, 2],
    "allowed_business_units": [1]
  }
}
```

### 3. List Branches
**Endpoint**: `POST /branches`
**Authentication**: Required
**Description**: Retrieve branch information with optional filtering

#### Parameters
```json
{
  "filters": {
    "active": true,
    "business_unit_id": 1
  },
  "fields": ["id", "name", "code", "manager_id"],
  "limit": 50,
  "offset": 0,
  "order": "name asc"
}
```

#### Request Example
```bash
curl -X POST http://localhost:8089/api/v1/ops_matrix/branches \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {"active": true},
    "fields": ["id", "name", "code"],
    "limit": 10
  }'
```

#### Response
```json
{
  "success": true,
  "data": {
    "count": 5,
    "branches": [
      {
        "id": 1,
        "name": "Main Branch",
        "code": "MAIN"
      },
      {
        "id": 2,
        "name": "North Branch",
        "code": "NORTH"
      }
    ]
  }
}
```

### 4. Branch Details
**Endpoint**: `POST /branches/<id>`
**Authentication**: Required
**Description**: Get detailed information for a specific branch

#### Request
```bash
curl -X POST http://localhost:8089/api/v1/ops_matrix/branches/1 \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json"
```

#### Response
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Main Branch",
    "code": "MAIN",
    "company_id": 1,
    "manager_id": 123,
    "address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345"
    },
    "business_units": [1, 2],
    "active": true
  }
}
```

### 5. List Business Units
**Endpoint**: `POST /business_units`
**Authentication**: Required
**Description**: Retrieve business unit information

#### Request
```bash
curl -X POST http://localhost:8089/api/v1/ops_matrix/business_units \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"filters": {"active": true}}'
```

#### Response
```json
{
  "success": true,
  "data": {
    "count": 3,
    "business_units": [
      {
        "id": 1,
        "name": "Sales Division",
        "code": "SALES",
        "leader_id": 456,
        "branches": [1, 2, 3]
      }
    ]
  }
}
```

### 6. Business Unit Details
**Endpoint**: `POST /business_units/<id>`
**Authentication**: Required
**Description**: Get detailed BU information

### 7. Sales Analysis
**Endpoint**: `POST /sales_analysis`
**Authentication**: Required
**Description**: Retrieve sales performance data with aggregations

#### Parameters
```json
{
  "date_from": "2025-01-01",
  "date_to": "2025-12-31",
  "branch_ids": [1, 2],
  "bu_ids": [1],
  "group_by": ["branch_id", "date:month"],
  "measures": ["amount_total", "margin_total"],
  "filters": {
    "state": "sale"
  }
}
```

#### Request Example
```bash
curl -X POST http://localhost:8089/api/v1/ops_matrix/sales_analysis \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "date_from": "2025-01-01",
    "date_to": "2025-12-31",
    "branch_ids": [1],
    "group_by": ["date:month"],
    "measures": ["amount_total"]
  }'
```

#### Response
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_amount": 1250000.00,
      "total_orders": 450,
      "average_order": 2777.78
    },
    "groups": [
      {
        "date": "2025-01-01",
        "amount_total": 95000.00,
        "order_count": 35
      },
      {
        "date": "2025-02-01",
        "amount_total": 112000.00,
        "order_count": 42
      }
    ]
  }
}
```

### 8. Approval Requests
**Endpoint**: `POST /approval_requests`
**Authentication**: Required
**Description**: List pending approval requests

#### Parameters
```json
{
  "status": "pending",
  "request_type": "sale_order",
  "limit": 20,
  "offset": 0
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "count": 15,
    "requests": [
      {
        "id": 789,
        "type": "sale_order",
        "reference": "SO00123",
        "amount": 15000.00,
        "requester": "Jane Smith",
        "submitted_date": "2025-12-28T09:00:00Z",
        "approvers": ["John Doe", "Mike Johnson"]
      }
    ]
  }
}
```

### 9. Approval Request Details
**Endpoint**: `POST /approval_requests/<id>`
**Authentication**: Required
**Description**: Get detailed approval request information

### 10. Approve Request
**Endpoint**: `POST /approval_requests/<id>/approve`
**Authentication**: Required
**Description**: Approve an approval request

#### Request
```bash
curl -X POST http://localhost:8089/api/v1/ops_matrix/approval_requests/789/approve \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"comments": "Approved for Q4 sales target"}'
```

#### Response
```json
{
  "success": true,
  "data": {
    "request_id": 789,
    "status": "approved",
    "approved_by": "John Doe",
    "approved_at": "2025-12-28T10:30:00Z"
  }
}
```

### 11. Reject Request
**Endpoint**: `POST /approval_requests/<id>/reject`
**Authentication**: Required
**Description**: Reject an approval request

### 12. Stock Levels
**Endpoint**: `POST /stock_levels`
**Authentication**: Required
**Description**: Query inventory levels across branches

#### Parameters
```json
{
  "branch_ids": [1, 2],
  "product_ids": [101, 102],
  "warehouse_ids": [1],
  "include_reserved": true,
  "filters": {
    "available_quantity": ">0"
  }
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "product_id": 101,
        "product_name": "Widget A",
        "branches": [
          {
            "branch_id": 1,
            "branch_name": "Main Branch",
            "quantity_available": 150,
            "quantity_reserved": 25,
            "quantity_free": 125
          }
        ]
      }
    ]
  }
}
```

## Advanced Parameters

### Filtering
Most endpoints support Odoo-style domain filtering:
```json
{
  "filters": [
    ["active", "=", true],
    ["company_id", "=", 1],
    "|",
    ["name", "ilike", "main"],
    ["code", "ilike", "main"]
  ]
}
```

### Field Selection
Specify which fields to return:
```json
{
  "fields": ["id", "name", "code", "active"]
}
```

### Sorting
Control result ordering:
```json
{
  "order": "name asc, create_date desc"
}
```

### Pagination
Handle large result sets:
```json
{
  "limit": 100,
  "offset": 200
}
```

## Rate Limiting

### Default Limits
- **Per User**: 1000 requests per hour
- **Per IP**: 10000 requests per hour
- **Burst Limit**: 100 requests per minute

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1640995200
```

### Rate Limit Response
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_API_KEY` | Invalid or missing API key | 401 |
| `ACCESS_DENIED` | Insufficient permissions | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `VALIDATION_ERROR` | Invalid request parameters | 400 |
| `RATE_LIMIT_EXCEEDED` | Rate limit exceeded | 429 |
| `INTERNAL_ERROR` | Server error | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |

## SDKs and Libraries

### Python Client
```python
from ops_matrix_client import OPSMatrixClient

client = OPSMatrixClient(
    base_url="http://localhost:8089/api/v1/ops_matrix",
    api_key="your_api_key"
)

# Get current user
user = client.me()
print(f"Welcome {user['name']}")

# List branches
branches = client.branches(limit=10)
for branch in branches['data']['branches']:
    print(f"{branch['name']} ({branch['code']})")
```

### JavaScript/Node.js Client
```javascript
const { OPSMatrixClient } = require('ops-matrix-client');

const client = new OPSMatrixClient({
  baseUrl: 'http://localhost:8089/api/v1/ops_matrix',
  apiKey: 'your_api_key'
});

// Get sales analysis
const analysis = await client.salesAnalysis({
  dateFrom: '2025-01-01',
  dateTo: '2025-12-31',
  branchIds: [1, 2]
});

console.log(analysis.data.summary);
```

## Best Practices

### Connection Management
- Reuse API connections when possible
- Implement exponential backoff for retries
- Handle rate limiting gracefully

### Error Handling
- Check response `success` field first
- Implement proper error logging
- Handle transient errors with retries

### Data Synchronization
- Use appropriate polling intervals
- Implement delta synchronization for large datasets
- Validate data integrity after synchronization

### Security
- Store API keys securely
- Rotate keys regularly
- Use HTTPS for all API communications
- Validate SSL certificates

### Performance
- Use field selection to reduce payload size
- Implement pagination for large datasets
- Cache frequently accessed data
- Batch related operations when possible

## Support and Resources

### Documentation
- [Introduction](01_Introduction.md) - Framework overview
- [Installation Guide](02_Installation_Guide.md) - Setup instructions
- [User Guide](04_User_Guide.md) - Feature usage
- [Administrator Guide](05_Administrator_Guide.md) - System management

### Getting Help
- Check [Troubleshooting](09_Troubleshooting.md) for common issues
- Review [FAQ](10_FAQ.md) for quick answers
- Contact system administrator for API key issues
- Use the health endpoint to verify API availability

### Version History
- **v1.0**: Initial release with core endpoints
- **v1.1**: Added advanced filtering and pagination
- **v1.2**: Enhanced rate limiting and security features

The OPS Matrix API provides comprehensive access to multi-branch operations, enabling seamless integration with external systems and automated business processes.