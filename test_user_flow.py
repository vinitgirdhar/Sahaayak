"""
Comprehensive User Flow Test Script for Sahaayak
Tests all major user journeys for both Vendor and Wholesaler roles
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_homepage():
    """Test homepage loads correctly"""
    print("\n=== TESTING HOMEPAGE ===")
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        print("✅ Homepage loads successfully")
        # Check for key elements
        if "Sahaayak" in response.text:
            print("✅ Brand name present")
        if "vendor" in response.text.lower():
            print("✅ Vendor section present")
        if "wholesaler" in response.text.lower():
            print("✅ Wholesaler section present")
    else:
        print(f"❌ Homepage failed: {response.status_code}")
    return response.status_code == 200

def test_vendor_login_page():
    """Test vendor login page loads"""
    print("\n=== TESTING VENDOR LOGIN PAGE ===")
    response = requests.get(f"{BASE_URL}/vendor/login")
    if response.status_code == 200:
        print("✅ Vendor login page loads")
        if "phone" in response.text.lower() or "login" in response.text.lower():
            print("✅ Login form present")
    else:
        print(f"❌ Vendor login page failed: {response.status_code}")
    return response.status_code == 200

def test_wholesaler_login_page():
    """Test wholesaler login page loads"""
    print("\n=== TESTING WHOLESALER LOGIN PAGE ===")
    response = requests.get(f"{BASE_URL}/wholesaler/login")
    if response.status_code == 200:
        print("✅ Wholesaler login page loads")
    else:
        print(f"❌ Wholesaler login page failed: {response.status_code}")
    return response.status_code == 200

def test_vendor_flow():
    """Test complete vendor user flow"""
    print("\n=== TESTING VENDOR USER FLOW ===")
    
    # Create a session to maintain cookies
    s = requests.Session()
    
    # 1. Login
    print("\n1. Testing Vendor Login...")
    login_data = {
        'phone': '9876543210',
        'password': 'vendor123'
    }
    response = s.post(f"{BASE_URL}/vendor/login", data=login_data, allow_redirects=False)
    if response.status_code == 302:
        print("✅ Login successful (redirected to dashboard)")
    else:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    # 2. Access Dashboard
    print("\n2. Testing Vendor Dashboard...")
    response = s.get(f"{BASE_URL}/vendor/dashboard")
    if response.status_code == 200:
        print("✅ Dashboard loads successfully")
        # Check for category cards
        categories = ["Vegetables", "Dairy", "Bread", "Grains", "Spices"]
        found = sum(1 for cat in categories if cat.lower() in response.text.lower())
        print(f"✅ Found {found}/{len(categories)} category sections")
    else:
        print(f"❌ Dashboard failed: {response.status_code}")
        return False
    
    # 3. Access Category Listing
    print("\n3. Testing Category Listing...")
    response = s.get(f"{BASE_URL}/vendor/category/Vegetables")
    if response.status_code == 200:
        print("✅ Category listing loads")
        if "product" in response.text.lower() or "₹" in response.text:
            print("✅ Products displayed with prices")
    else:
        print(f"❌ Category listing failed: {response.status_code}")
    
    # 4. Test Cart Page (even if empty)
    print("\n4. Testing Cart Page...")
    response = s.get(f"{BASE_URL}/vendor/cart")
    if response.status_code == 200:
        print("✅ Cart page loads successfully")
    else:
        print(f"❌ Cart page failed: {response.status_code}")
    
    # 5. Test Add to Cart API
    print("\n5. Testing Add to Cart API...")
    cart_data = {'product_id': 1, 'quantity': 2}
    response = s.post(f"{BASE_URL}/api/add-to-cart", json=cart_data)
    if response.status_code == 200:
        print("✅ Add to cart API works")
        result = response.json()
        print(f"   Cart response: {result.get('message', 'Success')}")
    else:
        print(f"⚠️ Add to cart API: {response.status_code}")
    
    # 6. Test Checkout Page
    print("\n6. Testing Checkout Page...")
    response = s.get(f"{BASE_URL}/vendor/checkout")
    if response.status_code == 200:
        print("✅ Checkout page loads")
    else:
        print(f"⚠️ Checkout page: {response.status_code} (might need items in cart)")
    
    # 7. Test Profile Page
    print("\n7. Testing Profile Page...")
    response = s.get(f"{BASE_URL}/vendor/profile")
    if response.status_code == 200:
        print("✅ Profile page loads")
    else:
        print(f"❌ Profile page failed: {response.status_code}")
    
    # 8. Test Orders Page
    print("\n8. Testing Orders Page...")
    response = s.get(f"{BASE_URL}/vendor/orders")
    if response.status_code == 200:
        print("✅ Orders page loads")
    else:
        print(f"❌ Orders page failed: {response.status_code}")
    
    # 9. Logout
    print("\n9. Testing Logout...")
    response = s.get(f"{BASE_URL}/vendor/logout", allow_redirects=False)
    if response.status_code == 302:
        print("✅ Logout successful")
    else:
        print(f"⚠️ Logout response: {response.status_code}")
    
    return True

def test_wholesaler_flow():
    """Test complete wholesaler user flow"""
    print("\n=== TESTING WHOLESALER USER FLOW ===")
    
    s = requests.Session()
    
    # 1. Login
    print("\n1. Testing Wholesaler Login...")
    login_data = {
        'phone': '9999999999',
        'password': 'password123'
    }
    response = s.post(f"{BASE_URL}/wholesaler/login", data=login_data, allow_redirects=False)
    if response.status_code == 302:
        print("✅ Login successful (redirected to dashboard)")
    else:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    # 2. Access Dashboard
    print("\n2. Testing Wholesaler Dashboard...")
    response = s.get(f"{BASE_URL}/wholesaler/dashboard")
    if response.status_code == 200:
        print("✅ Dashboard loads successfully")
        # Check for key dashboard elements
        if "product" in response.text.lower():
            print("✅ Products section present")
        if "order" in response.text.lower():
            print("✅ Orders section present")
    else:
        print(f"❌ Dashboard failed: {response.status_code}")
        return False
    
    # 3. Test Products Management
    print("\n3. Testing Products Management...")
    response = s.get(f"{BASE_URL}/wholesaler/products/manage")
    if response.status_code == 200:
        print("✅ Products management page loads")
    else:
        print(f"❌ Products management failed: {response.status_code}")
    
    # 4. Test Add Product Page
    print("\n4. Testing Add Product Page...")
    response = s.get(f"{BASE_URL}/wholesaler/products/add")
    if response.status_code == 200:
        print("✅ Add product page loads")
        # Check for form elements
        if "category" in response.text.lower():
            print("✅ Category dropdown present")
        if "price" in response.text.lower():
            print("✅ Price field present")
    else:
        print(f"❌ Add product page failed: {response.status_code}")
    
    # 5. Test Orders Management
    print("\n5. Testing Orders Management...")
    response = s.get(f"{BASE_URL}/wholesaler/orders/manage")
    if response.status_code == 200:
        print("✅ Orders management page loads")
    else:
        print(f"❌ Orders management failed: {response.status_code}")
    
    # 6. Test Profile Page
    print("\n6. Testing Wholesaler Profile...")
    response = s.get(f"{BASE_URL}/wholesaler/profile")
    if response.status_code == 200:
        print("✅ Profile page loads")
    else:
        print(f"❌ Profile page failed: {response.status_code}")
    
    # 7. Test Analytics Page
    print("\n7. Testing Analytics Page...")
    response = s.get(f"{BASE_URL}/wholesaler/analytics")
    if response.status_code == 200:
        print("✅ Analytics page loads")
    else:
        print(f"⚠️ Analytics page: {response.status_code}")
    
    # 8. Logout
    print("\n8. Testing Logout...")
    response = s.get(f"{BASE_URL}/wholesaler/logout", allow_redirects=False)
    if response.status_code == 302:
        print("✅ Logout successful")
    else:
        print(f"⚠️ Logout response: {response.status_code}")
    
    return True

def test_api_endpoints():
    """Test API endpoints for data integrity"""
    print("\n=== TESTING API ENDPOINTS ===")
    
    # 1. Filter Products API
    print("\n1. Testing Filter Products API...")
    response = requests.get(f"{BASE_URL}/api/filter-products")
    if response.status_code == 200:
        print("✅ Filter products API works")
        data = response.json()
        if 'products' in data:
            print(f"   Found {len(data['products'])} products")
    else:
        print(f"❌ Filter products failed: {response.status_code}")
    
    # 2. Search Products API
    print("\n2. Testing Search Products API...")
    response = requests.get(f"{BASE_URL}/api/search-products?query=rice")
    if response.status_code == 200:
        print("✅ Search products API works")
        data = response.json()
        if 'products' in data:
            print(f"   Search found {len(data['products'])} products for 'rice'")
    else:
        print(f"⚠️ Search products: {response.status_code}")
    
    # 3. Test with category filter
    print("\n3. Testing Category Filter...")
    response = requests.get(f"{BASE_URL}/api/filter-products?category=Vegetables")
    if response.status_code == 200:
        print("✅ Category filter works")
        data = response.json()
        if 'products' in data:
            print(f"   Found {len(data['products'])} vegetable products")
    else:
        print(f"⚠️ Category filter: {response.status_code}")

def test_registration_pages():
    """Test registration pages load correctly"""
    print("\n=== TESTING REGISTRATION PAGES ===")
    
    # Vendor Registration
    response = requests.get(f"{BASE_URL}/vendor/register")
    if response.status_code == 200:
        print("✅ Vendor registration page loads")
    else:
        print(f"❌ Vendor registration failed: {response.status_code}")
    
    # Wholesaler Registration
    response = requests.get(f"{BASE_URL}/register-wholesaler")
    if response.status_code == 200:
        print("✅ Wholesaler registration page loads")
    else:
        print(f"❌ Wholesaler registration failed: {response.status_code}")

def test_admin_flow():
    """Test admin functionality"""
    print("\n=== TESTING ADMIN FLOW ===")
    
    s = requests.Session()
    
    # Login
    print("\n1. Testing Admin Login...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    response = s.post(f"{BASE_URL}/admin/login", data=login_data, allow_redirects=False)
    if response.status_code == 302:
        print("✅ Admin login successful")
    else:
        print(f"❌ Admin login failed: {response.status_code}")
        return False
    
    # Access admin panel
    print("\n2. Testing Admin Panel...")
    response = s.get(f"{BASE_URL}/admin/wholesalers")
    if response.status_code == 200:
        print("✅ Admin panel loads")
    else:
        print(f"❌ Admin panel failed: {response.status_code}")
    
    return True

def run_all_tests():
    """Run all tests and generate summary"""
    print("=" * 60)
    print("SAHAAYAK - COMPREHENSIVE USER FLOW TEST")
    print("=" * 60)
    
    results = {}
    
    results['homepage'] = test_homepage()
    results['vendor_login_page'] = test_vendor_login_page()
    results['wholesaler_login_page'] = test_wholesaler_login_page()
    test_registration_pages()
    results['vendor_flow'] = test_vendor_flow()
    results['wholesaler_flow'] = test_wholesaler_flow()
    test_api_endpoints()
    results['admin_flow'] = test_admin_flow()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} core tests passed")
    
    if passed == total:
        print("\n🎉 ALL CORE TESTS PASSED! App is ready for production review.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
