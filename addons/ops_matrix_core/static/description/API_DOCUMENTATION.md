# OPS Matrix REST API v1 Documentation

**Version**: 1.0  
**Base URL**: `http://your-odoo-server:8089/api/v1/ops_matrix`  
**Authentication**: API Key (X-API-Key header)  
**Format**: JSON

---

## 📋 Table of Contents

1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [Error Handling](#error-handling)
4. [Endpoints](#endpoints)
   - [Utility Endpoints](#utility-endpoints)
   - [Branch Endpoints](#branch-endpoints)
   - [Business Unit Endpoints](#business-unit-endpoints)
   - [Sales Analysis Endpoints](#sales-analysis-endpoints)
   - [Approval Request Endpoints](#approval-request-endpoints)
   - [Stock/Inventory Endpoints](#stockinventory-endpoints)
5. [Examples](#examples)
6. [Python Client](#python-client)

---

## Authentication

### Generating an API Key

1. **Navigate to**: Settings → Users & Companies → Users
2. **Select a user** (must have appropriate permissions)
3. **Click**: "Generate API Key" button
4. **Copy the key** (shown only once)
5. **Store securely** (treat like a password)

### Using the API Key

Include the API key in the `X-API-Key` header of every request:

```bash
curl -X POST \
  http://localhost:8089/api/v1/ops_matrix/branches \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: YOUR_API_KEY_HERE' \
  -d '{"params": {"limit": 10}}'
```

### Revoking an API Key

1. Navigate to user settings
2. Click "Revoke API Key" button
3. Generate a new key if needed

---

## Rate Limiting

**Default Limits**:
- 1000 requests per hour per user
- Configurable per user by administrators

**Rate Limit Headers** (included in responses):
```
_rate_limit_remaining: 999
_rate_limit_limit: 1000
```

**When Exceeded**:
```json
{
  "success": false,
  "error": "Rate limit exceeded. Maximum 1000 calls per hour.",
  "code": 429,
  "retry_after": 1800
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "success": false,
  "error": "Error message here",
  "code": 400,
  "timestamp": "2025-12-27T14:00:00"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | Success | Request completed successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Access denied (security rules) |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

---

## Endpoints

### Utility Endpoints

#### Health Check

**Endpoint**: `GET/POST /api/v1/ops_matrix/health`  
**Authentication**: None required  
**Purpose**: Check API availability

**Request**:
```bash
curl -X POST http://localhost:8089/api/v1/ops_matrix/health \
  -H 'Content-Type: application/json' \
  -d '{"params": {}}'
```

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0",
  "timestamp": "2025-12-27T14:00:00",
  "database": "mz-db",
  "server_time": "2025-12-27 14:00:00"
}
```

#### Current User Info

**Endpoint**: `GET/POST /api/v1/ops_matrix/me`  
**Authentication**: Required  
**Purpose**: Get authenticated user information

**Request**:
```bash
curl -X POST http://localhost:8089/api/v1/ops_matrix/me \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: YOUR_API_KEY' \
  -d '{"params": {}}'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 5,
    "name": "John Doe",
    "email": "john@example.com",
    "login": "john.doe",
    "company": {
      "id": 1,
      "name": "My Company"
    },
    "allowed_branches": [
      {
        "id": 1,
        "name": "Main Branch",
        "code": "MB001"
      }
    ],
    "allowed_business_units": [
      {
        "id": 2,
        "name": "Sales Division",
        "code": "SD001"
      }
    ],
    "groups": ["Sales Manager", "Internal User"],
    "is_admin": false
  }
}
```

---

### Branch Endpoints

#### List Branches

**Endpoint**: `POST /api/v1/ops_matrix/branches`  
**Authentication**: Required  
**Purpose**: List all accessible branches

**Request Body**:
```json
{
  "params": {
    "filters": [["active", "=", true]],
    "limit": 100,
    "offset": 0,
    "fields": ["name", "code", "manager_id", "active"]
  }
}
```

**Parameters**:
- `filters` (optional): Odoo domain filters (array of tuples)
- `limit` (optional): Maximum records to return (default: 100, max: 1000)
- `offset` (optional): Pagination offset (default: 0)
- `fields` (optional): Fields to return (default: id, name, code, active, manager_id)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Main Branch",
      "code": "MB001",
      "active": true,
      "manager_id": [5, "John Doe"]
    },
    {
      "id": 2,
      "name": "Secondary Branch",
      "code": "SB002",
      "active": true,
      "manager_id": [6, "Jane Smith"]
    }
  ],
  "count": 2,
  "total": 10,
  "limit": 100,
  "offset": 0
}
```

#### Get Branch Details

**Endpoint**: `GET/POST /api/v1/ops_matrix/branches/<branch_id>`  
**Authentication**: Required  
**Purpose**: Get detailed information about a specific branch

**Request**:
```bash
curl -X POST http://localhost:8089/api/v1/ops_matrix/branches/1 \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: YOUR_API_KEY' \
  -d '{"params": {}}'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Main Branch",
    "code": "MB001",
    "active": true,
    "manager_id": [5, "John Doe"],
    "company_id": [1, "My Company"],
    "address": "123 Main St",
    "phone": "+1-555-0100",
    "email": "main@company.com",
    "business_units": [
      {
        "id": 2,
        "name": "Sales Division",
        "code": "SD001",
        "active": true
      }
    ],
    "create_date": "2025-01-01T00:00:00",
    "write_date": "2025-12-27T10:00:00"
  }
}
```

---

### Business Unit Endpoints

#### List Business Units

**Endpoint**: `POST /api/v1/ops_matrix/business_units`  
**Authentication**: Required  
**Purpose**: List all accessible business units

**Request Body**:
```json
{
  "params": {
    "filters": [["active", "=", true]],
    "limit": 100,
    "offset": 0,
    "fields": ["name", "code", "ops_branch_id"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 2,
      "name": "Sales Division",
      "code": "SD001",
      "active": true,
      "ops_branch_id": [1, "Main Branch"]
    }
  ],
  "count": 1,
  "total": 5
}
```

#### Get Business Unit Details

**Endpoint**: `GET/POST /api/v1/ops_matrix/business_units/<bu_id>`  
**Authentication**: Required  
**Purpose**: Get detailed information about a specific business unit

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Sales Division",
    "code": "SD001",
    "active": true,
    "ops_branch_id": [1, "Main Branch"],
    "manager_id": [7, "Sales Manager"],
    "create_date": "2025-01-01T00:00:00"
  }
}
```

---

### Sales Analysis Endpoints

#### Query Sales Data

**Endpoint**: `POST /api/v1/ops_matrix/sales_analysis`  
**Authentication**: Required  
**Purpose**: Query sales data with filters and aggregations

**Request Body**:
```json
{
  "params": {
    "date_from": "2025-01-01",
    "date_to": "2025-12-31",
    "branch_ids": [1, 2],
    "bu_ids": [2, 3],
    "state": "sale",
    "group_by": ["ops_branch_id"],
    "fields": ["amount_total:sum", "id:count"],
    "limit": 100
  }
}
```

**Parameters**:
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `branch_ids` (optional): Filter by branch IDs
- `bu_ids` (optional): Filter by business unit IDs
- `state` (optional): Order state (default: sale, done)
- `group_by` (optional): Fields to group by (for aggregations)
- `fields` (optional): Fields to return/aggregate
- `limit` (optional): Maximum records (default: 100)

**Response (Aggregated)**:
```json
{
  "success": true,
  "data": [
    {
      "ops_branch_id": [1, "Main Branch"],
      "amount_total": 500000.00,
      "id_count": 250
    },
    {
      "ops_branch_id": [2, "Secondary Branch"],
      "amount_total": 300000.00,
      "id_count": 150
    }
  ],
  "count": 2,
  "aggregations": {
    "total_revenue": 800000.00,
    "total_orders": 400,
    "average_order_value": 2000.00
  },
  "filters_applied": {
    "date_from": "2025-01-01",
    "date_to": "2025-12-31",
    "branches": [1, 2],
    "business_units": [2, 3]
  }
}
```

**Response (Detailed - without group_by)**:
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "name": "SO00123",
      "date_order": "2025-06-15T10:30:00",
      "partner_id": [42, "Customer ABC"],
      "amount_total": 5000.00,
      "state": "sale"
    }
  ],
  "count": 100,
  "aggregations": {
    "total_revenue": 800000.00,
    "total_orders": 400,
    "average_order_value": 2000.00
  }
}
```

---

### Approval Request Endpoints

#### List Approval Requests

**Endpoint**: `POST /api/v1/ops_matrix/approval_requests`  
**Authentication**: Required  
**Purpose**: List approval requests where user is an approver

**Request Body**:
```json
{
  "params": {
    "state": "pending",
    "approval_type": "sale_order",
    "limit": 50
  }
}
```

**Parameters**:
- `state` (optional): pending, approved, rejected
- `approval_type` (optional): sale_order, purchase_order, etc.
- `limit` (optional): Maximum records (default: 50)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 42,
      "name": "Approval for SO00123",
      "state": "pending",
      "approval_type": "sale_order",
      "priority": "high",
      "create_date": "2025-12-27T10:00:00",
      "approver_ids": [[5, 6, 7]]
    }
  ],
  "count": 1
}
```

#### Get Approval Request Status

**Endpoint**: `GET/POST /api/v1/ops_matrix/approval_requests/<approval_id>`  
**Authentication**: Required  
**Purpose**: Get detailed status of an approval request

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 42,
    "name": "Approval for SO00123",
    "state": "pending",
    "approval_type": "sale_order",
    "priority": "high",
    "create_date": "2025-12-27T10:00:00",
    "approvers": [
      {
        "id": 5,
        "name": "Manager 1",
        "email": "manager1@company.com"
      },
      {
        "id": 6,
        "name": "Manager 2",
        "email": "manager2@company.com"
      }
    ],
    "notes": "Requires urgent approval for large order"
  }
}
```

#### Approve Request

**Endpoint**: `POST /api/v1/ops_matrix/approval_requests/<approval_id>/approve`  
**Authentication**: Required  
**Purpose**: Approve an approval request

**Request Body**:
```json
{
  "params": {
    "notes": "Approved - budget confirmed"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Approval request approved successfully",
  "data": {
    "id": 42,
    "state": "approved"
  }
}
```

#### Reject Request

**Endpoint**: `POST /api/v1/ops_matrix/approval_requests/<approval_id>/reject`  
**Authentication**: Required  
**Purpose**: Reject an approval request

**Request Body**:
```json
{
  "params": {
    "reason": "Exceeds budget constraints"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Approval request rejected",
  "data": {
    "id": 42,
    "state": "rejected"
  }
}
```

---

### Stock/Inventory Endpoints

#### Query Stock Levels

**Endpoint**: `POST /api/v1/ops_matrix/stock_levels`  
**Authentication**: Required  
**Purpose**: Query current stock levels by branch/warehouse

**Request Body**:
```json
{
  "params": {
    "branch_ids": [1, 2],
    "product_ids": [10, 20, 30],
    "limit": 100
  }
}
```

**Parameters**:
- `branch_ids` (optional): Filter by branch IDs
- `product_ids` (optional): Filter by product IDs
- `limit` (optional): Maximum records (default: 100)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "product_id": [10, "Product A"],
      "location_id": [5, "Main Warehouse/Stock"],
      "quantity_on_hand": 150.00,
      "reserved_quantity": 20.00,
      "available_quantity": 130.00
    },
    {
      "product_id": [20, "Product B"],
      "location_id": [5, "Main Warehouse/Stock"],
      "quantity_on_hand": 75.00,
      "reserved_quantity": 0.00,
      "available_quantity": 75.00
    }
  ],
  "count": 2
}
```

---

## Examples

### Example 1: Get All Active Branches

```python
import requests

API_URL = "http://localhost:8089/api/v1/ops_matrix"
API_KEY = "your-api-key-here"

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
}

payload = {
    "params": {
        "filters": [["active", "=", True]],
        "limit": 50
    }
}

response = requests.post(
    f"{API_URL}/branches",
    json=payload,
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    if result.get('success'):
        branches = result['data']
        print(f"Found {result['count']} branches:")
        for branch in branches:
            print(f"  - {branch['name']} ({branch['code']})")
    else:
        print(f"Error: {result.get('error')}")
else:
    print(f"HTTP Error: {response.status_code}")
```

### Example 2: Sales Analysis by Branch

```python
import requests
from datetime import datetime, timedelta

API_URL = "http://localhost:8089/api/v1/ops_matrix"
API_KEY = "your-api-key-here"

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
}

# Get last 30 days of sales
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

payload = {
    "params": {
        "date_from": start_date.strftime('%Y-%m-%d'),
        "date_to": end_date.strftime('%Y-%m-%d'),
        "group_by": ["ops_branch_id"],
        "fields": ["amount_total:sum", "id:count"]
    }
}

response = requests.post(
    f"{API_URL}/sales_analysis",
    json=payload,
    headers=headers
)

result = response.json()
if result.get('success'):
    print(f"Sales Summary (Last 30 Days)")
    print(f"Total Revenue: ${result['aggregations']['total_revenue']:,.2f}")
    print(f"Total Orders: {result['aggregations']['total_orders']}")
    print(f"\nBy Branch:")
    for item in result['data']:
        branch_name = item['ops_branch_id'][1]
        revenue = item['amount_total']
        orders = item['id_count']
        print(f"  {branch_name}: ${revenue:,.2f} ({orders} orders)")
```

### Example 3: Approve Pending Requests

```python
import requests

API_URL = "http://localhost:8089/api/v1/ops_matrix"
API_KEY = "your-api-key-here"

headers = {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
}

# Get pending approvals
response = requests.post(
    f"{API_URL}/approval_requests",
    json={"params": {"state": "pending"}},
    headers=headers
)

result = response.json()
if result.get('success'):
    pending = result['data']
    print(f"Found {len(pending)} pending approvals")
    
    # Approve each one (with user confirmation)
    for approval in pending:
        print(f"\nApproval: {approval['name']}")
        print(f"Type: {approval['approval_type']}")
        print(f"Priority: {approval['priority']}")
        
        confirm = input("Approve? (y/n): ")
        if confirm.lower() == 'y':
            approve_response = requests.post(
                f"{API_URL}/approval_requests/{approval['id']}/approve",
                json={"params": {"notes": "Approved via API"}},
                headers=headers
            )
            
            approve_result = approve_response.json()
            if approve_result.get('success'):
                print(f"✓ Approved: {approval['name']}")
            else:
                print(f"✗ Failed: {approve_result.get('error')}")
```

---

## Python Client

### Installation

No additional dependencies required beyond `requests`:

```bash
pip install requests
```

### Complete Client Example

Save this as `ops_matrix_client.py`:

```python
#!/usr/bin/env python3
"""
OPS Matrix API Client
Simple Python client for OPS Matrix REST API
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class OpsMatrixClient:
    """Client for OPS Matrix REST API v1"""
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize client
        
        Args:
            base_url: Base URL (e.g., "http://localhost:8089")
            api_key: Your API key
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api/v1/ops_matrix"
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        payload = {"params": params or {}}
        
        response = requests.request(
            method,
            url,
            json=payload,
            headers=self.headers
        )
        
        return response.json()
    
    # Health & Authentication
    def health_check(self) -> Dict:
        """Check API health"""
        return requests.post(
            f"{self.api_url}/health",
            json={"params": {}},
            headers={'Content-Type': 'application/json'}
        ).json()
    
    def get_current_user(self) -> Dict:
        """Get current authenticated user info"""
        return self._request('POST', '/me')
    
    # Branches
    def list_branches(self, filters=None, limit=100, offset=0, fields=None) -> Dict:
        """List branches"""
        params = {
            'filters': filters or [],
            'limit': limit,
            'offset': offset,
            'fields': fields or ['id', 'name', 'code', 'active']
        }
        return self._request('POST', '/branches', params)
    
    def get_branch(self, branch_id: int) -> Dict:
        """Get branch details"""
        return self._request('POST', f'/branches/{branch_id}')
    
    # Business Units
    def list_business_units(self, filters=None, limit=100) -> Dict:
        """List business units"""
        params = {
            'filters': filters or [],
            'limit': limit
        }
        return self._request('POST', '/business_units', params)
    
    def get_business_unit(self, bu_id: int) -> Dict:
        """Get business unit details"""
        return self._request('POST', f'/business_units/{bu_id}')
    
    # Sales Analysis
    def sales_analysis(self, date_from=None, date_to=None, branch_ids=None, 
                      bu_ids=None, group_by=None, limit=100) -> Dict:
        """Query sales data"""
        params = {
            'date_from': date_from,
            'date_to': date_to,
            'branch_ids': branch_ids,
            'bu_ids': bu_ids,
            'group_by': group_by,
            'limit': limit
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        return self._request('POST', '/sales_analysis', params)
    
    # Approvals
    def list_approval_requests(self, state=None, approval_type=None, limit=50) -> Dict:
        """List approval requests"""
        params = {
            'state': state,
            'approval_type': approval_type,
            'limit': limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._request('POST', '/approval_requests', params)
    
    def get_approval_status(self, approval_id: int) -> Dict:
        """Get approval request status"""
        return self._request('POST', f'/approval_requests/{approval_id}')
    
    def approve_request(self, approval_id: int, notes: str = "") -> Dict:
        """Approve an approval request"""
        return self._request('POST', f'/approval_requests/{approval_id}/approve', {'notes': notes})
    
    def reject_request(self, approval_id: int, reason: str) -> Dict:
        """Reject an approval request"""
        return self._request('POST', f'/approval_requests/{approval_id}/reject', {'reason': reason})
    
    # Stock
    def query_stock_levels(self, branch_ids=None, product_ids=None, limit=100) -> Dict:
        """Query stock levels"""
        params = {
            'branch_ids': branch_ids,
            'product_ids': product_ids,
            'limit': limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        return self._request('POST', '/stock_levels', params)


# Example usage
if __name__ == '__main__':
    # Initialize client
    client = OpsMatrixClient(
        base_url='http://localhost:8089',
        api_key='YOUR_API_KEY_HERE'
    )
    
    # Health check
    print("API Health:", client.health_check())
    
    # Get current user
    user = client.get_current_user()
    if user.get('success'):
        print(f"\nAuthenticated as: {user['data']['name']}")
        print(f"Allowed branches: {len(user['data']['allowed_branches'])}")
    
    # List branches
    branches = client.list_branches(limit=10)
    if branches.get('success'):
        print(f"\nBranches ({branches['count']}):")
        for branch in branches['data']:
            print(f"  - {branch['name']} ({branch['code']})")
    
    # Sales analysis (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    sales = client.sales_analysis(
        date_from=start_date.strftime('%Y-%m-%d'),
        date_to=end_date.strftime('%Y-%m-%d'),
        group_by=['ops_branch_id']
    )
    
    if sales.get('success'):
        print(f"\nSales Summary:")
        print(f"Total Revenue: ${sales['aggregations']['total_revenue']:,.2f}")
        print(f"Total Orders: {sales['aggregations']['total_orders']}")
```

### Usage

```bash
# Install dependencies
pip install requests

# Edit the script and add your API key
nano ops_matrix_client.py

# Run
python3 ops_matrix_client.py
```

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for API keys in production
3. **Rotate keys regularly** (quarterly recommended)
4. **Monitor API usage** through Odoo logs
5. **Revoke compromised keys** immediately
6. **Use HTTPS** in production (not HTTP)
7. **Implement IP whitelisting** if possible
8. **Set appropriate rate limits** per user
9. **Log all API access** for audit trails
10. **Use service accounts** for automated integrations

---

## Support & Troubleshooting

### Common Issues

**401 Unauthorized**:
- Check API key is correct
- Verify key hasn't been revoked
- Ensure user account is active

**403 Forbidden**:
- User lacks permission to access resource
- Check security rules in Odoo
- Verify branch/BU access rights

**429 Rate Limit Exceeded**:
- Wait for rate limit reset
- Contact admin to increase limit
- Implement request throttling in client

**500 Internal Server Error**:
- Check Odoo logs for details
- Verify data integrity
- Report to system administrator

### Logging

API access is logged in Odoo:
- Location: Settings → Technical → Logging
- Search for: "API access"
- View user, endpoint, timestamp

---

## Changelog

### Version 1.0 (2025-12-27)
- Initial release
- Branch & Business Unit endpoints
- Sales analysis endpoint
- Approval workflow endpoints
- Stock query endpoint
- Rate limiting
- API key authentication
- Comprehensive error handling

---

## License

This API is part of the OPS Matrix Framework for Odoo 19.  
© 2025 - All rights reserved.
