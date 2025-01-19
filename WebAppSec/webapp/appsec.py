from flask import Flask, make_response
from flask_talisman import Talisman
from app import app as original_app

def create_secure_app():
    secure_app = original_app
    
    # Initialize Talisman with strict security settings
    Talisman(secure_app,
        force_https=False,  # Only false for local development
        frame_options='DENY',  # Strictly deny framing
        frame_options_allow_from=None,
        content_security_policy={
            'default-src': "'self'",
            'img-src': ["'self'", '*'],
            'script-src': ["'self'", "'unsafe-inline'"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'frame-ancestors': "'none'",  # Additional framing protection
            'base-uri': "'self'",
            'form-action': "'self'",
            'object-src': "'none'"
        }
    )

    # Enhanced security headers with multiple layers of clickjacking protection
    @secure_app.after_request
    def add_security_headers(response):
        # Multiple layers of frame protection
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'none'"
        
        # Additional security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), payment=()'
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        
        return response

    return secure_app

if __name__ == '__main__':
    secure_app = create_secure_app()
    secure_app.run(host='127.0.0.1', port=5000, debug=False)
