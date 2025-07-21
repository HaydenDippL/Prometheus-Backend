from flask import Flask, request, Response
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

KALSHI_API = 'https://api.elections.kalshi.com'

# Headers that should NOT be forwarded to Kalshi API
EXCLUDED_REQUEST_HEADERS = {
    'host', 'origin', 'referer', 'user-agent', 'connection', 
    'sec-fetch-site', 'sec-fetch-mode', 'sec-fetch-dest',
    'sec-ch-ua', 'sec-ch-ua-mobile', 'sec-ch-ua-platform'
}

@app.route('/api/kalshi/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def proxy(path):
    method = request.method
    
    # Handle OPTIONS preflight requests locally - DON'T forward to Kalshi
    if method == 'OPTIONS':
        logging.info("Handling preflight OPTIONS request for: %s", path)
        response = Response('', 200)
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Credentials"] = "true" 
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response
    
    # Build headers to send to Kalshi API
    headers = {}
    
    # Forward important headers from the client request
    for key, value in request.headers:
        if key.lower() not in EXCLUDED_REQUEST_HEADERS:
            headers[key] = value
    
    # Ensure we have basic headers for API communication
    if 'Accept' not in headers:
        headers['Accept'] = 'application/json'
    if 'User-Agent' not in headers:
        headers['User-Agent'] = 'KalshiProxy/1.0'
    
    url = f"{KALSHI_API}/{path}"
    
    logging.basicConfig(level=logging.INFO)
    logging.info("Proxying %s request to: %s", method, url)
    logging.info("Headers being sent to Kalshi: %s", headers)
    logging.info("Query params: %s", dict(request.args))

    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            timeout=30
        )
        
        logging.info("Kalshi API response status: %s", resp.status_code)

        # Filter response headers
        excluded_response_headers = {
            'content-encoding', 'content-length', 'transfer-encoding', 
            'connection', 'access-control-allow-origin', 'access-control-allow-credentials',
            'access-control-allow-headers', 'access-control-allow-methods'
        }
        response_headers = [
            (name, value) for name, value in resp.headers.items() 
            if name.lower() not in excluded_response_headers
        ]

        response = Response(resp.content, resp.status_code, response_headers)

        # Set CORS headers for your frontend
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

        return response
        
    except requests.exceptions.RequestException as e:
        logging.error("Request to Kalshi API failed: %s", str(e))
        error_response = Response(
            f'{{"error": "Proxy request failed", "details": "{str(e)}"}}',
            500,
            {'Content-Type': 'application/json'}
        )
        error_response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        error_response.headers["Access-Control-Allow-Credentials"] = "true"
        return error_response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)