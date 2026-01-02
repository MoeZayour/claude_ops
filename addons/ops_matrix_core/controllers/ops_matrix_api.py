# -*- coding: utf-8 -*-

"""
OPS Matrix REST API v1
Provides RESTful API endpoints for external system integration
"""

from odoo import http, _
from odoo.http import request
import json
import logging
from functools import wraps
from datetime import datetime, timedelta
import time

_logger = logging.getLogger(__name__)


# ============================================================================
# DECORATORS & MIDDLEWARE
# ============================================================================

def authenticate_api_key(func):
    """
    Decorator to authenticate API key and create audit log
    
    This decorator:
    1. Extracts API key from X-API-Key header or api_key query parameter
    2. Validates the key against ops.api.key model
    3. Updates last_used and usage_count on the API key
    4. Creates comprehensive audit log entry
    5. Sets user context based on the persona's user
    6. Returns 401 if authentication fails
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        
        # Extract API key from header or query parameter
        api_key_token = request.httprequest.headers.get('X-API-Key')
        if not api_key_token:
            api_key_token = request.httprequest.args.get('api_key')
        
        # Get request metadata
        endpoint = request.httprequest.path
        http_method = request.httprequest.method
        ip_address = request.httprequest.remote_addr or request.httprequest.environ.get('HTTP_X_FORWARDED_FOR', 'Unknown')
        user_agent = request.httprequest.headers.get('User-Agent', 'Unknown')
        
        # Check if API key is provided
        if not api_key_token:
            response_time = time.time() - start_time
            
            # Log failed authentication attempt
            request.env['ops.audit.log'].sudo().log_api_request(
                endpoint=endpoint,
                http_method=http_method,
                ip_address=ip_address,
                user_agent=user_agent,
                status_code=401,
                response_time=response_time,
                error_message='Missing API key in X-API-Key header or api_key parameter'
            )
            
            return {
                'success': False,
                'error': _('Missing API key. Include X-API-Key header or api_key parameter in your request.'),
                'code': 401
            }
        
        # Validate API key
        ApiKey = request.env['ops.api.key'].sudo()
        api_key_record = ApiKey.validate_key(api_key_token)
        
        if not api_key_record:
            response_time = time.time() - start_time
            
            _logger.warning(f"Invalid API key attempt from {ip_address}: {api_key_token[:8]}...")
            
            # Log failed authentication
            request.env['ops.audit.log'].sudo().log_api_request(
                endpoint=endpoint,
                http_method=http_method,
                ip_address=ip_address,
                user_agent=user_agent,
                status_code=401,
                response_time=response_time,
                error_message=f'Invalid or inactive API key: {api_key_token[:8]}...'
            )
            
            return {
                'success': False,
                'error': _('Invalid or inactive API key'),
                'code': 401
            }
        
        # Set user context from persona's linked user
        if api_key_record.persona_id and api_key_record.persona_id.user_ids:
            # Use the first user linked to the persona
            persona_user = api_key_record.persona_id.user_ids[0]
            request.uid = persona_user.id
        else:
            # Fallback to admin if no user is linked
            request.uid = request.env.ref('base.user_admin').id
            _logger.warning(f"API key {api_key_record.name} has no linked user, using admin")
        
        # Update API key usage statistics
        api_key_record.increment_usage()
        
        # Log successful authentication
        _logger.info(
            f"API access: {endpoint} [{http_method}] "
            f"Key: {api_key_record.name} "
            f"Persona: {api_key_record.persona_id.name} "
            f"IP: {ip_address}"
        )
        
        # Execute the actual API endpoint
        try:
            response = func(self, *args, **kwargs)
            response_time = time.time() - start_time
            
            # Determine status code from response
            status_code = 200
            error_message = None
            
            if isinstance(response, dict):
                status_code = response.get('code', 200)
                if not response.get('success', True):
                    error_message = response.get('error', 'Unknown error')
            
            # Create audit log entry
            request.env['ops.audit.log'].sudo().log_api_request(
                api_key_id=api_key_record.id,
                endpoint=endpoint,
                http_method=http_method,
                ip_address=ip_address,
                user_agent=user_agent,
                status_code=status_code,
                response_time=response_time,
                error_message=error_message
            )
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            
            _logger.error(f"API Error in {endpoint}: {str(e)}", exc_info=True)
            
            # Log the error
            request.env['ops.audit.log'].sudo().log_api_request(
                api_key_id=api_key_record.id,
                endpoint=endpoint,
                http_method=http_method,
                ip_address=ip_address,
                user_agent=user_agent,
                status_code=500,
                response_time=response_time,
                error_message=str(e)
            )
            
            return {
                'success': False,
                'error': str(e),
                'code': 500,
                'timestamp': datetime.now().isoformat()
            }
    
    return wrapper


def validate_api_key(func):
    """
    DEPRECATED: Use authenticate_api_key instead
    
    Legacy decorator for backward compatibility
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        _logger.warning(f"Using deprecated validate_api_key decorator in {func.__name__}. Use authenticate_api_key instead.")
        return authenticate_api_key(func)(self, *args, **kwargs)
    
    return wrapper


