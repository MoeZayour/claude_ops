#!/usr/bin/env python3
"""
OPS Matrix API Test Client
===========================

Simple command-line test client for the OPS Matrix REST API.
Use this to verify API functionality and troubleshoot issues.

Usage:
    python test_api_client.py

Configuration:
    Edit the API_URL and API_KEY constants below.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:8089/api/v1/ops_matrix"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

# ============================================================================
# API CLIENT CLASS
# ============================================================================

class OpsMatrixClient:
    """Simple client for OPS Matrix REST API"""
    
    def __init__(self, base_url: str, api_key: str):
        self.api_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
    
    def request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make API request"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        payload = {"params": params or {}}
        
        try:
            response = requests.request(
                method,
                url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'code': 0
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Invalid JSON response: {str(e)}',
                'code': 0
            }

# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(result: Dict, show_data: bool = True):
    """Print API result"""
    if result.get('success'):
        print("✓ SUCCESS")
        if show_data and 'data' in result:
            print(json.dumps(result['data'], indent=2))
        elif 'message' in result:
            print(f"  Message: {result['message']}")
    else:
        print("✗ FAILED")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        print(f"  Code: {result.get('code', 'N/A')}")

def test_health_check(client: OpsMatrixClient):
    """Test 1: Health Check (No Auth)"""
    print_section("TEST 1: Health Check")
    
    # Make request without auth header
    try:
        response = requests.post(
            f"{client.api_url}/health",
            json={"params": {}},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        result = response.json()
        print_result(result)
        
        if result.get('status') == 'healthy':
            print(f"\n  Version: {result.get('version')}")
            print(f"  Database: {result.get('database')}")
            print(f"  Server Time: {result.get('server_time')}")
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")

def test_authentication(client: OpsMatrixClient):
    """Test 2: Authentication"""
    print_section("TEST 2: Authentication - Get Current User")
    
    result = client.request('POST', '/me')
    print_result(result, show_data=False)
    
    if result.get('success'):
        user = result['data']
        print(f"\n  User ID: {user['id']}")
        print(f"  Name: {user['name']}")
        print(f"  Email: {user['email']}")
        print(f"  Login: {user['login']}")
        print(f"  Is Admin: {user['is_admin']}")
        print(f"  Allowed Branches: {len(user['allowed_branches'])}")
        print(f"  Allowed BUs: {len(user['allowed_business_units'])}")

def test_list_branches(client: OpsMatrixClient):
    """Test 3: List Branches"""
    print_section("TEST 3: List Branches")
    
    result = client.request('POST', '/branches', {
        'limit': 10,
        'filters': [['active', '=', True]]
    })
    
    print_result(result, show_data=False)
    
    if result.get('success'):
        print(f"\n  Found {result['count']} branches (of {result['total']} total)")
        for branch in result['data'][:5]:  # Show first 5
            print(f"    - {branch['name']} ({branch['code']})")
        
        if result['count'] > 5:
            print(f"    ... and {result['count'] - 5} more")

def test_get_branch_details(client: OpsMatrixClient):
    """Test 4: Get Branch Details"""
    print_section("TEST 4: Get Branch Details")
    
    # First get list of branches
    list_result = client.request('POST', '/branches', {'limit': 1})
    
    if not list_result.get('success') or not list_result['data']:
        print("✗ No branches available to test")
        return
    
    branch_id = list_result['data'][0]['id']
    print(f"Testing with Branch ID: {branch_id}")
    
    result = client.request('POST', f'/branches/{branch_id}')
    print_result(result, show_data=False)
    
    if result.get('success'):
        branch = result['data']
        print(f"\n  ID: {branch['id']}")
        print(f"  Name: {branch['name']}")
        print(f"  Code: {branch['code']}")
        print(f"  Company: {branch['company_id'][1] if branch.get('company_id') else 'N/A'}")
        print(f"  Manager: {branch['manager_id'][1] if branch.get('manager_id') else 'N/A'}")
        print(f"  Business Units: {len(branch.get('business_units', []))}")

def test_list_business_units(client: OpsMatrixClient):
    """Test 5: List Business Units"""
    print_section("TEST 5: List Business Units")
    
    result = client.request('POST', '/business_units', {
        'limit': 10,
        'filters': [['active', '=', True]]
    })
    
    print_result(result, show_data=False)
    
    if result.get('success'):
        print(f"\n  Found {result['count']} business units")
        for bu in result['data'][:5]:
            branch_name = bu['ops_branch_id'][1] if bu.get('ops_branch_id') else 'N/A'
            print(f"    - {bu['name']} ({bu['code']}) - Branch: {branch_name}")

def test_sales_analysis(client: OpsMatrixClient):
    """Test 6: Sales Analysis"""
    print_section("TEST 6: Sales Analysis")
    
    # Query last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"Querying sales from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    result = client.request('POST', '/sales_analysis', {
        'date_from': start_date.strftime('%Y-%m-%d'),
        'date_to': end_date.strftime('%Y-%m-%d'),
        'group_by': ['ops_branch_id'],
        'limit': 10
    })
    
    print_result(result, show_data=False)
    
    if result.get('success'):
        agg = result.get('aggregations', {})
        print(f"\n  Total Revenue: ${agg.get('total_revenue', 0):,.2f}")
        print(f"  Total Orders: {agg.get('total_orders', 0)}")
        print(f"  Average Order: ${agg.get('average_order_value', 0):,.2f}")
        
        if result['data']:
            print("\n  By Branch:")
            for item in result['data'][:5]:
                branch = item.get('ops_branch_id', [None, 'Unknown'])
                revenue = item.get('amount_total', 0)
                count = item.get('id_count', 0)
                print(f"    - {branch[1]}: ${revenue:,.2f} ({count} orders)")

def test_approval_requests(client: OpsMatrixClient):
    """Test 7: Approval Requests"""
    print_section("TEST 7: List Approval Requests")
    
    result = client.request('POST', '/approval_requests', {
        'state': 'pending',
        'limit': 10
    })
    
    print_result(result, show_data=False)
    
    if result.get('success'):
        print(f"\n  Found {result['count']} pending approval requests")
        for approval in result['data'][:5]:
            print(f"    - [{approval['id']}] {approval['name']}")
            print(f"      Type: {approval['approval_type']}, Priority: {approval['priority']}")

def test_stock_levels(client: OpsMatrixClient):
    """Test 8: Stock Levels"""
    print_section("TEST 8: Query Stock Levels")
    
    result = client.request('POST', '/stock_levels', {
        'limit': 10
    })
    
    print_result(result, show_data=False)
    
    if result.get('success'):
        print(f"\n  Found {result['count']} stock records")
        for stock in result['data'][:5]:
            product = stock['product_id'][1] if stock.get('product_id') else 'Unknown'
            location = stock['location_id'][1] if stock.get('location_id') else 'Unknown'
            qty = stock.get('quantity_on_hand', 0)
            available = stock.get('available_quantity', 0)
            print(f"    - {product}")
            print(f"      Location: {location}")
            print(f"      On Hand: {qty:.2f}, Available: {available:.2f}")

def test_invalid_endpoint(client: OpsMatrixClient):
    """Test 9: Invalid Endpoint (404)"""
    print_section("TEST 9: Invalid Endpoint (404)")
    
    result = client.request('POST', '/nonexistent_endpoint')
    print_result(result, show_data=False)
    
    # This should fail with 404
    if not result.get('success'):
        print("\n  (This error is expected - testing error handling)")

def test_invalid_api_key():
    """Test 10: Invalid API Key (401)"""
    print_section("TEST 10: Invalid API Key (401)")
    
    bad_client = OpsMatrixClient(API_URL, "invalid_key_12345")
    result = bad_client.request('POST', '/me')
    print_result(result, show_data=False)
    
    # This should fail with 401
    if not result.get('success') and result.get('code') == 401:
        print("\n  (This error is expected - testing authentication)")

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all API tests"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  OPS Matrix REST API - Test Suite".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    print(f"\nAPI URL: {API_URL}")
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:] if len(API_KEY) > 14 else '***'}")
    
    # Initialize client
    client = OpsMatrixClient(API_URL, API_KEY)
    
    # Run tests
    tests = [
        test_health_check,
        test_authentication,
        test_list_branches,
        test_get_branch_details,
        test_list_business_units,
        test_sales_analysis,
        test_approval_requests,
        test_stock_levels,
        test_invalid_endpoint,
        test_invalid_api_key,
    ]
    
    passed = 0
    failed = 0
    
    for i, test_func in enumerate(tests, 1):
        try:
            test_func(client) if test_func != test_invalid_api_key else test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ TEST FAILED WITH EXCEPTION: {str(e)}")
            failed += 1
        
        # Pause between tests
        if i < len(tests):
            print("\nPress Enter to continue to next test...")
            input()
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print(f"  Total Tests: {len(tests)}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print("="*70 + "\n")

# ============================================================================
# INTERACTIVE MENU
# ============================================================================

def show_menu():
    """Show interactive menu"""
    print("\n" + "="*70)
    print("  OPS Matrix API Test Client - Main Menu")
    print("="*70)
    print("  1. Run All Tests")
    print("  2. Test Health Check")
    print("  3. Test Authentication")
    print("  4. Test Branches")
    print("  5. Test Business Units")
    print("  6. Test Sales Analysis")
    print("  7. Test Approvals")
    print("  8. Test Stock Levels")
    print("  9. Test Error Handling")
    print("  0. Exit")
    print("="*70)

def main():
    """Main entry point"""
    # Check if API key is set
    if API_KEY == "YOUR_API_KEY_HERE":
        print("\n" + "!"*70)
        print("  ⚠️  WARNING: API Key Not Configured")
        print("!"*70)
        print("\nPlease edit this file and set your API key:")
        print(f"  1. Open: {__file__}")
        print(f"  2. Find: API_KEY = \"YOUR_API_KEY_HERE\"")
        print(f"  3. Replace with your actual API key")
        print("\nTo generate an API key:")
        print("  1. Go to Odoo: Settings → Users & Companies → Users")
        print("  2. Select a user")
        print("  3. Click 'Generate API Key'")
        print("\n" + "!"*70)
        return
    
    client = OpsMatrixClient(API_URL, API_KEY)
    
    while True:
        show_menu()
        choice = input("\nEnter choice (0-9): ").strip()
        
        if choice == '0':
            print("\nGoodbye!")
            break
        elif choice == '1':
            run_all_tests()
        elif choice == '2':
            test_health_check(client)
        elif choice == '3':
            test_authentication(client)
        elif choice == '4':
            test_list_branches(client)
            test_get_branch_details(client)
        elif choice == '5':
            test_list_business_units(client)
        elif choice == '6':
            test_sales_analysis(client)
        elif choice == '7':
            test_approval_requests(client)
        elif choice == '8':
            test_stock_levels(client)
        elif choice == '9':
            test_invalid_endpoint(client)
            test_invalid_api_key()
        else:
            print("\n✗ Invalid choice. Please enter 0-9.")
        
        if choice != '0':
            input("\nPress Enter to return to menu...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
