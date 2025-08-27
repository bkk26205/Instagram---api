from flask import Flask, request, jsonify
import requests
import re
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
        # Updated headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Fetch Instagram profile page
        response = requests.get(f'https://www.instagram.com/{username}/', headers=headers, timeout=10)
        
        if response.status_code != 200:
            return jsonify({
                "error": f"Account not found or unavailable (HTTP {response.status_code})",
                "username": username
            }), 404
        
        html_content = response.text
        
        # Multiple methods to extract data
        json_data = None
        
        # Method 1: Try to find the new JSON pattern
        pattern = r'<script type="application/json" data-reactroot="">(.*?)</script>'
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match)
                if 'props' in data and 'pageProps' in data['props']:
                    json_data = data
                    break
            except:
                continue
        
        # Method 2: Try alternative pattern
        if not json_data:
            pattern2 = r'window\.__additionalDataLoaded\s*\(\s*[^,]+,\s*({.*?})\s*\)\s*;'
            match2 = re.search(pattern2, html_content, re.DOTALL)
            if match2:
                try:
                    json_data = json.loads(match2.group(1))
                except:
                    pass
        
        # Method 3: Try the old pattern
        if not json_data:
            pattern3 = r'window\._sharedData\s*=\s*({.*?});'
            match3 = re.search(pattern3, html_content, re.DOTALL)
            if match3:
                try:
                    json_data = json.loads(match3.group(1))
                except:
                    pass
        
        if not json_data:
            return jsonify({
                "error": "Could not extract data from Instagram page",
                "username": username,
                "tip": "Instagram has changed their HTML structure"
            }), 500
        
        # Extract user data based on different possible JSON structures
        user_data = None
        
        # New structure
        if 'props' in json_data and 'pageProps' in json_data['props']:
            user_data = json_data['props']['pageProps'].get('user', {})
        # Older structure
        elif 'entry_data' in json_data and 'ProfilePage' in json_data['entry_data']:
            user_data = json_data['entry_data']['ProfilePage'][0]['graphql']['user']
        # Alternative structure
        elif 'graphql' in json_data and 'user' in json_data['graphql']:
            user_data = json_data['graphql']['user']
        
        if not user_data:
            return jsonify({
                "error": "Could not find user data in extracted JSON",
                "username": username
            }), 500
        
        # Format response
        result = {
            "username": user_data.get('username', username),
            "full_name": user_data.get('full_name', ''),
            "biography": user_data.get('biography', ''),
            "followers": user_data.get('edge_followed_by', {}).get('count', 0),
            "following": user_data.get('edge_follow', {}).get('count', 0),
            "posts": user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
            "profile_pic": user_data.get('profile_pic_url_hd', user_data.get('profile_pic_url', '')),
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