def rate_limit(max_calls=1000, period=3600):
    """
    Decorator for rate limiting API calls
    Default: 1000 calls per hour
    
    Note: This is a simplified implementation.
    For production, use Redis or dedicated rate limiting service.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            user_id = request.uid
            cache_key = f'api_rate_limit_{user_id}_{int(time.time() / period)}'
            
            # Get user's rate limit setting (default 1000)
            user = request.env['res.users'].browse(user_id)
            user_limit = user.ops_api_rate_limit or max_calls
            
            # Simple in-memory counter (replace with Redis in production)
            if not hasattr(request, '_api_call_counts'):
                request._api_call_counts = {}
            
            current_count = request._api_call_counts.get(cache_key, 0)
            
            if current_count >= user_limit:
                return {
                    'success': False,
                    'error': _('Rate limit exceeded. Maximum %s calls per hour.') % user_limit,
                    'code': 429,
                    'retry_after': period - (int(time.time()) % period)
                }
            
            # Increment counter
            request._api_call_counts[cache_key] = current_count + 1
            
            # Add rate limit headers to response
            response = func(self, *args, **kwargs)
            if isinstance(response, dict):
                response['_rate_limit_remaining'] = user_limit - current_count - 1
                response['_rate_limit_limit'] = user_limit
            
            return response
        
        return wrapper
    return decorator


def handle_exceptions(func):
    """
    Decorator for consistent exception handling
    Catches and formats all exceptions into standardized error responses
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            _logger.error(f"API Error in {func.__name__}: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'code': 500,
                'timestamp': datetime.now().isoformat()
            }
    
    return wrapper


# ============================================================================
# MAIN API CONTROLLER
# ============================================================================

