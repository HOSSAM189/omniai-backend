#!/usr/bin/env python3
"""
USD Payment System Setup Script for OMNIAI

This script helps set up and configure the enhanced USD-only payment system.
It validates configuration, creates necessary database tables, and provides
setup guidance.
"""

import os
import sys
import logging
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging():
    """Set up logging for the setup process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('usd_payment_setup.log')
        ]
    )
    return logging.getLogger(__name__)

def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = '.env'
    env_example = '.env.example'
    
    if not os.path.exists(env_file) and os.path.exists(env_example):
        print("Creating .env file from template...")
        with open(env_example, 'r') as example:
            content = example.read()
        
        with open(env_file, 'w') as env:
            env.write(content)
        
        print("✅ .env file created from template")
        print("⚠️ Please update .env file with your actual Stripe keys and configuration")
        return True
    elif os.path.exists(env_file):
        print("✅ .env file already exists")
        return True
    else:
        print("❌ No .env.example file found to create .env from")
        return False

def load_environment():
    """Load environment variables from .env file."""
    env_file = '.env'
    if os.path.exists(env_file):
        print("Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print("⚠️ No .env file found, using system environment variables")

def validate_configuration():
    """Validate the USD payment configuration."""
    print("\n" + "="*60)
    print("VALIDATING USD PAYMENT CONFIGURATION")
    print("="*60)
    
    try:
        from src.utils.payment_config_validator import PaymentConfigValidator
        
        validator = PaymentConfigValidator()
        results = validator.validate_all()
        
        print(f"Validation Status: {'PASSED' if results['valid'] else 'FAILED'}")
        print(f"Summary: {results['summary']}")
        
        if results['errors']:
            print(f"\n❌ Errors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"   • {error}")
        
        if results['warnings']:
            print(f"\n⚠️ Warnings ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"   • {warning}")
        
        if results['info']:
            print(f"\n✅ Configured ({len(results['info'])}):")
            for info in results['info']:
                print(f"   • {info}")
        
        # Generate setup guide if there are issues
        if results['errors'] or results['warnings']:
            guide_file = 'usd_payment_setup_guide.md'
            with open(guide_file, 'w') as f:
                f.write(validator.generate_setup_guide())
            print(f"\n📋 Setup guide generated: {guide_file}")
        
        return results['valid']
        
    except ImportError as e:
        print(f"❌ Could not import validation module: {e}")
        return False
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def setup_database():
    """Set up database tables for payment system."""
    print("\n" + "="*60)
    print("SETTING UP DATABASE TABLES")
    print("="*60)
    
    try:
        from flask import Flask
        from src.models.user import db
        from src.models.payment import PaymentTransaction
        from src.models.subscription import Subscription
        
        # Create Flask app for database context
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', 
            'sqlite:///database/app.db'
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Create database directory if it doesn't exist
            db_dir = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                print(f"✅ Created database directory: {db_dir}")
            
            # Create all tables
            db.create_all()
            print("✅ Database tables created/updated")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['users', 'payment_transactions', 'subscriptions']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                print(f"⚠️ Missing tables: {missing_tables}")
                return False
            else:
                print(f"✅ All required tables present: {required_tables}")
                return True
                
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_enhanced_services():
    """Test the enhanced payment services."""
    print("\n" + "="*60)
    print("TESTING ENHANCED PAYMENT SERVICES")
    print("="*60)
    
    try:
        from src.services.enhanced_stripe_service import enhanced_stripe_service
        
        # Test service initialization
        config = enhanced_stripe_service.get_payment_config()
        print("✅ Enhanced Stripe service initialized")
        print(f"   Currency: {config['currency']}")
        print(f"   Min Amount: ${config['min_amount']}")
        print(f"   Max Amount: ${config['max_amount']}")
        
        # Test currency validation
        try:
            enhanced_stripe_service.validate_currency('USD')
            print("✅ USD currency validation working")
        except Exception as e:
            print(f"❌ USD currency validation failed: {e}")
            return False
        
        # Test non-USD currency rejection
        try:
            enhanced_stripe_service.validate_currency('EUR')
            print("❌ Non-USD currency validation should have failed")
            return False
        except ValueError:
            print("✅ Non-USD currency properly rejected")
        
        # Test amount validation
        try:
            enhanced_stripe_service.validate_payment_amount(10.00)
            print("✅ Payment amount validation working")
        except Exception as e:
            print(f"❌ Payment amount validation failed: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Could not import enhanced services: {e}")
        return False
    except Exception as e:
        print(f"❌ Service testing failed: {e}")
        return False

def create_test_data():
    """Create test data for development."""
    print("\n" + "="*60)
    print("CREATING TEST DATA")
    print("="*60)
    
    try:
        from flask import Flask
        from src.models.user import db
        from src.models.system_setting import SystemSetting
        
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', 
            'sqlite:///database/app.db'
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Create default pricing settings
            pricing_settings = [
                ('default_individual_plan_monthly', '9.99'),
                ('default_individual_plan_annual', '99.99'),
                ('default_company_plan_monthly', '29.99'),
                ('default_company_plan_annual', '299.99')
            ]
            
            for key, value in pricing_settings:
                setting = SystemSetting.query.filter_by(key=key).first()
                if not setting:
                    setting = SystemSetting(key=key, value=value)
                    db.session.add(setting)
                    print(f"✅ Created pricing setting: {key} = ${value}")
                else:
                    print(f"✅ Pricing setting exists: {key} = ${setting.value}")
            
            db.session.commit()
            print("✅ Test data created successfully")
            return True
            
    except Exception as e:
        print(f"❌ Test data creation failed: {e}")
        return False

def generate_summary_report():
    """Generate a summary report of the setup."""
    print("\n" + "="*60)
    print("SETUP SUMMARY REPORT")
    print("="*60)
    
    report = f"""
