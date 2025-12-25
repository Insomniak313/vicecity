from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import urllib.error

VCSKY_BASE_URL = "https://cdn.dos.zone/vcsky/"

def handler(request, context=None):
    """
    Vercel serverless function handler
    """
    try:
        # Extract the path - Vercel passes the full path including /vcsky/
        path = request.url.split('/vcsky/')[-1] if '/vcsky/' in request.url else ''
        
        # Build the full URL
        url = urllib.parse.urljoin(VCSKY_BASE_URL, path)
        
        # Create the proxied request
        req = urllib.request.Request(url)
        
        # Forward some headers
        for header in ['User-Agent', 'Accept', 'Accept-Encoding']:
            if header in request.headers:
                req.add_header(header, request.headers[header])
        
        # Make the request
        with urllib.request.urlopen(req, timeout=10) as response:
            # Read response content
            content = response.read()
            
            # Build response headers
            headers = {
                'Cross-Origin-Opener-Policy': 'same-origin',
                'Cross-Origin-Embedder-Policy': 'require-corp',
                'Access-Control-Allow-Origin': '*',
            }
            
            # Forward content-type and other headers
            for header, value in response.headers.items():
                if header.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                    headers[header] = value
            
            return Response(content, status=response.status, headers=headers)
            
    except urllib.error.HTTPError as e:
        return Response(e.read(), status=e.code, headers={
            'Access-Control-Allow-Origin': '*'
        })
        
    except Exception as e:
        return Response(str(e).encode(), status=500, headers={
            'Access-Control-Allow-Origin': '*'
        })


# Vercel Response class
class Response:
    def __init__(self, body, status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or {}
