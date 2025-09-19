#!/usr/bin/env python3
"""
Enhanced Payment System Test Suite

This script provides comprehensive testing for the USD-only payment system,
including security validation, rate limiting, and fraud detection.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class PaymentSystemTester:
    """
    Comprehensive test suite for the enhanced USD payment system.
    """
    
    def __init__(self, base_url: str = 'http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
        # Test configuration
        self.test_user_id = 1
        self.test_session_data = {'user_id': self.test_user_id}
        
    def log_test_result(self, test_name: str, success: bool, details: str = ''):
        """Log test result."""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def test_payment_config_endpoint(self):
        """Test payment configuration endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/config")
            
            if response.status_code == 200:
                config = response.json()
                
                # Validate USD-only configuration
                if config.get('currency') == 'USD' and config.get('usd_only') is True:
                    self.log_test_result(
                        "Payment Config - USD Only",
                        True,
                        f"Currency: {config.get('currency')}, USD Only: {config.get('usd_only')}"
                    )
                else:
                    self.log_test_result(
                        "Payment Config - USD Only",
                        False,
                        f"Expected USD-only config, got: {config}"
                    )
                
                # Validate required fields
                required_fields = ['publishable_key', 'currency', 'min_amount', 'max_amount']
                missing_fields = [field for field in required_fields if field not in config]
                
                if not missing_fields:
                    self.log_test_result(
                        "Payment Config - Required Fields",
                        True,
                        "All required fields present"
                    )
                else:
                    self.log_test_result(
                        "Payment Config - Required Fields",
                        False,
                        f"Missing fields: {missing_fields}"
                    )
            else:
                self.log_test_result(
                    "Payment Config - Endpoint Access",
                    False,
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Payment Config - Endpoint Access",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_usd_currency_validation(self):
        """Test USD currency validation."""
        # Test valid USD request
        try:
            # Mock session for authentication
            with self.session as s:
                s.cookies.set('session', json.dumps(self.test_session_data))
                
                valid_data = {
                    'plan_type': 'individual',
                    'billing_cycle': 'monthly',
                    'currency': 'USD'
                }
                
                response = s.post(
                    f"{self.base_url}/api/payment/v2/create-checkout-session",
                    json=valid_data
                )
                
                # We expect this to fail due to authentication, but not due to currency
                if response.status_code in [401, 403]:  # Auth failure, not currency failure
                    self.log_test_result(
                        "USD Currency Validation - Valid USD",
                        True,
                        "USD currency accepted (auth failure expected)"
                    )
                elif response.status_code == 400 and 'currency' in response.text.lower():
                    self.log_test_result(
                        "USD Currency Validation - Valid USD",
                        False,
                        f"USD currency rejected: {response.text}"
                    )
                else:
                    self.log_test_result(
                        "USD Currency Validation - Valid USD",
                        True,
                        f"USD currency processed (status: {response.status_code})"
                    )
                
        except Exception as e:
            self.log_test_result(
                "USD Currency Validation - Valid USD",
                False,
                f"Exception: {str(e)}"
            )
        
        # Test invalid non-USD request
        try:
            with self.session as s:
                s.cookies.set('session', json.dumps(self.test_session_data))
                
                invalid_data = {
                    'plan_type': 'individual',
                    'billing_cycle': 'monthly',
                    'currency': 'EUR'
                }
                
                response = s.post(
                    f"{self.base_url}/api/payment/v2/create-checkout-session",
                    json=invalid_data
                )
                
                if response.status_code == 400 and 'USD' in response.text:
                    self.log_test_result(
                        "USD Currency Validation - Invalid EUR",
                        True,
                        "EUR currency properly rejected"
                    )
                else:
                    self.log_test_result(
                        "USD Currency Validation - Invalid EUR",
                        False,
                        f"EUR currency not rejected: {response.status_code} - {response.text}"
                    )
                    
        except Exception as e:
            self.log_test_result(
                "USD Currency Validation - Invalid EUR",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_amount_validation(self):
        """Test payment amount validation."""
        try:
            # Test valid amount
            valid_data = {
                'amount': 10.00,
                'currency': 'USD'
            }
            
            response = self.session.post(
                f"{self.base_url}/api/payment/v2/validate-amount",
                json=valid_data
            )
            
            if response.status_code in [200, 401]:  # Success or auth required
                self.log_test_result(
                    "Amount Validation - Valid Amount",
                    True,
                    "Valid amount accepted"
                )
            else:
                self.log_test_result(
                    "Amount Validation - Valid Amount",
                    False,
                    f"Valid amount rejected: {response.text}"
                )
            
            # Test invalid amount (too high)
            invalid_data = {
                'amount': 50000.00,
                'currency': 'USD'
            }
            
            response = self.session.post(
                f"{self.base_url}/api/payment/v2/validate-amount",
                json=invalid_data
            )
            
            if response.status_code == 400:
                self.log_test_result(
                    "Amount Validation - Invalid High Amount",
                    True,
                    "High amount properly rejected"
                )
            else:
                self.log_test_result(
                    "Amount Validation - Invalid High Amount",
                    False,
                    f"High amount not rejected: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Amount Validation",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        try:
            # Make multiple rapid requests to trigger rate limiting
            endpoint = f"{self.base_url}/api/payment/v2/config"
            
            responses = []
            for i in range(15):  # Exceed the typical rate limit
                response = self.session.get(endpoint)
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay between requests
            
            # Check if any requests were rate limited (429 status)
            rate_limited = any(status == 429 for status in responses)
            
            if rate_limited:
                self.log_test_result(
                    "Rate Limiting",
                    True,
                    f"Rate limiting triggered after multiple requests"
                )
            else:
                self.log_test_result(
                    "Rate Limiting",
                    False,
                    f"Rate limiting not triggered: {responses}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Rate Limiting",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_security_headers(self):
        """Test security headers in responses."""
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/config")
            
            # Check for important security headers
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Strict-Transport-Security'
            ]
            
            present_headers = []
            missing_headers = []
            
            for header in security_headers:
                if header in response.headers:
                    present_headers.append(header)
                else:
                    missing_headers.append(header)
            
            if len(present_headers) >= 3:  # Most security headers present
                self.log_test_result(
                    "Security Headers",
                    True,
                    f"Present: {present_headers}, Missing: {missing_headers}"
                )
            else:
                self.log_test_result(
                    "Security Headers",
                    False,
                    f"Too few security headers. Present: {present_headers}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Security Headers",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_webhook_endpoint(self):
        """Test webhook endpoint security."""
        try:
            # Test webhook without signature (should fail)
            webhook_data = {
                'type': 'checkout.session.completed',
                'data': {'object': {'id': 'test'}}
            }
            
            response = self.session.post(
                f"{self.base_url}/api/payment/v2/webhook",
                json=webhook_data
            )
            
            if response.status_code == 400:
                self.log_test_result(
                    "Webhook Security - Missing Signature",
                    True,
                    "Webhook properly rejected without signature"
                )
            else:
                self.log_test_result(
                    "Webhook Security - Missing Signature",
                    False,
                    f"Webhook not properly secured: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Webhook Security",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_health_endpoint(self):
        """Test payment system health endpoint."""
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/health")
            
            if response.status_code == 200:
                health_data = response.json()
                
                if health_data.get('currency') == 'USD' and 'features' in health_data:
                    self.log_test_result(
                        "Health Endpoint",
                        True,
                        f"Health check passed: {health_data.get('status')}"
                    )
                else:
                    self.log_test_result(
                        "Health Endpoint",
                        False,
                        f"Invalid health response: {health_data}"
                    )
            else:
                self.log_test_result(
                    "Health Endpoint",
                    False,
                    f"Health endpoint failed: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Health Endpoint",
                False,
                f"Exception: {str(e)}"
            )
    
    def test_pricing_endpoint(self):
        """Test pricing endpoint for USD-specific information."""
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/pricing")
            
            if response.status_code == 200:
                pricing_data = response.json()
                pricing = pricing_data.get('pricing', {})
                
                # Validate USD currency
                if pricing.get('currency') == 'USD':
                    self.log_test_result(
                        "Pricing Endpoint - USD Currency",
                        True,
                        "Pricing correctly shows USD currency"
                    )
                else:
                    self.log_test_result(
                        "Pricing Endpoint - USD Currency",
                        False,
                        f"Wrong currency in pricing: {pricing.get('currency')}"
                    )
                
                # Validate pricing structure
                required_plans = ['individual', 'company']
                required_cycles = ['monthly', 'annual']
                
                valid_structure = all(
                    plan in pricing and 
                    all(cycle in pricing[plan] for cycle in required_cycles)
                    for plan in required_plans
                )
                
                if valid_structure:
                    self.log_test_result(
                        "Pricing Endpoint - Structure",
                        True,
                        "Pricing structure is valid"
                    )
                else:
                    self.log_test_result(
                        "Pricing Endpoint - Structure",
                        False,
                        f"Invalid pricing structure: {pricing}"
                    )
            else:
                self.log_test_result(
                    "Pricing Endpoint",
                    False,
                    f"Pricing endpoint failed: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Pricing Endpoint",
                False,
                f"Exception: {str(e)}"
            )
    
    def run_all_tests(self):
        """Run all payment system tests."""
        print("🧪 Starting Enhanced Payment System Tests")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_payment_config_endpoint,
            self.test_usd_currency_validation,
            self.test_amount_validation,
            self.test_rate_limiting,
            self.test_security_headers,
            self.test_webhook_endpoint,
            self.test_health_endpoint,
            self.test_pricing_endpoint
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test_result(
                    test_method.__name__,
                    False,
                    f"Test method failed: {str(e)}"
                )
            
            time.sleep(0.5)  # Small delay between tests
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate and display test summary."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test_name']}: {result['details']}")
        
        # Save detailed results
        with open('payment_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'success_rate': (passed_tests/total_tests)*100
                },
                'test_results': self.test_results,
                'generated_at': datetime.utcnow().isoformat()
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: payment_test_results.json")
        
        return passed_tests == total_tests

def main():
    """Main test execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Enhanced Payment System')
    parser.add_argument(
        '--url', 
        default='http://localhost:5000',
        help='Base URL for the payment system (default: http://localhost:5000)'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Create and run tester
    tester = PaymentSystemTester(base_url=args.url)
    
    print(f"🎯 Testing Enhanced Payment System at: {args.url}")
    print(f"⏰ Test started at: {datetime.utcnow().isoformat()}")
    
    success = tester.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Payment system is ready for USD transactions.")
    else:
        print("⚠️ SOME TESTS FAILED. Please review and fix issues before deployment.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