# USD Payment System Setup Report
Generated: {datetime.now().isoformat()}

## Setup Status
- Environment Configuration: {'✅' if os.path.exists('.env') else '❌'}
- Database Tables: {'✅' if os.path.exists('database/app.db') else '❌'}
- Enhanced Services: ✅ (if no errors above)

## Next Steps
1. Update .env file with your actual Stripe keys
2. Configure webhook endpoints in Stripe dashboard
3. Test with Stripe test cards
4. Deploy to production environment
5. Switch to live Stripe keys for production

## Important Files
- .env: Environment configuration
- src/services/enhanced_stripe_service.py: Enhanced USD-only service
- src/routes/enhanced_payment.py: Enhanced payment API endpoints
- src/utils/payment_config_validator.py: Configuration validator

## Testing
Use the following test card for USD transactions:
- Card Number: 4242424242424242 (Visa)
- Expiry: Any future date
- CVC: Any 3 digits
- ZIP: Any 5 digits

## Support
For issues, check the setup guide: usd_payment_setup_guide.md
"""
    
    with open('usd_payment_setup_report.md', 'w') as f:
        f.write(report)
    
    print("✅ Setup report generated: usd_payment_setup_report.md")
    print(report)

def main():
    """Main setup function."""
    logger = setup_logging()
    logger.info("Starting USD payment system setup")
    
    print("🚀 OMNIAI USD Payment System Setup")
    print("="*60)
    
    success = True
    
    # Step 1: Create environment file
    if not create_env_file():
        success = False
    
    # Step 2: Load environment
    load_environment()
    
    # Step 3: Validate configuration
    if not validate_configuration():
        print("\n⚠️ Configuration validation failed. Please fix issues before continuing.")
        success = False
    
    # Step 4: Setup database
    if not setup_database():
        success = False
    
    # Step 5: Test enhanced services
    if not test_enhanced_services():
        success = False
    
    # Step 6: Create test data
    if not create_test_data():
        success = False
    
    # Step 7: Generate summary
    generate_summary_report()
    
    print("\n" + "="*60)
    if success:
        print("🎉 USD PAYMENT SYSTEM SETUP COMPLETED SUCCESSFULLY!")
        print("✅ Your OMNIAI application is ready for USD-only payments")
    else:
        print("❌ SETUP COMPLETED WITH ISSUES")
        print("⚠️ Please review the errors above and fix them")
    print("="*60)
    
    logger.info(f"USD payment system setup completed: {'SUCCESS' if success else 'WITH ISSUES'}")
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