class OpsMatrixAPI(http.Controller):
    """
    OPS Matrix REST API v1
    
    Base URL: /api/v1/ops_matrix
    Authentication: API Key in X-API-Key header
    Format: JSON
    
    All endpoints return:
    {
        "success": true/false,
        "data": {...},
        "error": "error message" (if success=false)
    }
    """
    
    # ========================================================================
    # UTILITY ENDPOINTS
    # ========================================================================
    
    @http.route('/api/v1/ops_matrix/health', type='json', auth='none', 
                methods=['GET', 'POST'], csrf=False)
    @handle_exceptions
    def health_check(self):
        """
        Health check endpoint - no authentication required
        
        Returns system status and version information
        
        Example Response:
        {
            "status": "healthy",
            "version": "1.0",
            "timestamp": "2025-12-27T14:00:00",
            "database": "mz-db"
        }
        """
        return {
            'status': 'healthy',
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'database': request.env.cr.dbname,
            'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @http.route('/api/v1/ops_matrix/me', type='json', auth='none', 
                methods=['GET', 'POST'], csrf=False)
    @validate_api_key
    @handle_exceptions
    def get_current_user(self):
        """
        Get current authenticated user information
        
        Returns user details, permissions, and allowed branches/BUs
        
        Example Response:
        {
            "success": true,
            "data": {
                "id": 5,
                "name": "John Doe",
                "email": "john@example.com",
                "allowed_branches": [...],
                "allowed_business_units": [...]
            }
        }
        """
        user = request.env.user
        
        data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'login': user.login,
            'company': {
                'id': user.company_id.id,
                'name': user.company_id.name
            },
            'allowed_branches': [
                {
                    'id': branch.id,
                    'name': branch.name,
                    'code': branch.code
                } for branch in user.ops_allowed_branch_ids
            ],
            'allowed_business_units': [
                {
                    'id': bu.id,
                    'name': bu.name,
                    'code': bu.code
                } for bu in user.ops_allowed_business_unit_ids
            ],
            'groups': [group.name for group in user.group_ids],
            'is_admin': user.has_group('base.group_system')
        }
        
        return {
            'success': True,
            'data': data
        }
    
    # ========================================================================
    # BRANCH ENDPOINTS
    # ========================================================================
    
    @http.route('/api/v1/ops_matrix/branches', type='json', auth='none', 
                methods=['POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=1000, period=3600)
    @handle_exceptions
    def list_branches(self, **kwargs):
        """
        List all branches accessible to the current user
        
        Request Body (all optional):
        {
            "filters": [["active", "=", true]],  # Odoo domain filters
            "limit": 100,                        # Max records to return
            "offset": 0,                         # Pagination offset
            "fields": ["name", "code", "manager_id"]  # Fields to return
        }
        
        Response:
        {
            "success": true,
            "data": [...],
            "count": 10,
            "total": 50
        }
        """
        domain = kwargs.get('filters', [])
        limit = min(kwargs.get('limit', 100), 1000)  # Max 1000 records
        offset = kwargs.get('offset', 0)
        fields = kwargs.get('fields', ['id', 'name', 'code', 'active', 'manager_id'])
        
        # Apply user's security restrictions automatically
        branches = request.env['ops.branch'].search_read(
            domain=domain,
            fields=fields,
            limit=limit,
            offset=offset,
            order='name'
        )
        
        total_count = request.env['ops.branch'].search_count(domain)
        
        return {
            'success': True,
            'data': branches,
            'count': len(branches),
            'total': total_count,
            'limit': limit,
            'offset': offset
        }
    
    @http.route('/api/v1/ops_matrix/branches/<int:branch_id>', type='json', 
                auth='none', methods=['GET', 'POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=1000, period=3600)
    @handle_exceptions
    def get_branch(self, branch_id):
        """
        Get detailed information about a specific branch
        
        Path Parameter:
        - branch_id: Branch ID to retrieve
        
        Response:
        {
            "success": true,
            "data": {
                "id": 1,
                "name": "Main Branch",
                "code": "MB001",
                "manager_id": [5, "John Doe"],
                "business_units": [...]
            }
        }
        """
        branch = request.env['ops.branch'].browse(branch_id)
        
        if not branch.exists():
            return {
                'success': False,
                'error': _('Branch with ID %s not found') % branch_id,
                'code': 404
            }
        
        # Check user has access (security rules apply automatically)
        try:
            branch.check_access_rights('read')
            branch.check_access_rule('read')
        except Exception as e:
            return {
                'success': False,
                'error': _('Access denied to this branch'),
                'code': 403
            }
        
        data = {
            'id': branch.id,
            'name': branch.name,
            'code': branch.code,
            'active': branch.active,
            'manager_id': [branch.manager_id.id, branch.manager_id.name] if branch.manager_id else None,
            'company_id': [branch.company_id.id, branch.company_id.name],
            'address': branch.address if hasattr(branch, 'address') else None,
            'phone': branch.phone if hasattr(branch, 'phone') else None,
            'email': branch.email if hasattr(branch, 'email') else None,
            'business_units': [
                {
                    'id': bu.id,
                    'name': bu.name,
                    'code': bu.code,
                    'active': bu.active
                } for bu in branch.business_unit_ids
            ],
            'create_date': branch.create_date.isoformat() if branch.create_date else None,
            'write_date': branch.write_date.isoformat() if branch.write_date else None
        }
        
        return {
            'success': True,
            'data': data
        }
    
    # ========================================================================
    # BUSINESS UNIT ENDPOINTS
    # ========================================================================
    
    @http.route('/api/v1/ops_matrix/business_units', type='json', auth='none', 
                methods=['POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=1000, period=3600)
    @handle_exceptions
    def list_business_units(self, **kwargs):
        """
        List all business units accessible to the current user
        
        Request Body (all optional):
        {
            "filters": [["active", "=", true]],
            "limit": 100,
            "offset": 0,
            "fields": ["name", "code", "ops_branch_id"]
        }
        
        Response:
        {
            "success": true,
            "data": [...],
            "count": 15
        }
        """
        domain = kwargs.get('filters', [])
        limit = min(kwargs.get('limit', 100), 1000)
        offset = kwargs.get('offset', 0)
        fields = kwargs.get('fields', ['id', 'name', 'code', 'ops_branch_id', 'active'])
        
        bus = request.env['ops.business.unit'].search_read(
            domain=domain,
            fields=fields,
            limit=limit,
            offset=offset,
            order='name'
        )
        
        total_count = request.env['ops.business.unit'].search_count(domain)
        
        return {
            'success': True,
            'data': bus,
            'count': len(bus),
            'total': total_count
        }
    
    @http.route('/api/v1/ops_matrix/business_units/<int:bu_id>', type='json', 
                auth='none', methods=['GET', 'POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=1000, period=3600)
    @handle_exceptions
    def get_business_unit(self, bu_id):
        """
        Get detailed information about a specific business unit
        """
        bu = request.env['ops.business.unit'].browse(bu_id)
        
        if not bu.exists():
            return {
                'success': False,
                'error': _('Business Unit with ID %s not found') % bu_id,
                'code': 404
            }
        
        try:
            bu.check_access_rights('read')
            bu.check_access_rule('read')
        except Exception:
            return {
                'success': False,
                'error': _('Access denied to this business unit'),
                'code': 403
            }
        
        data = {
            'id': bu.id,
            'name': bu.name,
            'code': bu.code,
            'active': bu.active,
            'ops_branch_id': [bu.ops_branch_id.id, bu.ops_branch_id.name] if bu.ops_branch_id else None,
            'manager_id': [bu.manager_id.id, bu.manager_id.name] if bu.manager_id else None,
            'create_date': bu.create_date.isoformat() if bu.create_date else None
        }
        
        return {
            'success': True,
            'data': data
        }
    
    # ========================================================================
    # SALES ANALYSIS ENDPOINTS
    # ========================================================================
    
    @http.route('/api/v1/ops_matrix/sales_analysis', type='json', auth='none', 
                methods=['POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=500, period=3600)
    @handle_exceptions
    def query_sales_data(self, **kwargs):
        """
        Query sales analysis data with filters and aggregations
        
        Request Body:
        {
            "date_from": "2025-01-01",
            "date_to": "2025-12-31",
            "branch_ids": [1, 2, 3],
            "bu_ids": [5, 6],
            "group_by": ["ops_branch_id", "product_category_id"],
            "fields": ["total_amount", "total_qty"],
            "limit": 100
        }
        
        Response:
        {
            "success": true,
            "data": [...],
            "aggregations": {
                "total_revenue": 1000000,
                "total_orders": 500
            }
        }
        """
        domain = []
        
        # Date filters
        if kwargs.get('date_from'):
            domain.append(('date_order', '>=', kwargs['date_from']))
        if kwargs.get('date_to'):
            domain.append(('date_order', '<=', kwargs['date_to']))
        
        # Branch filter
        if kwargs.get('branch_ids'):
            domain.append(('ops_branch_id', 'in', kwargs['branch_ids']))
        
        # BU filter
        if kwargs.get('bu_ids'):
            domain.append(('ops_business_unit_id', 'in', kwargs['bu_ids']))
        
        # State filter (default to confirmed orders only)
        if kwargs.get('state'):
            domain.append(('state', '=', kwargs['state']))
        else:
            domain.append(('state', 'in', ['sale', 'done']))
        
        # Get data from sale.order model
        SaleOrder = request.env['sale.order']
        
        if kwargs.get('group_by'):
            # Aggregated data
            fields = kwargs.get('fields', ['amount_total:sum', 'id:count'])
            data = SaleOrder.read_group(
                domain=domain,
                fields=fields,
                groupby=kwargs['group_by'],
                limit=kwargs.get('limit', 100)
            )
        else:
            # Detailed records
            fields = kwargs.get('fields', ['name', 'date_order', 'partner_id', 'amount_total', 'state'])
            data = SaleOrder.search_read(
                domain=domain,
                fields=fields,
                limit=kwargs.get('limit', 100),
                offset=kwargs.get('offset', 0),
                order='date_order desc'
            )
        
        # Calculate overall aggregations
        all_orders = SaleOrder.search(domain)
        aggregations = {
            'total_revenue': sum(all_orders.mapped('amount_total')),
            'total_orders': len(all_orders),
            'average_order_value': sum(all_orders.mapped('amount_total')) / len(all_orders) if all_orders else 0
        }
        
        return {
            'success': True,
            'data': data,
            'count': len(data),
            'aggregations': aggregations,
            'filters_applied': {
                'date_from': kwargs.get('date_from'),
                'date_to': kwargs.get('date_to'),
                'branches': kwargs.get('branch_ids'),
                'business_units': kwargs.get('bu_ids')
            }
        }
    
    # ========================================================================
    # APPROVAL REQUEST ENDPOINTS
    # ========================================================================
    
    @http.route('/api/v1/ops_matrix/approval_requests', type='json', auth='none', 
                methods=['POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=500, period=3600)
    @handle_exceptions
    def list_approval_requests(self, **kwargs):
        """
        List approval requests for current user
        
        Request Body (optional):
        {
            "state": "pending",  # pending, approved, rejected
            "approval_type": "sale_order",
            "limit": 50
        }
        """
        domain = []
        
        # Filter by state
        if kwargs.get('state'):
            domain.append(('state', '=', kwargs['state']))
        
        # Filter by approval type
        if kwargs.get('approval_type'):
            domain.append(('approval_type', '=', kwargs['approval_type']))
        
        # Only show requests where user is an approver
        domain.append(('approver_ids', 'in', [request.uid]))
        
        ApprovalRequest = request.env['ops.approval.request']
        
        fields = ['id', 'name', 'state', 'approval_type', 'priority', 
                  'create_date', 'approver_ids']
        
        requests_data = ApprovalRequest.search_read(
            domain=domain,
            fields=fields,
            limit=kwargs.get('limit', 50),
            order='create_date desc'
        )
        
        return {
            'success': True,
            'data': requests_data,
            'count': len(requests_data)
        }
    
    @http.route('/api/v1/ops_matrix/approval_requests/<int:approval_id>', 
                type='json', auth='none', methods=['GET', 'POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=1000, period=3600)
    @handle_exceptions
    def get_approval_status(self, approval_id):
        """
        Get detailed status of an approval request
        
        Response includes approval history and current approvers
        """
        approval = request.env['ops.approval.request'].browse(approval_id)
        
        if not approval.exists():
            return {
                'success': False,
                'error': _('Approval request %s not found') % approval_id,
                'code': 404
            }
        
        try:
            approval.check_access_rights('read')
            approval.check_access_rule('read')
        except Exception:
            return {
                'success': False,
                'error': _('Access denied'),
                'code': 403
            }
        
        data = {
            'id': approval.id,
            'name': approval.name,
            'state': approval.state,
            'approval_type': approval.approval_type,
            'priority': approval.priority,
            'create_date': approval.create_date.isoformat(),
            'approvers': [
                {
                    'id': approver.id,
                    'name': approver.name,
                    'email': approver.email
                } for approver in approval.approver_ids
            ],
            'notes': approval.notes if hasattr(approval, 'notes') else None
        }
        
        return {
            'success': True,
            'data': data
        }
    
    @http.route('/api/v1/ops_matrix/approval_requests/<int:approval_id>/approve', 
                type='json', auth='none', methods=['POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=500, period=3600)
    @handle_exceptions
    def approve_request(self, approval_id, **kwargs):
        """
        Approve an approval request
        
        Request Body (optional):
        {
            "notes": "Approved with conditions..."
        }
        
        Response:
        {
            "success": true,
            "message": "Approval request approved successfully"
        }
        """
        approval = request.env['ops.approval.request'].browse(approval_id)
        
        if not approval.exists():
            return {
                'success': False,
                'error': _('Approval request not found'),
                'code': 404
            }
        
        # Check user is an approver
        current_user = request.env.user
        if current_user not in approval.approver_ids:
            return {
                'success': False,
                'error': 'You are not authorized to approve this request',
                'code': 403
            }
        
        # Approve
        try:
            approval.action_approve()
            
            # Add notes if provided
            if kwargs.get('notes'):
                approval.message_post(
                    body=kwargs['notes'],
                    subject='Approval via API'
                )
            
            return {
                'success': True,
                'message': _('Approval request approved successfully'),
                'data': {
                    'id': approval.id,
                    'state': approval.state
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': _('Failed to approve request: %s') % str(e),
                'code': 400
            }
    
    @http.route('/api/v1/ops_matrix/approval_requests/<int:approval_id>/reject', 
                type='json', auth='none', methods=['POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=500, period=3600)
    @handle_exceptions
    def reject_request(self, approval_id, **kwargs):
        """
        Reject an approval request
        
        Request Body:
        {
            "reason": "Does not meet criteria..."  # Required
        }
        """
        if not kwargs.get('reason'):
            return {
                'success': False,
                'error': _('Rejection reason is required'),
                'code': 400
            }
        
        approval = request.env['ops.approval.request'].browse(approval_id)
        
        if not approval.exists():
            return {
                'success': False,
                'error': _('Approval request not found'),
                'code': 404
            }
        
        current_user = request.env.user
        if current_user not in approval.approver_ids:
            return {
                'success': False,
                'error': _('You are not authorized to reject this request'),
                'code': 403
            }
        
        try:
            approval.action_reject()
            approval.message_post(
                body=f"Rejected via API: {kwargs['reason']}",
                subject='Rejection via API'
            )
            
            return {
                'success': True,
                'message': _('Approval request rejected'),
                'data': {
                    'id': approval.id,
                    'state': approval.state
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': _('Failed to reject request: %s') % str(e),
                'code': 400
            }
    
    # ========================================================================
    # INVENTORY/STOCK ENDPOINTS
    # ========================================================================
    
    @http.route('/api/v1/ops_matrix/stock_levels', type='json', auth='none', 
                methods=['POST'], csrf=False)
    @validate_api_key
    @rate_limit(max_calls=500, period=3600)
    @handle_exceptions
    def query_stock_levels(self, **kwargs):
        """
        Query current stock levels by branch/warehouse
        
        Request Body:
        {
            "branch_ids": [1, 2],
            "product_ids": [10, 20, 30],
            "limit": 100
        }
        
        Response:
        {
            "success": true,
            "data": [
                {
                    "product_id": [10, "Product A"],
                    "warehouse_id": [1, "Main Warehouse"],
                    "quantity_on_hand": 150.0,
                    "reserved_quantity": 20.0,
                    "available_quantity": 130.0
                }
            ]
        }
        """
        domain = []
        
        # Filter by branches
        if kwargs.get('branch_ids'):
            warehouses = request.env['stock.warehouse'].search([
                ('ops_branch_id', 'in', kwargs['branch_ids'])
            ])
            location_ids = warehouses.mapped('lot_stock_id').ids
            domain.append(('location_id', 'in', location_ids))
        
        # Filter by products
        if kwargs.get('product_ids'):
            domain.append(('product_id', 'in', kwargs['product_ids']))
        
        # Get stock quants
        quants = request.env['stock.quant'].search_read(
            domain=domain,
            fields=['product_id', 'location_id', 'quantity', 'reserved_quantity'],
            limit=kwargs.get('limit', 100)
        )
        
        # Format response
        data = []
        for quant in quants:
            data.append({
                'product_id': quant['product_id'],
                'location_id': quant['location_id'],
                'quantity_on_hand': quant['quantity'],
                'reserved_quantity': quant['reserved_quantity'],
                'available_quantity': quant['quantity'] - quant['reserved_quantity']
            })
        
        return {
            'success': True,
            'data': data,
            'count': len(data)
        }
