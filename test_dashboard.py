#!/usr/bin/env python3
"""
Test the vendor dashboard route with updated template
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from my_app import create_app
from my_app.db import init_db

def test_vendor_dashboard():
    app = create_app()
    init_db()
    
    with app.test_client() as client:
        # Simulate vendor login
        with client.session_transaction() as sess:
            sess['vendor_id'] = 1
            sess['vendor_name'] = 'Test Vendor'
        
        # Test the vendor dashboard route
        response = client.get('/vendor/dashboard')
        
        if response.status_code == 200:
            print("✅ Vendor dashboard loads successfully!")
            
            # Check if categories are being passed to template
            html_content = response.get_data(as_text=True)
            
            # Look for evidence of dynamic categories in the HTML
            if 'All Categories' in html_content:
                print("✅ Category filter is present in template")
            
            if 'budget-product-grid' in html_content:
                print("✅ Budget products grid is present")
                
            return True
        else:
            print(f"❌ Dashboard failed with status {response.status_code}")
            return False

if __name__ == "__main__":
    test_vendor_dashboard()
