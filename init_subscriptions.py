#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models.user import db
from src.models.subscription import Subscription
import json

with app.app_context():
    # Check if subscriptions already exist
    existing = Subscription.query.first()
    if existing:
        print('Subscriptions already exist, skipping initialization')
        exit()
    
    # Individual subscription plans
    individual_basic = Subscription(
        name='Individual Basic',
        description='Core AI advisory features for personal use',
        user_type_applicable='individual',
        price_monthly=9.99,
        price_annual=99.99,
        currency='USD',
        features=json.dumps({
            'ai_interactions_per_month': 1000,
            'workflows': 5,
            'support_level': 'standard',
            'mobile_access': True,
            'voice_interaction': False
        }),
        is_active=True
    )
    
    individual_premium = Subscription(
        name='Individual Premium',
        description='Enhanced AI with learning and advanced features',
        user_type_applicable='individual',
        price_monthly=19.99,
        price_annual=199.99,
        currency='USD',
        features=json.dumps({
            'ai_interactions_per_month': 5000,
            'workflows': 25,
            'support_level': 'priority',
            'mobile_access': True,
            'voice_interaction': True,
            'advanced_analytics': True,
            'ai_learning': True
        }),
        is_active=True
    )
    
    individual_pro = Subscription(
        name='Individual Pro',
        description='All premium features with unlimited access',
        user_type_applicable='individual',
        price_monthly=39.99,
        price_annual=399.99,
        currency='USD',
        features=json.dumps({
            'ai_interactions_per_month': -1,  # unlimited
            'workflows': -1,  # unlimited
            'support_level': 'priority',
            'mobile_access': True,
            'voice_interaction': True,
            'advanced_analytics': True,
            'ai_learning': True,
            'api_access': 'limited',
            'custom_integrations': True
        }),
        is_active=True
    )
    
    # Company subscription plans
    company_business = Subscription(
        name='Business Plan',
        description='Multi-user support with enterprise AI advisory',
        user_type_applicable='company',
        price_monthly=49.99,
        price_annual=499.99,
        currency='USD',
        features=json.dumps({
            'max_users': 10,
            'ai_interactions_per_month': 10000,
            'workflows': -1,  # unlimited
            'support_level': 'priority',
            'mobile_access': True,
            'voice_interaction': True,
            'business_analytics': True,
            'enterprise_ai': True
        }),
        is_active=True
    )
    
    company_enterprise = Subscription(
        name='Enterprise Plan',
        description='Full feature access with custom branding',
        user_type_applicable='company',
        price_monthly=99.99,
        price_annual=999.99,
        currency='USD',
        features=json.dumps({
            'max_users': 50,
            'ai_interactions_per_month': 50000,
            'workflows': -1,  # unlimited
            'support_level': 'dedicated',
            'mobile_access': True,
            'voice_interaction': True,
            'business_analytics': True,
            'enterprise_ai': True,
            'custom_branding': True,
            'api_access': 'full',
            'compliance_tools': True
        }),
        is_active=True
    )
    
    company_corporate = Subscription(
        name='Corporate Plan',
        description='Unlimited users with custom deployment options',
        user_type_applicable='company',
        price_monthly=199.99,
        price_annual=1999.99,
        currency='USD',
        features=json.dumps({
            'max_users': -1,  # unlimited
            'ai_interactions_per_month': -1,  # unlimited
            'workflows': -1,  # unlimited
            'support_level': '24/7_dedicated',
            'mobile_access': True,
            'voice_interaction': True,
            'business_analytics': True,
            'enterprise_ai': True,
            'custom_branding': True,
            'api_access': 'full',
            'compliance_tools': True,
            'white_label': True,
            'custom_deployment': True,
            'custom_integrations': True
        }),
        is_active=True
    )
    
    # Add all subscriptions
    subscriptions = [
        individual_basic, individual_premium, individual_pro,
        company_business, company_enterprise, company_corporate
    ]
    
    for sub in subscriptions:
        db.session.add(sub)
    
    db.session.commit()
    print('Successfully created subscription plans')
    
    # Print created subscriptions
    for sub in Subscription.query.all():
        print(f'- {sub.name}: ${sub.price_monthly}/month (${sub.price_annual}/year) for {sub.user_type_applicable}')

