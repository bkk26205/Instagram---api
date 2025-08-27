from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/api/instagram/user', methods=['GET'])
def get_instagram_user():
    username = request.args.get('username')
    
    if not username:
        return jsonify({
            "error": "Username parameter is required",
            "example": "/api/instagram/user?username=instagram"
        }), 400
    
    try:
        # Use Instagram's GraphQL API directly
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://www.instagram.com',
            'Referer': f'https://www.instagram.com/{username}/',
            'X-Requested-With': 'XMLHttpRequest',
            'X-IG-App-ID': '936619743392459',
        }
        
        # First get the user ID
        user_id_url = f'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}'
        response = requests.get(user_id_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({
                "error": f"Account not found or unavailable (HTTP {response.status_code})",
                "username": username
            }), 404
        
        data = response.json()
        
        if 'data' not in data or 'user' not in data['data']:
            return jsonify({
                "error": "Could not extract user data from Instagram API",
                "username": username
            }), 500
        
        user_data = data['data']['user']
        
        # Format response
        result = {
            "username": user_data.get('username', username),
            "full_name": user_data.get('full_name', ''),
            "biography": user_data.get('biography', ''),
            "followers": user_data.get('edge_followed_by', {}).get('count', 0),
            "following": user_data.get('edge_follow', {}).get('count', 0),
            "posts": user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
            "profile_pic": user_data.get('profile_pic_url_hd', ''),
            "is_private": user_data.get('is_private', False),
            "is_verified": user_data.get('is_verified', False),
            "external_url": user_data.get('external_url', ''),
            "success": True,
            "credit": "Made with ❤️ by @DIWANI_xD"
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "username": username,
            "credit": "Made with ❤️ by @DIWANI_xD"
        }), 500

@app.route('/')
def home():
    return jsonify({
        "message": "Instagram Public Data API",
        "endpoints": {
            "get_user_info": "/api/instagram/user?username=USERNAME"
        },
        "credit": "Made with ❤️ by @DIWANI_xD"
    })

if __name__ == '__main__':
    app.run(debug=True)
