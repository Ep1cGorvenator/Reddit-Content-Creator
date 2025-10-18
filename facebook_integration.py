import requests
import os
from typing import Optional, Dict, Any
import json

class FacebookPoster:
    """
    Handles posting content to Facebook using the Graph API.
    
    Setup Instructions:
    1. Go to https://developers.facebook.com/
    2. Create a new app or use existing
    3. Add Facebook Login product
    4. Get your App ID and App Secret
    5. Generate a User Access Token with 'pages_manage_posts' permission
    6. (Optional) Get a Long-Lived Page Access Token for your page
    """
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize Facebook poster.
        
        Args:
            access_token: Facebook Page Access Token. If None, will look for FB_ACCESS_TOKEN env var
        """
        self.access_token = access_token or os.getenv('FB_ACCESS_TOKEN')
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def validate_token(self) -> Dict[str, Any]:
        """
        Validate the access token and get token info.
        
        Returns:
            Dict with token information or error
        """
        if not self.access_token:
            return {"error": "No access token provided"}
        
        url = f"{self.base_url}/me"
        params = {
            "access_token": self.access_token,
            "fields": "id,name"  # Explicitly request only basic fields
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            # Check if response is valid
            if response.status_code != 200:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
            
            # Try to parse JSON
            try:
                data = response.json()
                return data
            except json.JSONDecodeError as e:
                return {
                    "error": f"Invalid JSON response: {str(e)}",
                    "raw_response": response.text[:500]  # First 500 chars
                }
                
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error - check your internet"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def get_pages(self) -> Dict[str, Any]:
        """
        Get list of pages the user manages.
        
        Returns:
            Dict with pages data or error
        """
        if not self.access_token:
            return {"error": "No access token provided"}
        
        url = f"{self.base_url}/me/accounts"
        params = {
            "access_token": self.access_token,
            "fields": "id,name,access_token,category"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
            
            try:
                data = response.json()
                
                # Check if there's an error in the response
                if "error" in data:
                    return data
                
                # Check if we got pages
                if "data" not in data:
                    return {
                        "error": "No 'data' field in response",
                        "raw_response": str(data)
                    }
                
                return data
                
            except json.JSONDecodeError as e:
                return {
                    "error": f"Invalid JSON response: {str(e)}",
                    "raw_response": response.text[:500]
                }
                
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection error - check your internet"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def post_to_page(
        self, 
        page_id: str, 
        message: str, 
        page_access_token: Optional[str] = None,
        link: Optional[str] = None,
        video_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post content to a Facebook page.
        
        Args:
            page_id: Facebook Page ID
            message: Text content to post
            page_access_token: Page-specific access token (if available)
            link: Optional URL to attach
            video_path: Optional path to video file to upload
            
        Returns:
            Dict with post_id or error
        """
        token = page_access_token or self.access_token
        
        if not token:
            return {"error": "No access token provided"}
        
        # If video is provided, use video upload endpoint
        if video_path and os.path.exists(video_path):
            return self._post_video(page_id, message, video_path, token)
        
        # Regular text/link post
        url = f"{self.base_url}/{page_id}/feed"
        
        data = {
            "message": message,
            "access_token": token
        }
        
        if link:
            data["link"] = link
        
        try:
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if "error" in result:
                return result
            
            return {
                "success": True,
                "post_id": result.get("id"),
                "message": "Posted successfully to Facebook!"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _post_video(
        self, 
        page_id: str, 
        message: str, 
        video_path: str, 
        token: str
    ) -> Dict[str, Any]:
        """
        Upload and post a video to Facebook page.
        
        Args:
            page_id: Facebook Page ID
            message: Video description
            video_path: Path to video file
            token: Access token
            
        Returns:
            Dict with video post result
        """
        url = f"{self.base_url}/{page_id}/videos"
        
        try:
            with open(video_path, 'rb') as video_file:
                files = {'file': video_file}
                data = {
                    'description': message,
                    'access_token': token
                }
                
                response = requests.post(url, data=data, files=files, timeout=120)
                result = response.json()
                
                if "error" in result:
                    return result
                
                return {
                    "success": True,
                    "video_id": result.get("id"),
                    "message": "Video posted successfully to Facebook!"
                }
        except Exception as e:
            return {"error": str(e)}
    
    def post_to_profile(
        self, 
        message: str, 
        link: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post to user's personal profile (feed).
        Note: This has limited functionality due to Facebook API restrictions.
        
        Args:
            message: Text content to post
            link: Optional URL to attach
            
        Returns:
            Dict with result or error
        """
        if not self.access_token:
            return {"error": "No access token provided"}
        
        url = f"{self.base_url}/me/feed"
        
        data = {
            "message": message,
            "access_token": self.access_token
        }
        
        if link:
            data["link"] = link
        
        try:
            response = requests.post(url, data=data, timeout=30)
            result = response.json()
            
            if "error" in result:
                return result
            
            return {
                "success": True,
                "post_id": result.get("id"),
                "message": "Posted successfully to your profile!"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def delete_post(self, post_id: str, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a post.
        
        Args:
            post_id: ID of the post to delete
            token: Access token (uses instance token if not provided)
            
        Returns:
            Dict with success status or error
        """
        token = token or self.access_token
        
        if not token:
            return {"error": "No access token provided"}
        
        url = f"{self.base_url}/{post_id}"
        params = {"access_token": token}
        
        try:
            response = requests.delete(url, params=params, timeout=10)
            result = response.json()
            
            if "success" in result and result["success"]:
                return {"success": True, "message": "Post deleted successfully"}
            
            return result
        except Exception as e:
            return {"error": str(e)}


class FacebookAuth:
    """
    Helper class for Facebook authentication flow.
    """
    
    @staticmethod
    def get_login_url(app_id: str, redirect_uri: str, scope: str = "pages_manage_posts,pages_read_engagement") -> str:
        """
        Generate Facebook OAuth login URL.
        
        Args:
            app_id: Your Facebook App ID
            redirect_uri: URL to redirect after authentication
            scope: Permissions to request (comma-separated)
            
        Returns:
            Facebook login URL
        """
        base_url = "https://www.facebook.com/v18.0/dialog/oauth"
        return f"{base_url}?client_id={app_id}&redirect_uri={redirect_uri}&scope={scope}"
    
    @staticmethod
    def exchange_code_for_token(
        app_id: str, 
        app_secret: str, 
        redirect_uri: str, 
        code: str
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            app_id: Your Facebook App ID
            app_secret: Your Facebook App Secret
            redirect_uri: Same redirect URI used in login
            code: Authorization code from callback
            
        Returns:
            Dict with access_token or error
        """
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            "client_id": app_id,
            "client_secret": app_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def get_long_lived_token(app_id: str, app_secret: str, short_token: str) -> Dict[str, Any]:
        """
        Exchange short-lived token for long-lived token (60 days).
        
        Args:
            app_id: Your Facebook App ID
            app_secret: Your Facebook App Secret
            short_token: Short-lived access token
            
        Returns:
            Dict with long-lived access_token or error
        """
        url = "https://graph.facebook.com/v18.0/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e)}