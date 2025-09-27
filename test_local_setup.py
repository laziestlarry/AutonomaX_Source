#!/usr/bin/env python3
"""
Comprehensive local test of your AutonomaX setup
"""

import asyncio
import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    try:
        from apps.api.main import app
        print("✅ API imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_endpoints():
    """Test API endpoint structure"""
    from apps.api.main import app
    endpoints = []
    for route in app.routes:
        if hasattr(route, 'methods'):
            endpoints.append({
                'path': route.path,
                'methods': list(route.methods),
                'name': getattr(route, 'name', 'Unknown')
            })
    
    print("\n=== API ENDPOINT ANALYSIS ===")
    for endpoint in endpoints:
        print(f"{endpoint['methods']} {endpoint['path']}")
    
    return endpoints

def check_missing_blueprint_endpoints(current_endpoints):
    """Check what's missing from your blueprint"""
    blueprint_endpoints = [
        ('POST', '/v1/products/draft'),
        ('POST', '/v1/products/publish'),
        ('GET', '/v1/products'),
        ('POST', '/v1/experiments/start'),
        ('GET', '/v1/experiments'),
        ('POST', '/v1/segments'),
        ('GET', '/v1/segments'),
    ]
    
    current_paths = {f"{list(e['methods'])[0] if e['methods'] else 'GET'} {e['path']}" for e in current_endpoints}
    
    print("\n=== MISSING BLUEPRINT ENDPOINTS ===")
    missing = []
    for method, path in blueprint_endpoints:
        key = f"{method} {path}"
        if key not in current_paths:
            missing.append(key)
            print(f"❌ Missing: {key}")
    
    return missing

async def test_api_startup():
    """Test if the API can start successfully"""
    try:
        import uvicorn
        from apps.api.main import app
        
        # Test configuration
        config = uvicorn.Config(app, host="127.0.0.1", port=8080, log_level="info")
        server = uvicorn.Server(config)
        
        # Start and immediately shutdown to test startup
        await server.serve()
        print("✅ API startup test passed")
        return True
    except Exception as e:
        print(f"❌ API startup failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 AUTONOMAX LOCAL TEST SUITE")
    print("=" * 50)
    
    # Test 1: Basic imports
    if not test_imports():
        print("\n❌ Cannot proceed - fix imports first")
        sys.exit(1)
    
    # Test 2: Endpoint analysis
    endpoints = test_endpoints()
    
    # Test 3: Missing endpoints
    missing = check_missing_blueprint_endpoints(endpoints)
    
    # Test 4: API startup
    if asyncio.run(test_api_startup()):
        print("\n🎉 Local API test completed successfully!")
    else:
        print("\n⚠️  API startup issues detected")
    
    print(f"\n📊 Summary: {len(missing)} missing endpoints from blueprint")