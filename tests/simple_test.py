#!/usr/bin/env python3
"""
Simple test to verify the limit parameter
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from my_app import create_app

def test_simple():
    app = create_app()
    
    with app.test_client() as client:
        # Simulate vendor login
        with client.session_transaction() as sess:
            sess['vendor_id'] = 1
        
        # Test with limit
        response = client.post('/api/filter-products', 
                              json={'limit': 5},
                              content_type='application/json')
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Found {len(data)} products with limit=5")
        else:
            print(f"❌ Error: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_simple()
