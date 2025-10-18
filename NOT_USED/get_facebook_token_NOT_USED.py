## get_facebook_token.py
#
#from facebook_integration import FacebookAuth, FacebookPoster
#
## ============================================
## STEP 1: Fill in your information here
## ============================================
#
## From Facebook App Dashboard > Settings > Basic
#APP_ID = "2498932317144961"           # Example: "1234567890123456"
#APP_SECRET = "55ad6b318c52bbcf7b18b8e97b70357a"   # Example: "a1b2c3d4e5f6..."
#
## From Graph API Explorer (the short-lived token you just got)
#SHORT_TOKEN = "EAAjgxAUUx4EBPqrlAUZADgZB2tj8Qac0UZBsHEIYlfP9UzKoEEmkcUwBPF4pvf4mXketEZACwjCxTHizFc4xIsTifDDxO6ntg82yyVVDwWIMtXNIETc4IaZAR8A43h9mKUWYXsI8GtJRAN7VsUArBLZBKWReT1s15I35bygPZCQCSZBNtLKR8e5YB2yznI5NlIUUoXOGMPpYcJLdOyAYV2Te4cY3ZBEcjc53WnJZAJfusnhn6eBZA0ZD"  # Example: "EAABsbCS1iHg..."
#
#
## ============================================
## STEP 2: Run this script
## ============================================
#
#print("=" * 60)
#print("FACEBOOK TOKEN GENERATOR")
#print("=" * 60)
#
## Exchange short-lived token for long-lived user token (60 days)
#print("\n🔄 Exchanging for long-lived user token...")
#result = FacebookAuth.get_long_lived_token(APP_ID, APP_SECRET, SHORT_TOKEN)
#
#if "access_token" in result:
#    long_user_token = result["access_token"]
#    print("✅ Long-lived USER token obtained!")
#    print(f"   Expires in: {result.get('expires_in', 'Unknown')} seconds")
#    print(f"   Token: {long_user_token[:30]}...{long_user_token[-10:]}")
#    
#    # Now get page access tokens (these NEVER expire!)
#    print("\n🔄 Getting page access tokens...")
#    fb = FacebookPoster(long_user_token)
#    pages = fb.get_pages()
#    
#    if "data" in pages:
#        print(f"\n✅ Found {len(pages['data'])} page(s):\n")
#        
#        for idx, page in enumerate(pages["data"], 1):
#            print(f"📄 PAGE {idx}: {page['name']}")
#            print(f"   Page ID: {page['id']}")
#            print(f"   Category: {page.get('category', 'N/A')}")
#            print(f"   Page Token (NEVER EXPIRES): {page['access_token']}")
#            print(f"   ⬆️  USE THIS TOKEN FOR PRODUCTION ⬆️\n")
#        
#        print("=" * 60)
#        print("SAVE YOUR PAGE ACCESS TOKEN!")
#        print("This token never expires - keep it secure!")
#        print("=" * 60)
#    else:
#        print(f"❌ Error getting pages: {pages}")
#else:
#    print(f"❌ Error: {result}")
#