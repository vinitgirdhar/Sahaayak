#!/usr/bin/env python3
"""
Quick test script to verify the new filter-products API endpoint
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from my_app import create_app
from my_app.db import init_db
import json

def test_filter_api():
    # Initialize the app and database
    app = create_app()
    init_db()
    
    with app.test_client() as client:
        # Simulate a vendor session
        with client.session_transaction() as sess:
            sess['vendor_id'] = 1
        
        # Test the filter API
        response = client.post('/api/filter-products', 
                              json={'maxBudget': 50, 'category': 'All Categories', 'sortBy': 'Price Low to High'},
                              content_type='application/json')
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ API test passed! Found {len(data)} products")
            if data:
                print(f"   First product: {data[0]['name']} - ₹{data[0]['price']}")
            return True
        else:
            print(f"❌ API test failed with status {response.status_code}")
            return False

if __name__ == "__main__":
    test_filter_api()
