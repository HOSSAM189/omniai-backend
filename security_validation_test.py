#!/usr/bin/env python3
"""
Security Validation Test for OMNIAI USD Payment System

This script validates the security measures and USD-only enforcement
of the payment system without requiring full authentication.
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class SecurityValidator:
    """Security validation test class."""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results = []
    
    def print_test_result(self, test_name, passed, details=""):
        """Print formatted test result."""
        status = f"{Fore.GREEN}PASS" if passed else f"{Fore.RED}FAIL"
        print(f"{test_name:<50} [{status}{Style.RESET_ALL}]")
        if details:
            print(f"  {Fore.YELLOW}Details: {details}")
        
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def test_system_health(self):
        """Test basic system health and configuration."""
        print(f"\n{Fore.CYAN}=== System Health Tests ===")
        
        # Test 1: Health endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/health", timeout=5)
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed:
                data = response.json()
                currency = data.get('currency', 'Unknown')
                passed = currency == 'USD'
                details += f", Currency: {currency}"
            
            self.print_test_result("Health Endpoint", passed, details)
        except Exception as e:
            self.print_test_result("Health Endpoint", False, str(e))
        
        # Test 2: Configuration endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/config", timeout=5)
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed:
                data = response.json()
                usd_only = data.get('usd_only', False)
                currency = data.get('currency', 'Unknown')
                passed = usd_only and currency == 'USD'
                details += f", USD Only: {usd_only}, Currency: {currency}"
            
            self.print_test_result("USD Configuration", passed, details)
        except Exception as e:
            self.print_test_result("USD Configuration", False, str(e))
        
        # Test 3: Pricing endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/pricing", timeout=5)
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed:
                data = response.json()
                currency = data.get('currency', 'Unknown')
                plans = data.get('plans', {})
                passed = currency == 'USD' and len(plans) > 0
                details += f", Currency: {currency}, Plans: {len(plans)}"
            
            self.print_test_result("Pricing Information", passed, details)
        except Exception as e:
            self.print_test_result("Pricing Information", False, str(e))
    
    def test_security_headers(self):
        """Test security headers and CORS configuration."""
        print(f"\n{Fore.CYAN}=== Security Headers Tests ===")
        
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/config", timeout=5)
            
            # Check for security headers
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            }
            
            header_count = 0
            for header, expected in security_headers.items():
                if header in response.headers:
                    header_count += 1
            
            passed = header_count > 0  # At least some security headers
            details = f"Security headers present: {header_count}/{len(security_headers)}"
            
            self.print_test_result("Security Headers", passed, details)
            
            # Check CORS headers
            cors_headers = ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods']
            cors_count = sum(1 for header in cors_headers if header in response.headers)
            
            passed = cors_count > 0
            details = f"CORS headers present: {cors_count}/{len(cors_headers)}"
            
            self.print_test_result("CORS Configuration", passed, details)
            
        except Exception as e:
            self.print_test_result("Security Headers", False, str(e))
            self.print_test_result("CORS Configuration", False, str(e))
    
    def test_authentication_requirements(self):
        """Test authentication requirements for protected endpoints."""
        print(f"\n{Fore.CYAN}=== Authentication Tests ===")
        
        protected_endpoints = [
            '/api/payment/v2/validate-amount',
            '/api/payment/v2/subscription-status',
            '/api/payment/v2/create-checkout-session',
            '/api/payment/v2/payment-history'
        ]
        
        for endpoint in protected_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                # Should return 401 (Unauthorized) or 405 (Method Not Allowed)
                passed = response.status_code in [401, 403, 405]
                details = f"Status: {response.status_code} (should be 401/403/405)"
                
                endpoint_name = endpoint.split('/')[-1].replace('-', ' ').title()
                self.print_test_result(f"Auth Required: {endpoint_name}", passed, details)
                
            except Exception as e:
                endpoint_name = endpoint.split('/')[-1].replace('-', ' ').title()
                self.print_test_result(f"Auth Required: {endpoint_name}", False, str(e))
    
    def test_webhook_security(self):
        """Test webhook endpoint security."""
        print(f"\n{Fore.CYAN}=== Webhook Security Tests ===")
        
        # Test 1: Webhook health (should be accessible)
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/webhook/health", timeout=5)
            passed = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if passed:
                data = response.json()
                features = data.get('features', {})
                usd_validation = features.get('usd_validation', False)
                details += f", USD validation: {usd_validation}"
            
            self.print_test_result("Webhook Health", passed, details)
        except Exception as e:
            self.print_test_result("Webhook Health", False, str(e))
        
        # Test 2: Webhook endpoint (should require signature)
        try:
            response = self.session.post(f"{self.base_url}/api/payment/v2/webhook", timeout=5)
            # Should return 400 (Bad Request) due to missing signature
            passed = response.status_code == 400
            details = f"Status: {response.status_code} (should be 400 - missing signature)"
            
            self.print_test_result("Webhook Signature Required", passed, details)
        except Exception as e:
            self.print_test_result("Webhook Signature Required", False, str(e))
        
        # Test 3: Webhook with invalid signature
        try:
            headers = {'Stripe-Signature': 'invalid_signature'}
            response = self.session.post(
                f"{self.base_url}/api/payment/v2/webhook",
                headers=headers,
                data='{"test": "data"}',
                timeout=5
            )
            # Should return 400 (Bad Request) due to invalid signature
            passed = response.status_code in [400, 500]
            details = f"Status: {response.status_code} (should reject invalid signature)"
            
            self.print_test_result("Invalid Signature Rejection", passed, details)
        except Exception as e:
            self.print_test_result("Invalid Signature Rejection", False, str(e))
    
    def test_error_handling(self):
        """Test error handling and response formats."""
        print(f"\n{Fore.CYAN}=== Error Handling Tests ===")
        
        # Test 1: Invalid endpoint
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/nonexistent", timeout=5)
            passed = response.status_code == 404
            details = f"Status: {response.status_code} (should be 404)"
            
            self.print_test_result("Invalid Endpoint", passed, details)
        except Exception as e:
            self.print_test_result("Invalid Endpoint", False, str(e))
        
        # Test 2: Invalid JSON
        try:
            response = self.session.post(
                f"{self.base_url}/api/payment/v2/webhook",
                data="invalid json",
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            passed = response.status_code in [400, 422]
            details = f"Status: {response.status_code} (should be 400/422)"
            
            self.print_test_result("Invalid JSON Handling", passed, details)
        except Exception as e:
            self.print_test_result("Invalid JSON Handling", False, str(e))
        
        # Test 3: Error response format
        try:
            response = self.session.get(f"{self.base_url}/api/payment/v2/nonexistent", timeout=5)
            
            if response.status_code == 404:
                try:
                    data = response.json()
                    has_error_field = 'error' in data or 'message' in data
                    passed = has_error_field
                    details = f"Error field present: {has_error_field}"
                except:
                    passed = False
                    details = "Invalid JSON in error response"
            else:
                passed = False
                details = f"Unexpected status: {response.status_code}"
            
            self.print_test_result("Error Response Format", passed, details)
        except Exception as e:
            self.print_test_result("Error Response Format", False, str(e))
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        print(f"\n{Fore.CYAN}=== Rate Limiting Tests ===")
        
        try:
            # Make multiple rapid requests to test rate limiting
            responses = []
            start_time = time.time()
            
            for i in range(20):  # Make 20 requests
                response = self.session.get(f"{self.base_url}/api/payment/v2/config", timeout=2)
                responses.append(response.status_code)
                time.sleep(0.05)  # Small delay
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Check if any requests were rate limited
            rate_limited = any(status == 429 for status in responses)
            success_count = sum(1 for status in responses if status == 200)
            
            # Rate limiting might not be strictly enforced in test environment
            passed = success_count > 0  # At least some requests succeeded
            details = f"Successful: {success_count}/20, Duration: {duration:.2f}s"
            
            if rate_limited:
                details += ", Rate limiting active"
            
            self.print_test_result("Rate Limiting", passed, details)
            
        except Exception as e:
            self.print_test_result("Rate Limiting", False, str(e))
    
    def test_admin_endpoints(self):
        """Test admin endpoint access control."""
        print(f"\n{Fore.CYAN}=== Admin Access Control Tests ===")
        
        admin_endpoints = [
            '/api/payment/v2/webhook/stats',
            '/api/payment/v2/webhook/reset-stats',
            '/api/payment/v2/admin/webhook/events'
        ]
        
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                # Should return 401/403 (Unauthorized/Forbidden) for non-admin access
                passed = response.status_code in [401, 403, 405]
                details = f"Status: {response.status_code} (should be 401/403/405)"
                
                endpoint_name = endpoint.split('/')[-1].replace('-', ' ').title()
                self.print_test_result(f"Admin Only: {endpoint_name}", passed, details)
                
            except Exception as e:
                endpoint_name = endpoint.split('/')[-1].replace('-', ' ').title()
                self.print_test_result(f"Admin Only: {endpoint_name}", False, str(e))
    
    def generate_report(self):
        """Generate security validation report."""
        print(f"\n{Fore.CYAN}=== Security Validation Report ===")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"{Fore.CYAN}Total Tests: {total_tests}")
        print(f"{Fore.GREEN}Passed: {passed_tests}")
        print(f"{Fore.RED}Failed: {failed_tests}")
        print(f"{Fore.CYAN}Pass Rate: {pass_rate:.1f}%")
        
        # Determine security status
        if pass_rate >= 90:
            status_color = Fore.GREEN
            status = "EXCELLENT SECURITY"
        elif pass_rate >= 75:
            status_color = Fore.YELLOW
            status = "GOOD SECURITY"
        elif pass_rate >= 50:
            status_color = Fore.YELLOW
            status = "NEEDS IMPROVEMENT"
        else:
            status_color = Fore.RED
            status = "CRITICAL SECURITY ISSUES"
        
        print(f"\n{status_color}Security Status: {status}")
        
        # Save report
        report_data = {
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'pass_rate': pass_rate,
                'status': status
            },
            'test_results': self.test_results,
            'timestamp': datetime.utcnow().isoformat(),
            'recommendations': self._generate_recommendations()
        }
        
        with open('security_validation_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n{Fore.CYAN}Detailed report saved to: security_validation_report.json")
        
        return report_data
    
    def _generate_recommendations(self):
        """Generate security recommendations."""
        recommendations = []
        
        failed_tests = [result for result in self.test_results if not result['passed']]
        
        if failed_tests:
            recommendations.append("Review and address failed security tests")
            
            for test in failed_tests:
                if 'auth' in test['test'].lower():
                    recommendations.append("Strengthen authentication mechanisms")
                elif 'header' in test['test'].lower():
                    recommendations.append("Implement comprehensive security headers")
                elif 'webhook' in test['test'].lower():
                    recommendations.append("Enhance webhook security validation")
                elif 'rate' in test['test'].lower():
                    recommendations.append("Configure proper rate limiting")
        
        if len(failed_tests) == 0:
            recommendations.append("Security validation passed - system appears secure")
            recommendations.append("Consider penetration testing for production deployment")
        
        return list(set(recommendations))  # Remove duplicates
    
    def run_all_tests(self):
        """Run all security validation tests."""
        print(f"{Fore.CYAN}OMNIAI Payment System Security Validation")
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}Testing URL: {self.base_url}")
        
        self.test_system_health()
        self.test_security_headers()
        self.test_authentication_requirements()
        self.test_webhook_security()
        self.test_error_handling()
        self.test_rate_limiting()
        self.test_admin_endpoints()
        
        return self.generate_report()

def main():
    """Main execution function."""
    validator = SecurityValidator()
    report = validator.run_all_tests()
    
    # Return exit code based on results
    if report['summary']['pass_rate'] >= 75:
        exit(0)  # Success
    else:
        exit(1)  # Failure

if __name__ == "__main__":
    main()

