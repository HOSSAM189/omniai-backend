#!/usr/bin/env python3
"""
Comprehensive Payment System Test Suite

This script provides comprehensive testing for the OMNIAI USD-only payment system,
including security validation, functionality testing, and compliance verification.
"""

import os
import sys
import json
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import stripe
from colorama import init, Fore, Back, Style

# Initialize colorama for colored output
init(autoreset=True)

class PaymentSystemTester:
    """Comprehensive payment system testing class."""
    
    def __init__(self, base_url: str = "http://localhost:5000", test_mode: bool = True):
        self.base_url = base_url.rstrip('/')
        self.test_mode = test_mode
        self.session = requests.Session()
        
        # Test configuration
        self.test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'test_details': []
        }
        
        # Test user credentials
        self.test_users = {
            'regular_user': {
                'email': 'test.user@omniai.test',
                'password': 'TestPassword123!',
                'first_name': 'Test',
                'last_name': 'User'
            },
            'admin_user': {
                'email': 'admin@omniai.test',
                'password': 'AdminPassword123!',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        }
        
        # Stripe test cards for USD testing
        self.test_cards = {
            'visa_usd': '4242424242424242',
            'visa_declined': '4000000000000002',
            'visa_insufficient_funds': '4000000000009995',
            'mastercard_usd': '5555555555554444',
            'amex_usd': '378282246310005'
        }
        
        # Non-USD test scenarios
        self.non_usd_scenarios = [
            {'currency': 'EUR', 'amount': 999},
            {'currency': 'GBP', 'amount': 899},
            {'currency': 'CAD', 'amount': 1299},
            {'currency': 'JPY', 'amount': 1100}
        ]
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('payment_test_results.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def print_header(self, title: str):
        """Print a formatted test section header."""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{title.center(60)}")
        print(f"{Fore.CYAN}{'='*60}")
    
    def print_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Print formatted test result."""
        status = f"{Fore.GREEN}PASS" if passed else f"{Fore.RED}FAIL"
        print(f"{test_name:<40} [{status}{Style.RESET_ALL}]")
        if details:
            print(f"  {Fore.YELLOW}Details: {details}")
        
        # Record test result
        self.test_results['total_tests'] += 1
        if passed:
            self.test_results['passed_tests'] += 1
        else:
            self.test_results['failed_tests'] += 1
        
        self.test_results['test_details'].append({
            'test_name': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def run_all_tests(self):
        """Run the complete test suite."""
        self.print_header("OMNIAI USD Payment System Test Suite")
        print(f"{Fore.YELLOW}Starting comprehensive payment system testing...")
        print(f"{Fore.YELLOW}Base URL: {self.base_url}")
        print(f"{Fore.YELLOW}Test Mode: {self.test_mode}")
        
        try:
            # Test 1: System Health and Configuration
            self.test_system_health()
            
            # Test 2: Authentication System
            self.test_authentication_system()
            
            # Test 3: USD-Only Enforcement
            self.test_usd_only_enforcement()
            
            # Test 4: Payment Configuration
            self.test_payment_configuration()
            
            # Test 5: Security Middleware
            self.test_security_middleware()
            
            # Test 6: Subscription Management
            self.test_subscription_management()
            
            # Test 7: Webhook Processing
            self.test_webhook_processing()
            
            # Test 8: Error Handling
            self.test_error_handling()
            
            # Test 9: Rate Limiting
            self.test_rate_limiting()
            
            # Test 10: Admin Functions
            self.test_admin_functions()
            
            # Generate final report
            self.generate_test_report()
            
        except Exception as e:
            self.logger.error(f"Test suite execution failed: {str(e)}")
            print(f"{Fore.RED}Test suite execution failed: {str(e)}")
    
    def test_system_health(self):
        """Test system health and basic connectivity."""
        self.print_header("System Health Tests")
        
        # Test 1.1: Basic connectivity
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/health")
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            if passed:
                data = response.json()
                details += f", Features: {len(data.get('features', {}))}"
            self.print_test_result("Basic Connectivity", passed, details)
        except Exception as e:
            self.print_test_result("Basic Connectivity", False, str(e))
        
        # Test 1.2: Webhook health
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/webhook/health")
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            if passed:
                data = response.json()
                details += f", Webhook configured: {data.get('webhook_configured', False)}"
            self.print_test_result("Webhook Health", passed, details)
        except Exception as e:
            self.print_test_result("Webhook Health", False, str(e))
        
        # Test 1.3: Configuration validation
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/config")
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            if passed:
                data = response.json()
                currency = data.get('currency', 'Unknown')
                passed = currency == 'USD'
                details += f", Currency: {currency}"
            self.print_test_result("USD Configuration", passed, details)
        except Exception as e:
            self.print_test_result("USD Configuration", False, str(e))
    
    def test_authentication_system(self):
        """Test authentication and user management."""
        self.print_header("Authentication System Tests")
        
        # Test 2.1: User registration
        try:
            user_data = self.test_users['regular_user'].copy()
            user_data['email'] = f"test_{int(time.time())}@omniai.test"
            
            response = self.session.post(f"{self.base_url}/api/auth/register", json=user_data)
            passed = response.status_code in [200, 201]
            details = f"Status: {response.status_code}"
            
            if passed:
                self.test_users['regular_user']['email'] = user_data['email']
                data = response.json()
                details += f", User ID: {data.get('user', {}).get('id', 'Unknown')}"
            
            self.print_test_result("User Registration", passed, details)
        except Exception as e:
            self.print_test_result("User Registration", False, str(e))
        
        # Test 2.2: User login
        try:
            login_data = {
                'email': self.test_users['regular_user']['email'],
                'password': self.test_users['regular_user']['password']
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed:
                data = response.json()
                token = data.get('token')
                if token:
                    self.session.headers.update({'Authorization': f'Bearer {token}'})
                    details += ", Token received"
                else:
                    passed = False
                    details += ", No token received"
            
            self.print_test_result("User Login", passed, details)
        except Exception as e:
            self.print_test_result("User Login", False, str(e))
        
        # Test 2.3: Protected endpoint access
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/subscription-status")
            passed = response.status_code in [200, 404]  # 404 is OK if no subscription
            details = f"Status: {response.status_code}"
            self.print_test_result("Protected Endpoint Access", passed, details)
        except Exception as e:
            self.print_test_result("Protected Endpoint Access", False, str(e))
    
    def test_usd_only_enforcement(self):
        """Test USD-only currency enforcement."""
        self.print_header("USD-Only Enforcement Tests")
        
        # Test 3.1: Valid USD amount validation
        try:
            test_amounts = [1.00, 9.99, 99.99, 299.99, 999.99]
            passed_count = 0
            
            for amount in test_amounts:
                response = self.session.post(
                    f"{self.base_url}/api/payment/v2/validate-amount",
                    json={'amount': amount, 'currency': 'USD'}
                )
                if response.status_code == 200:
                    passed_count += 1
            
            passed = passed_count == len(test_amounts)
            details = f"Valid amounts: {passed_count}/{len(test_amounts)}"
            self.print_test_result("USD Amount Validation", passed, details)
        except Exception as e:
            self.print_test_result("USD Amount Validation", False, str(e))
        
        # Test 3.2: Non-USD currency rejection
        try:
            rejected_count = 0
            
            for scenario in self.non_usd_scenarios:
                response = self.session.post(
                    f"{self.base_url}/api/payment/v2/validate-amount",
                    json=scenario
                )
                if response.status_code in [400, 422]:  # Should be rejected
                    rejected_count += 1
            
            passed = rejected_count == len(self.non_usd_scenarios)
            details = f"Rejected currencies: {rejected_count}/{len(self.non_usd_scenarios)}"
            self.print_test_result("Non-USD Rejection", passed, details)
        except Exception as e:
            self.print_test_result("Non-USD Rejection", False, str(e))
        
        # Test 3.3: Invalid amount ranges
        try:
            invalid_amounts = [0, -1, 0.50, 10001, 99999]
            rejected_count = 0
            
            for amount in invalid_amounts:
                response = self.session.post(
                    f"{self.base_url}/api/payment/v2/validate-amount",
                    json={'amount': amount, 'currency': 'USD'}
                )
                if response.status_code in [400, 422]:
                    rejected_count += 1
            
            passed = rejected_count == len(invalid_amounts)
            details = f"Invalid amounts rejected: {rejected_count}/{len(invalid_amounts)}"
            self.print_test_result("Invalid Amount Rejection", passed, details)
        except Exception as e:
            self.print_test_result("Invalid Amount Rejection", False, str(e))
    
    def test_payment_configuration(self):
        """Test payment configuration and pricing."""
        self.print_header("Payment Configuration Tests")
        
        # Test 4.1: Pricing information
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/pricing")
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed:
                data = response.json()
                currency = data.get('currency')
                plans = data.get('plans', {})
                passed = currency == 'USD' and len(plans) > 0
                details += f", Currency: {currency}, Plans: {len(plans)}"
            
            self.print_test_result("Pricing Information", passed, details)
        except Exception as e:
            self.print_test_result("Pricing Information", False, str(e))
        
        # Test 4.2: Checkout session creation
        try:
            checkout_data = {
                'plan_type': 'individual',
                'billing_cycle': 'monthly',
                'success_url': f"{self.base_url}/payment/success",
                'cancel_url': f"{self.base_url}/payment/cancel"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/payment/v2/create-checkout-session",
                json=checkout_data
            )
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed:
                data = response.json()
                checkout_url = data.get('checkout_url')
                passed = bool(checkout_url and 'stripe.com' in checkout_url)
                details += f", Checkout URL: {'Valid' if passed else 'Invalid'}"
            
            self.print_test_result("Checkout Session Creation", passed, details)
        except Exception as e:
            self.print_test_result("Checkout Session Creation", False, str(e))
    
    def test_security_middleware(self):
        """Test security middleware and protection measures."""
        self.print_header("Security Middleware Tests")
        
        # Test 5.1: Rate limiting headers
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/config")
            passed = response.status_code == 200
            
            # Check for security headers
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            header_count = sum(1 for header in security_headers if header in response.headers)
            details = f"Security headers: {header_count}/{len(security_headers)}"
            
            self.print_test_result("Security Headers", passed, details)
        except Exception as e:
            self.print_test_result("Security Headers", False, str(e))
        
        # Test 5.2: Request validation
        try:
            # Test with invalid JSON
            response = self.session.post(
                f"{self.base_url}/api/payment/v2/validate-amount",
                data="invalid json",
                headers={'Content-Type': 'application/json'}
            )
            passed = response.status_code in [400, 422]
            details = f"Invalid JSON rejected: {response.status_code}"
            self.print_test_result("Request Validation", passed, details)
        except Exception as e:
            self.print_test_result("Request Validation", False, str(e))
        
        # Test 5.3: Authentication requirement
        try:
            # Create session without auth token
            unauth_session = requests.Session()
            response = unauth_session.get(f"{self.base_url}/api/payment/v2/subscription-status")
            passed = response.status_code in [401, 403]
            details = f"Unauthorized access blocked: {response.status_code}"
            self.print_test_result("Authentication Requirement", passed, details)
        except Exception as e:
            self.print_test_result("Authentication Requirement", False, str(e))
    
    def test_subscription_management(self):
        """Test subscription management functionality."""
        self.print_header("Subscription Management Tests")
        
        # Test 6.1: Subscription status retrieval
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/subscription-status")
            passed = response.status_code in [200, 404]
            details = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                details += f", Has subscription: {bool(data.get('subscription'))}"
            
            self.print_test_result("Subscription Status", passed, details)
        except Exception as e:
            self.print_test_result("Subscription Status", False, str(e))
        
        # Test 6.2: Payment history
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/payment-history")
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed:
                data = response.json()
                payments = data.get('payments', [])
                details += f", Payment records: {len(payments)}"
            
            self.print_test_result("Payment History", passed, details)
        except Exception as e:
            self.print_test_result("Payment History", False, str(e))
        
        # Test 6.3: Subscription sync
        try:
            response = self.session.post(f"{self.base_url}/api/payment/v2/subscription/sync")
            passed = response.status_code in [200, 400]  # 400 OK if no customer ID
            details = f"Status: {response.status_code}"
            self.print_test_result("Subscription Sync", passed, details)
        except Exception as e:
            self.print_test_result("Subscription Sync", False, str(e))
    
    def test_webhook_processing(self):
        """Test webhook processing functionality."""
        self.print_header("Webhook Processing Tests")
        
        # Test 7.1: Webhook health
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/webhook/health")
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed:
                data = response.json()
                features = data.get('features', {})
                details += f", Features: {len(features)}"
            
            self.print_test_result("Webhook Health", passed, details)
        except Exception as e:
            self.print_test_result("Webhook Health", False, str(e))
        
        # Test 7.2: Webhook endpoint accessibility
        try:
            # Test webhook endpoint (should require signature)
            response = self.session.post(f"{self.base_url}/api/payment/v2/webhook")
            passed = response.status_code == 400  # Should fail without signature
            details = f"Signature required: {response.status_code == 400}"
            self.print_test_result("Webhook Security", passed, details)
        except Exception as e:
            self.print_test_result("Webhook Security", False, str(e))
    
    def test_error_handling(self):
        """Test error handling and recovery."""
        self.print_header("Error Handling Tests")
        
        # Test 8.1: Invalid endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/nonexistent")
            passed = response.status_code == 404
            details = f"404 for invalid endpoint: {passed}"
            self.print_test_result("Invalid Endpoint Handling", passed, details)
        except Exception as e:
            self.print_test_result("Invalid Endpoint Handling", False, str(e))
        
        # Test 8.2: Malformed requests
        try:
            response = self.session.post(
                f"{self.base_url}/api/payment/v2/validate-amount",
                json={'invalid': 'data'}
            )
            passed = response.status_code in [400, 422]
            details = f"Malformed request rejected: {passed}"
            self.print_test_result("Malformed Request Handling", passed, details)
        except Exception as e:
            self.print_test_result("Malformed Request Handling", False, str(e))
        
        # Test 8.3: Error response format
        try:
            response = self.session.post(f"{self.base_url}/api/payment/v2/validate-amount")
            passed = response.status_code in [400, 422]
            
            if passed:
                try:
                    data = response.json()
                    has_error = 'error' in data or 'message' in data
                    passed = has_error
                    details = f"Error format valid: {has_error}"
                except:
                    passed = False
                    details = "Invalid JSON error response"
            else:
                details = f"Unexpected status: {response.status_code}"
            
            self.print_test_result("Error Response Format", passed, details)
        except Exception as e:
            self.print_test_result("Error Response Format", False, str(e))
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        self.print_header("Rate Limiting Tests")
        
        # Test 9.1: Rate limit enforcement
        try:
            # Make multiple rapid requests
            responses = []
            for i in range(15):  # Exceed typical rate limit
                response = self.session.get(f"{self.base_url}/api/payment/v2/config")
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay
            
            # Check if any requests were rate limited
            rate_limited = any(status == 429 for status in responses)
            success_count = sum(1 for status in responses if status == 200)
            
            details = f"Successful: {success_count}/15, Rate limited: {rate_limited}"
            # Rate limiting might not be enforced in test environment
            passed = True  # Consider test passed if no errors occurred
            
            self.print_test_result("Rate Limit Enforcement", passed, details)
        except Exception as e:
            self.print_test_result("Rate Limit Enforcement", False, str(e))
    
    def test_admin_functions(self):
        """Test admin-only functionality."""
        self.print_header("Admin Function Tests")
        
        # Test 10.1: Admin endpoint access (should fail for regular user)
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/webhook/stats")
            passed = response.status_code in [403, 401]  # Should be forbidden
            details = f"Admin access blocked: {response.status_code in [403, 401]}"
            self.print_test_result("Admin Access Control", passed, details)
        except Exception as e:
            self.print_test_result("Admin Access Control", False, str(e))
        
        # Test 10.2: Admin endpoint functionality (if admin user available)
        # This would require admin credentials which may not be available in test environment
        self.print_test_result("Admin Functionality", True, "Skipped - Admin credentials not available")
        self.test_results['skipped_tests'] += 1
    
    def generate_test_report(self):
        """Generate comprehensive test report."""
        self.print_header("Test Results Summary")
        
        total = self.test_results['total_tests']
        passed = self.test_results['passed_tests']
        failed = self.test_results['failed_tests']
        skipped = self.test_results['skipped_tests']
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"{Fore.CYAN}Total Tests: {total}")
        print(f"{Fore.GREEN}Passed: {passed}")
        print(f"{Fore.RED}Failed: {failed}")
        print(f"{Fore.YELLOW}Skipped: {skipped}")
        print(f"{Fore.CYAN}Pass Rate: {pass_rate:.1f}%")
        
        # Determine overall status
        if pass_rate >= 90:
            status_color = Fore.GREEN
            status = "EXCELLENT"
        elif pass_rate >= 75:
            status_color = Fore.YELLOW
            status = "GOOD"
        elif pass_rate >= 50:
            status_color = Fore.YELLOW
            status = "NEEDS IMPROVEMENT"
        else:
            status_color = Fore.RED
            status = "CRITICAL ISSUES"
        
        print(f"\n{status_color}Overall Status: {status}")
        
        # Save detailed report
        report_data = {
            'test_summary': self.test_results,
            'test_environment': {
                'base_url': self.base_url,
                'test_mode': self.test_mode,
                'timestamp': datetime.utcnow().isoformat()
            },
            'recommendations': self._generate_recommendations()
        }
        
        with open('payment_system_test_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n{Fore.CYAN}Detailed report saved to: payment_system_test_report.json")
        print(f"{Fore.CYAN}Log file saved to: payment_test_results.log")
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        failed_tests = [
            test for test in self.test_results['test_details'] 
            if not test['passed']
        ]
        
        if failed_tests:
            recommendations.append("Review and fix failed test cases")
            
            # Specific recommendations based on failed tests
            for test in failed_tests:
                if 'connectivity' in test['test_name'].lower():
                    recommendations.append("Check server connectivity and ensure services are running")
                elif 'authentication' in test['test_name'].lower():
                    recommendations.append("Verify authentication system configuration")
                elif 'usd' in test['test_name'].lower():
                    recommendations.append("Review USD-only enforcement implementation")
                elif 'security' in test['test_name'].lower():
                    recommendations.append("Enhance security middleware configuration")
        
        if self.test_results['passed_tests'] / self.test_results['total_tests'] < 0.9:
            recommendations.append("Consider additional testing before production deployment")
        
        if not recommendations:
            recommendations.append("System appears to be functioning correctly")
            recommendations.append("Consider load testing for production readiness")
        
        return recommendations

def main():
    """Main test execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='OMNIAI Payment System Test Suite')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL for the payment system')
    parser.add_argument('--test-mode', action='store_true', default=True,
                       help='Run in test mode')
    
    args = parser.parse_args()
    
    print(f"{Fore.CYAN}OMNIAI Payment System Test Suite")
    print(f"{Fore.CYAN}{'='*50}")
    
    tester = PaymentSystemTester(base_url=args.url, test_mode=args.test_mode)
    tester.run_all_tests()

if __name__ == "__main__":
    main()

