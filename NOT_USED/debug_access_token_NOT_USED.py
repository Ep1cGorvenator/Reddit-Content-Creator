#"""
#Diagnostic script to debug Facebook token issues
#Run this to identify the exact problem with your token
#"""
#
#import requests
#import json
#
## ============================================
## PASTE YOUR TOKEN HERE
## ============================================
#TOKEN = "EAAjgxAUUx4EBPlbKsWcC4dyoVz1xviwzcXEF8Ga0ebbn3KiuqfH7aGZApdB8ZBZAiAoWKg1uzIFBKvUVMmvmPClzfpDCkWHZC0WaveYzJnIyqrFNlpk8uNcTrXRqzoNbZCEn7gNOmvRQ7s7BnjmyjR71ovu9O9jUzDD1qcLEHAIKyV8UAdIyMTMhn7HZBaPy6KzaBD"
#
#print("=" * 70)
#print("FACEBOOK TOKEN DIAGNOSTIC TOOL")
#print("=" * 70)
#
## Test 1: Check token format
#print("\n📋 Test 1: Token Format Check")
#print("-" * 70)
#print(f"Token length: {len(TOKEN)} characters")
#print(f"Token starts with: {TOKEN[:10]}...")
#print(f"Token ends with: ...{TOKEN[-10:]}")
#
#if len(TOKEN) < 50:
#    print("⚠️  WARNING: Token seems too short (should be 150-300 chars)")
#elif len(TOKEN) > 500:
#    print("⚠️  WARNING: Token seems too long")
#else:
#    print("✅ Token length looks reasonable")
#
## Test 2: Basic connectivity
#print("\n🌐 Test 2: Internet Connectivity")
#print("-" * 70)
#try:
#    response = requests.get("https://graph.facebook.com", timeout=5)
#    print(f"✅ Can reach Facebook API (Status: {response.status_code})")
#except Exception as e:
#    print(f"❌ Cannot reach Facebook API: {e}")
#    print("   Check your internet connection!")
#    exit(1)
#
## Test 3: Token validation (detailed)
#print("\n🔐 Test 3: Token Validation")
#print("-" * 70)
#
#url = "https://graph.facebook.com/v18.0/me"
#params = {
#    "access_token": TOKEN,
#    "fields": "id,name"
#}
#
#try:
#    print(f"Making request to: {url}")
#    response = requests.get(url, params=params, timeout=10)
#    
#    print(f"Response status code: {response.status_code}")
#    print(f"Response headers: {dict(response.headers)}")
#    print(f"\nRaw response text:")
#    print("-" * 70)
#    print(response.text)
#    print("-" * 70)
#    
#    if response.status_code == 200:
#        try:
#            data = response.json()
#            print("\n✅ Token is VALID!")
#            print(f"   User ID: {data.get('id', 'Unknown')}")
#            print(f"   User Name: {data.get('name', 'Unknown')}")
#        except json.JSONDecodeError as e:
#            print(f"\n❌ Token validation succeeded but response is not JSON")
#            print(f"   JSON Error: {e}")
#            print(f"   This is the 'Invalid JSON for postcard' issue!")
#    else:
#        try:
#            error_data = response.json()
#            print(f"\n❌ Token is INVALID")
#            print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
#            print(f"   Type: {error_data.get('error', {}).get('type', 'Unknown')}")
#            print(f"   Code: {error_data.get('error', {}).get('code', 'Unknown')}")
#        except:
#            print(f"\n❌ Token is INVALID (non-JSON error)")
#            
#except requests.exceptions.Timeout:
#    print("❌ Request timed out")
#except requests.exceptions.ConnectionError:
#    print("❌ Connection error")
#except Exception as e:
#    print(f"❌ Unexpected error: {e}")
#    import traceback
#    traceback.print_exc()
#
## Test 4: Check token permissions
#print("\n🔑 Test 4: Token Permissions")
#print("-" * 70)
#
#url = "https://graph.facebook.com/v18.0/me/permissions"
#params = {"access_token": TOKEN}
#
#try:
#    response = requests.get(url, params=params, timeout=10)
#    
#    if response.status_code == 200:
#        data = response.json()
#        permissions = data.get("data", [])
#        
#        print(f"Found {len(permissions)} permissions:\n")
#        
#        required = ["pages_manage_posts", "pages_read_engagement", "pages_show_list"]
#        granted = []
#        
#        for perm in permissions:
#            status = "✅" if perm["status"] == "granted" else "❌"
#            print(f"{status} {perm['permission']}: {perm['status']}")
#            
#            if perm["status"] == "granted":
#                granted.append(perm["permission"])
#        
#        print("\n" + "=" * 70)
#        print("Required Permissions Check:")
#        print("=" * 70)
#        for req in required:
#            if req in granted:
#                print(f"✅ {req}")
#            else:
#                print(f"❌ {req} - MISSING!")
#    else:
#        print(f"❌ Could not fetch permissions (Status: {response.status_code})")
#        print(f"   Response: {response.text}")
#        
#except Exception as e:
#    print(f"❌ Error checking permissions: {e}")
#
## Test 5: Try to fetch pages
#print("\n📄 Test 5: Fetch Pages")
#print("-" * 70)
#
#url = "https://graph.facebook.com/v18.0/me/accounts"
#params = {
#    "access_token": TOKEN,
#    "fields": "id,name,access_token,category"
#}
#
#try:
#    response = requests.get(url, params=params, timeout=10)
#    
#    print(f"Response status: {response.status_code}")
#    
#    if response.status_code == 200:
#        data = response.json()
#        
#        if "data" in data:
#            pages = data["data"]
#            print(f"\n✅ Found {len(pages)} page(s):\n")
#            
#            for idx, page in enumerate(pages, 1):
#                print(f"📄 PAGE {idx}:")
#                print(f"   Name: {page.get('name', 'Unknown')}")
#                print(f"   ID: {page.get('id', 'Unknown')}")
#                print(f"   Category: {page.get('category', 'Unknown')}")
#                print(f"   Has Token: {'Yes' if page.get('access_token') else 'No'}")
#                print()
#        else:
#            print("❌ No 'data' field in response")
#            print(f"   Response: {data}")
#    else:
#        print(f"❌ Failed to fetch pages")
#        print(f"   Response: {response.text}")
#        
#except Exception as e:
#    print(f"❌ Error fetching pages: {e}")
#
## Test 6: Debug Token (if possible)
#print("\n🔍 Test 6: Token Debug Info")
#print("-" * 70)
#
#url = "https://graph.facebook.com/v18.0/debug_token"
#params = {
#    "input_token": TOKEN,
#    "access_token": TOKEN  # Using same token to debug itself
#}
#
#try:
#    response = requests.get(url, params=params, timeout=10)
#    
#    if response.status_code == 200:
#        data = response.json()
#        token_data = data.get("data", {})
#        
#        print(f"App ID: {token_data.get('app_id', 'Unknown')}")
#        print(f"Type: {token_data.get('type', 'Unknown')}")
#        print(f"Valid: {token_data.get('is_valid', False)}")
#        print(f"Expires: {token_data.get('expires_at', 'Never')}")
#        print(f"User ID: {token_data.get('user_id', 'Unknown')}")
#        
#        if 'scopes' in token_data:
#            print(f"\nScopes: {', '.join(token_data['scopes'])}")
#    else:
#        print(f"Could not debug token (Status: {response.status_code})")
#        
#except Exception as e:
#    print(f"Error debugging token: {e}")
#
#print("\n" + "=" * 70)
#print("DIAGNOSTIC COMPLETE")
#print("=" * 70)
#print("\nIf you see 'Invalid JSON for postcard', the issue is likely:")
#print("1. Token is for wrong app/environment")
#print("2. Token has unusual characters or is corrupted")
#print("3. Facebook API version mismatch")
#print("4. Network/proxy intercepting requests")
#print("\nShare the output above for further help!")