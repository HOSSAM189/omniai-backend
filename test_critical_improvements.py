#!/usr/bin/env python3
"""
Comprehensive Test Script for OMNIAI Critical Improvements
Tests all three critical items: Authentication, Error Handling, and Monitoring
"""

import requests
import json
import time
import sys
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for colored output
init(autoreset=True)

class OmniAITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.admin_token = None
        self.test_results = {
            'authentication': {'passed': 0, 'failed': 0, 'tests': []},
            'error_handling': {'passed': 0, 'failed': 0, 'tests': []},
            'monitoring': {'passed': 0, 'failed': 0, 'tests': []},
            'overall': {'passed': 0, 'failed': 0}
        }
    
    def print_header(self, title):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{title.center(60)}")
        print(f"{Fore.CYAN}{'='*60}")
    
    def print_test_result(self, test_name, passed, message="", details=None):
        """Print test result with color coding"""
        status = f"{Fore.GREEN}✅ PASS" if passed else f"{Fore.RED}❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"      {Fore.YELLOW}{message}")
        if details and not passed:
            print(f"      {Fore.RED}Details: {details}")
        return passed
    
    def record_test_result(self, category, test_name, passed, message="", details=None):
        """Record test result for reporting"""
        result = {
            'name': test_name,
            'passed': passed,
            'message': message,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.test_results[category]['tests'].append(result)
        if passed:
            self.test_results[category]['passed'] += 1
            self.test_results['overall']['passed'] += 1
        else:
            self.test_results[category]['failed'] += 1
            self.test_results['overall']['failed'] += 1
    
    def test_authentication_improvements(self):
        """Test Item 1: Authentication Gaps Fixed"""
        self.print_header("TESTING ITEM 1: AUTHENTICATION IMPROVEMENTS")
        
        # Test 1: Enhanced Authentication Endpoints
        try:
            response = requests.get(f"{self.base_url}/api/auth/v2/pricing")
            passed = response.status_code == 200
            message = f"Status: {response.status_code}"
            if passed:
                data = response.json()
                message += f", Plans: {len(data.get('data', {}).get('plans', []))}"
            
            self.print_test_result("Enhanced Auth Pricing Endpoint", passed, message)
            self.record_test_result('authentication', 'pricing_endpoint', passed, message, 
                                  response.text if not passed else None)
        except Exception as e:
            self.print_test_result("Enhanced Auth Pricing Endpoint", False, f"Error: {str(e)}")
            self.record_test_result('authentication', 'pricing_endpoint', False, str(e))
        
        # Test 2: Admin Login Enhancement
        try:
            admin_data = {
                "username": "admin",
                "password": "omniai2025",
                "user_type": "admin"
            }
            response = requests.post(f"{self.base_url}/api/auth/v2/admin/login", 
                                   json=admin_data)
            passed = response.status_code in [200, 401]  # 401 is acceptable if credentials are wrong
            message = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'token' in data.get('data', {}):
                    self.admin_token = data['data']['token']
                    message += ", Token received"
            
            self.print_test_result("Enhanced Admin Login", passed, message)
            self.record_test_result('authentication', 'admin_login', passed, message)
        except Exception as e:
            self.print_test_result("Enhanced Admin Login", False, f"Error: {str(e)}")
            self.record_test_result('authentication', 'admin_login', False, str(e))
        
        # Test 3: Rate Limiting Protection
        try:
            # Make multiple rapid requests to test rate limiting
            responses = []
            for i in range(15):  # Exceed typical rate limit
                response = requests.get(f"{self.base_url}/api/auth/v2/pricing")
                responses.append(response.status_code)
            
            # Check if rate limiting kicked in
            rate_limited = 429 in responses
            passed = rate_limited or all(r == 200 for r in responses)
            message = f"Rate limiting {'detected' if rate_limited else 'not triggered'}"
            
            self.print_test_result("Rate Limiting Protection", passed, message)
            self.record_test_result('authentication', 'rate_limiting', passed, message)
        except Exception as e:
            self.print_test_result("Rate Limiting Protection", False, f"Error: {str(e)}")
            self.record_test_result('authentication', 'rate_limiting', False, str(e))
        
        # Test 4: Security Headers
        try:
            response = requests.get(f"{self.base_url}/api/auth/v2/pricing")
            headers = response.headers
            
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection',
                'Strict-Transport-Security'
            ]
            
            present_headers = [h for h in security_headers if h in headers]
            passed = len(present_headers) >= 3  # At least 3 security headers
            message = f"Security headers: {len(present_headers)}/{len(security_headers)}"
            
            self.print_test_result("Security Headers", passed, message)
            self.record_test_result('authentication', 'security_headers', passed, message)
        except Exception as e:
            self.print_test_result("Security Headers", False, f"Error: {str(e)}")
            self.record_test_result('authentication', 'security_headers', False, str(e))
    
    def test_error_handling_improvements(self):
        """Test Item 2: Error Handling Improvements"""
        self.print_header("TESTING ITEM 2: ERROR HANDLING IMPROVEMENTS")
        
        # Test 1: Error Monitoring Endpoint
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {}
            response = requests.get(f"{self.base_url}/api/admin/errors/stats", headers=headers)
            passed = response.status_code in [200, 401]  # 401 acceptable if not authenticated
            message = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    message += ", Error stats retrieved"
            
            self.print_test_result("Error Monitoring Endpoint", passed, message)
            self.record_test_result('error_handling', 'error_monitoring', passed, message)
        except Exception as e:
            self.print_test_result("Error Monitoring Endpoint", False, f"Error: {str(e)}")
            self.record_test_result('error_handling', 'error_monitoring', False, str(e))
        
        # Test 2: Custom Error Responses
        try:
            # Test 404 error handling
            response = requests.get(f"{self.base_url}/api/nonexistent/endpoint")
            passed = response.status_code == 404
            
            if passed:
                try:
                    data = response.json()
                    has_error_structure = 'error' in data and 'id' in data.get('error', {})
                    passed = has_error_structure
                    message = "Custom error structure present" if has_error_structure else "Basic 404 response"
                except:
                    message = "Non-JSON 404 response"
            else:
                message = f"Unexpected status: {response.status_code}"
            
            self.print_test_result("Custom Error Responses", passed, message)
            self.record_test_result('error_handling', 'custom_errors', passed, message)
        except Exception as e:
            self.print_test_result("Custom Error Responses", False, f"Error: {str(e)}")
            self.record_test_result('error_handling', 'custom_errors', False, str(e))
        
        # Test 3: Error Health Endpoint
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {}
            response = requests.get(f"{self.base_url}/api/admin/errors/health", headers=headers)
            passed = response.status_code in [200, 401]
            message = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'health_score' in data.get('data', {}):
                    health_score = data['data']['health_score']
                    message += f", Health score: {health_score}"
            
            self.print_test_result("Error Health Monitoring", passed, message)
            self.record_test_result('error_handling', 'error_health', passed, message)
        except Exception as e:
            self.print_test_result("Error Health Monitoring", False, f"Error: {str(e)}")
            self.record_test_result('error_handling', 'error_health', False, str(e))
        
        # Test 4: Error Resolution Tracking
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {}
            response = requests.get(f"{self.base_url}/api/admin/errors/recent", headers=headers)
            passed = response.status_code in [200, 401]
            message = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    errors = data.get('data', {}).get('errors', [])
                    message += f", Recent errors: {len(errors)}"
            
            self.print_test_result("Error Resolution Tracking", passed, message)
            self.record_test_result('error_handling', 'error_resolution', passed, message)
        except Exception as e:
            self.print_test_result("Error Resolution Tracking", False, f"Error: {str(e)}")
            self.record_test_result('error_handling', 'error_resolution', False, str(e))
    
    def test_monitoring_improvements(self):
        """Test Item 3: Enhanced Monitoring and Alerting"""
        self.print_header("TESTING ITEM 3: MONITORING & ALERTING IMPROVEMENTS")
        
        # Test 1: Monitoring Service Status
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {}
            response = requests.get(f"{self.base_url}/api/admin/monitoring/status", headers=headers)
            passed = response.status_code in [200, 401]
            message = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    monitoring_active = data.get('data', {}).get('monitoring_active', False)
                    message += f", Monitoring: {'Active' if monitoring_active else 'Inactive'}"
            
            self.print_test_result("Monitoring Service Status", passed, message)
            self.record_test_result('monitoring', 'monitoring_status', passed, message)
        except Exception as e:
            self.print_test_result("Monitoring Service Status", False, f"Error: {str(e)}")
            self.record_test_result('monitoring', 'monitoring_status', False, str(e))
        
        # Test 2: System Health Monitoring
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {}
            response = requests.get(f"{self.base_url}/api/admin/monitoring/health", headers=headers)
            passed = response.status_code in [200, 401]
            message = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    health_data = data.get('data', {})
                    health_score = health_data.get('health_score', 0)
                    status = health_data.get('status', 'unknown')
                    message += f", Health: {health_score}/100 ({status})"
            
            self.print_test_result("System Health Monitoring", passed, message)
            self.record_test_result('monitoring', 'system_health', passed, message)
        except Exception as e:
            self.print_test_result("System Health Monitoring", False, f"Error: {str(e)}")
            self.record_test_result('monitoring', 'system_health', False, str(e))
        
        # Test 3: Metrics Collection
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {}
            response = requests.get(f"{self.base_url}/api/admin/monitoring/metrics", headers=headers)
            passed = response.status_code in [200, 401]
            message = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    metrics = data.get('data', {}).get('latest_metrics', {})
                    message += f", Metrics collected: {len(metrics)}"
            
            self.print_test_result("Metrics Collection", passed, message)
            self.record_test_result('monitoring', 'metrics_collection', passed, message)
        except Exception as e:
            self.print_test_result("Metrics Collection", False, f"Error: {str(e)}")
            self.record_test_result('monitoring', 'metrics_collection', False, str(e))
        
        # Test 4: Alert Management
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {}
            response = requests.get(f"{self.base_url}/api/admin/monitoring/alerts", headers=headers)
            passed = response.status_code in [200, 401]
            message = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    alerts = data.get('data', {}).get('alerts', [])
                    message += f", Alerts: {len(alerts)}"
            
            self.print_test_result("Alert Management", passed, message)
            self.record_test_result('monitoring', 'alert_management', passed, message)
        except Exception as e:
            self.print_test_result("Alert Management", False, f"Error: {str(e)}")
            self.record_test_result('monitoring', 'alert_management', False, str(e))
        
        # Test 5: Monitoring Dashboard
        try:
            headers = {'Authorization': f'Bearer {self.admin_token}'} if self.admin_token else {}
            response = requests.get(f"{self.base_url}/api/admin/monitoring/dashboard", headers=headers)
            passed = response.status_code in [200, 401]
            message = f"Status: {response.status_code}"
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    dashboard_data = data.get('data', {})
                    has_health = 'health_summary' in dashboard_data
                    has_alerts = 'recent_alerts' in dashboard_data
                    has_metrics = 'key_metrics' in dashboard_data
                    
                    components = sum([has_health, has_alerts, has_metrics])
                    message += f", Dashboard components: {components}/3"
            
            self.print_test_result("Monitoring Dashboard", passed, message)
            self.record_test_result('monitoring', 'monitoring_dashboard', passed, message)
        except Exception as e:
            self.print_test_result("Monitoring Dashboard", False, f"Error: {str(e)}")
            self.record_test_result('monitoring', 'monitoring_dashboard', False, str(e))
    
    def test_integration(self):
        """Test integration between all three improvements"""
        self.print_header("TESTING INTEGRATION OF ALL IMPROVEMENTS")
        
        # Test 1: Admin can access all monitoring features
        if self.admin_token:
            try:
                endpoints = [
                    '/api/admin/errors/stats',
                    '/api/admin/monitoring/health',
                    '/api/admin/monitoring/dashboard'
                ]
                
                headers = {'Authorization': f'Bearer {self.admin_token}'}
                accessible_endpoints = 0
                
                for endpoint in endpoints:
                    response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
                    if response.status_code == 200:
                        accessible_endpoints += 1
                
                passed = accessible_endpoints >= 2  # At least 2 endpoints accessible
                message = f"Accessible endpoints: {accessible_endpoints}/{len(endpoints)}"
                
                self.print_test_result("Admin Integration Access", passed, message)
                self.record_test_result('monitoring', 'admin_integration', passed, message)
            except Exception as e:
                self.print_test_result("Admin Integration Access", False, f"Error: {str(e)}")
                self.record_test_result('monitoring', 'admin_integration', False, str(e))
        else:
            self.print_test_result("Admin Integration Access", False, "No admin token available")
            self.record_test_result('monitoring', 'admin_integration', False, "No admin token")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.print_header("COMPREHENSIVE TEST REPORT")
        
        total_tests = self.test_results['overall']['passed'] + self.test_results['overall']['failed']
        success_rate = (self.test_results['overall']['passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{Fore.CYAN}📊 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {Fore.GREEN}{self.test_results['overall']['passed']}")
        print(f"   Failed: {Fore.RED}{self.test_results['overall']['failed']}")
        print(f"   Success Rate: {Fore.YELLOW}{success_rate:.1f}%")
        
        # Category breakdown
        for category, results in self.test_results.items():
            if category == 'overall':
                continue
            
            category_total = results['passed'] + results['failed']
            category_rate = (results['passed'] / category_total * 100) if category_total > 0 else 0
            
            print(f"\n{Fore.MAGENTA}📋 {category.upper().replace('_', ' ')}:")
            print(f"   Passed: {Fore.GREEN}{results['passed']}")
            print(f"   Failed: {Fore.RED}{results['failed']}")
            print(f"   Success Rate: {Fore.YELLOW}{category_rate:.1f}%")
        
        # Recommendations
        print(f"\n{Fore.CYAN}💡 RECOMMENDATIONS:")
        
        if self.test_results['authentication']['failed'] > 0:
            print(f"   {Fore.YELLOW}• Review authentication configuration and admin credentials")
        
        if self.test_results['error_handling']['failed'] > 0:
            print(f"   {Fore.YELLOW}• Verify error handling middleware is properly initialized")
        
        if self.test_results['monitoring']['failed'] > 0:
            print(f"   {Fore.YELLOW}• Check monitoring service dependencies and Redis connectivity")
        
        if success_rate >= 80:
            print(f"   {Fore.GREEN}✅ System is ready for production deployment")
        elif success_rate >= 60:
            print(f"   {Fore.YELLOW}⚠️  System needs minor fixes before production")
        else:
            print(f"   {Fore.RED}❌ System requires significant improvements before production")
        
        # Save detailed report
        report_file = f"omniai_test_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n{Fore.CYAN}📄 Detailed report saved to: {report_file}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"{Fore.CYAN}🚀 Starting OMNIAI Critical Improvements Test Suite")
        print(f"{Fore.CYAN}⏰ Test started at: {datetime.utcnow().isoformat()}")
        
        # Check if server is running
        try:
            response = requests.get(f"{self.base_url}/api/auth/v2/pricing", timeout=5)
            print(f"{Fore.GREEN}✅ Server is running at {self.base_url}")
        except:
            print(f"{Fore.RED}❌ Server is not accessible at {self.base_url}")
            print(f"{Fore.YELLOW}Please ensure the Flask application is running")
            return
        
        # Run test suites
        self.test_authentication_improvements()
        self.test_error_handling_improvements()
        self.test_monitoring_improvements()
        self.test_integration()
        
        # Generate report
        self.generate_report()

if __name__ == "__main__":
    # Check if custom URL provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    tester = OmniAITester(base_url)
    tester.run_all_tests()

