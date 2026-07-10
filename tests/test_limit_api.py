#!/usr/bin/env python3
"""
Test script to verify the updated filter API with limit parameter
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from my_app import create_app
from my_app.db import init_db
import json

def test_filter_api_with_limit():
    # Initialize the app and database
    app = create_app()
    init_db()
    
    with app.test_client() as client:
        # Simulate a vendor session
        with client.session_transaction() as sess:
            sess['vendor_id'] = 1
        
        # Test the filter API without limit (should return all products)
        response1 = client.post('/api/filter-products', 
                              json={'maxBudget': '', 'category': 'All Categories', 'sortBy': 'Price Low to High'},
                              content_type='application/json')
        
        # Test the filter API with limit=8
        response2 = client.post('/api/filter-products', 
                              json={'maxBudget': '', 'category': 'All Categories', 'sortBy': 'Price Low to High', 'limit': 8},
                              content_type='application/json')
        
        if response1.status_code == 200 and response2.status_code == 200:
            data1 = response1.get_json()
            data2 = response2.get_json()
            
            print(f"✅ API test passed!")
            print(f"   Without limit: Found {len(data1)} products")
            print(f"   With limit=8: Found {len(data2)} products")
            
            if len(data2) <= 8:
                print(f"✅ Limit parameter working correctly!")
            else:
                print(f"❌ Limit parameter not working - expected ≤8, got {len(data2)}")
                
            return True
        else:
            print(f"❌ API test failed with status {response1.status_code}, {response2.status_code}")
            return False

if __name__ == "__main__":
    test_filter_api_with_limit()
