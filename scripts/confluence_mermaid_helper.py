#!/usr/bin/env python3
"""
Optimized helper for adding Mermaid diagrams to Confluence pages.
Minimizes token usage by only fetching/modifying what's necessary.
Uses subprocess + curl (no external dependencies).
"""
import os
import sys
import json
import re
import subprocess
import tempfile
import time
from typing import Optional

class ConfluenceMermaidHelper:
    def __init__(self):
        # Try environment variables first
        self.url = os.environ.get('CONFLUENCE_URL')
        self.username = os.environ.get('CONFLUENCE_USERNAME')
        self.token = os.environ.get('CONFLUENCE_API_TOKEN')
        
        # Fallback to keychain if not in env
        if not self.token:
            self.token = self._get_from_keychain('confluence_api_token', os.environ.get('USER', ''))
        if not self.username:
            self.username = self._get_from_keychain('confluence_username', os.environ.get('USER', ''))
        if not self.url:
            self.url = "https://metal-scribe.atlassian.net/wiki"
        
        if not all([self.url, self.username, self.token]):
            raise ValueError("Missing required credentials (check environment or keychain)")
        
        self.auth_str = f"{self.username}:{self.token}"
    
    def _get_from_keychain(self, service: str, account: str) -> str:
        """Get credential from macOS keychain."""
        try:
            cmd = ['security', 'find-generic-password', '-a', account, '-s', service, '-w']
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return result.stdout.strip() if result.returncode == 0 else ''
        except Exception:
            return ''
    
    def _curl_request(self, method: str, endpoint: str, data: dict = None, 
                     files: dict = None, headers: dict = None) -> dict:
        """Make a curl request and return JSON response."""
        url = f"{self.url}{endpoint}"
        cmd = ['curl', '-s', '-X', method, '-u', self.auth_str]
        
        if headers:
            for key, value in headers.items():
                cmd.extend(['-H', f'{key}: {value}'])
        
        if data:
            # Write JSON data to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(data, f)
                temp_file = f.name
            cmd.extend(['-d', f'@{temp_file}'])
        
        if files:
            cmd.extend(['-H', 'X-Atlassian-Token: no-check'])
            for key, (filename, content) in files.items():
                cmd.extend(['-F', f'file=@{content}'])
        
        cmd.append(url)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp file
        if data and 'temp_file' in locals():
            os.unlink(temp_file)
        
        if result.returncode != 0:
            raise RuntimeError(f"Curl failed: {result.stderr}")
        
        return json.loads(result.stdout) if result.stdout else {}
    
    def get_page_version(self, page_id: str) -> int:
        """Get only the version number (minimal data fetch)."""
        data = self._curl_request('GET', f"/rest/api/content/{page_id}?expand=version")
        return data['version']['number']
    
    def upload_diagram(self, page_id: str, diagram_path: str, attachment_name: str) -> dict:
        """Upload diagram as attachment (without .mmd extension)."""
        # Create temp file with exact name (no extension, no random suffix)
        tmp_path = f'/tmp/{attachment_name}'
        
        with open(diagram_path, 'r') as src:
            with open(tmp_path, 'w') as dst:
                dst.write(src.read())
        
        # Upload using curl directly
        cmd = [
            'curl', '-s', '-X', 'POST',
            '-H', 'X-Atlassian-Token: no-check',
            '-u', self.auth_str,
            '-F', f'file=@{tmp_path}',
            '-F', 'comment=Mermaid diagram source',
            f'{self.url}/rest/api/content/{page_id}/child/attachment'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        os.unlink(tmp_path)
        
        if result.returncode != 0:
            raise RuntimeError(f"Upload failed: {result.stderr}")
        
        response = json.loads(result.stdout)
        return response['results'][0]
    
    def update_page_targeted(self, page_id: str, find_pattern: str, 
                            replacement: str, title: str) -> dict:
        """
        Make a targeted update to page content.
        Only fetches and reconstructs the minimum necessary.
        """
        # Get current version and content
        data = self._curl_request('GET', f"/rest/api/content/{page_id}?expand=body.storage,version")
        
        current_version = data['version']['number']
        content = data['body']['storage']['value']
        
        # Make the targeted replacement
        if find_pattern not in content:
            raise ValueError(f"Pattern not found in page: {find_pattern}")
        
        new_content = content.replace(find_pattern, replacement, 1)
        
        # Update page
        update_data = {
            "version": {"number": current_version + 1},
            "type": "page",
            "title": title,
            "body": {
                "storage": {
                    "value": new_content,
                    "representation": "storage"
                }
            }
        }
        
        return self._curl_request(
            'PUT', 
            f"/rest/api/content/{page_id}",
            data=update_data,
            headers={'Content-Type': 'application/json'}
        )
    
    def add_mermaid_diagram(self, page_id: str, page_title: str,
                           diagram_path: str, attachment_name: str,
                           insert_after_pattern: str, clean_existing: bool = False,
                           auto_prefix: bool = True) -> dict:
        """
        Complete workflow: upload diagram and add macro to page.
        
        Args:
            page_id: Confluence page ID
            page_title: Page title (needed for update)
            diagram_path: Path to .mmd file
            attachment_name: Name for attachment (without extension)
            insert_after_pattern: HTML pattern to insert after
            clean_existing: If True, delete existing attachment with same name first
            auto_prefix: If True, automatically prefix generic names to avoid conflicts
        """
        # Auto-prefix generic names to avoid conflicts
        generic_names = ['diagram', 'chart', 'image', 'graph', 'figure', 'visual']
        if auto_prefix and attachment_name.lower() in generic_names:
            import hashlib
            pattern_hash = hashlib.md5(insert_after_pattern.encode()).hexdigest()[:8]
            original_name = attachment_name
            attachment_name = f"{attachment_name}-{pattern_hash}"
            print(f"⚠️  Generic name '{original_name}' auto-prefixed to '{attachment_name}' to avoid conflicts")
        
        # Clean up existing attachment if requested
        if clean_existing:
            print(f"Checking for existing '{attachment_name}' attachment...")
            cmd = ['curl', '-s', '-u', self.auth_str,
                   f'{self.url}/rest/api/content/{page_id}/child/attachment?filename={attachment_name}']
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            if data.get('results'):
                att_id = data['results'][0]['id']
                print(f"  Deleting existing attachment (id: {att_id})...")
                cmd_del = ['curl', '-s', '-X', 'DELETE', '-u', self.auth_str,
                          f'{self.url}/rest/api/content/{att_id}']
                subprocess.run(cmd_del, capture_output=True, text=True)
                print(f"  ✅ Deleted")
                import time
                time.sleep(1)  # Wait for deletion to process
        
        print(f"Uploading diagram: {attachment_name}")
        attachment = self.upload_diagram(page_id, diagram_path, attachment_name)
        
        # Create Mermaid macro
        macro = (
            f'<ac:structured-macro ac:name="mermaid-cloud" ac:schema-version="1">'
            f'<ac:parameter ac:name="toolbar">bottom</ac:parameter>'
            f'<ac:parameter ac:name="filename">{attachment_name}</ac:parameter>'
            f'<ac:parameter ac:name="zoom">fit</ac:parameter>'
            f'<ac:parameter ac:name="revision">1</ac:parameter>'
            f'</ac:structured-macro>'
        )
        
        # Insert macro after the pattern
        replacement = insert_after_pattern + macro
        
        print(f"Updating page with macro")
        result = self.update_page_targeted(
            page_id, insert_after_pattern, replacement, page_title
        )
        
        print(f"✅ Successfully added diagram to page (version {result['version']['number']})")
        return result


def main():
    if len(sys.argv) < 6:
        print("Usage: confluence_mermaid_helper.py <page_id> <page_title> <diagram.mmd> <attachment_name> <insert_after_pattern>")
        print("Example: confluence_mermaid_helper.py 131083 'My Page' diagram.mmd my-diagram '<h2>Section 3</h2>'")
        sys.exit(1)
    
    page_id = sys.argv[1]
    page_title = sys.argv[2]
    diagram_path = sys.argv[3]
    attachment_name = sys.argv[4]
    insert_after = sys.argv[5]
    
    helper = ConfluenceMermaidHelper()
    helper.add_mermaid_diagram(page_id, page_title, diagram_path, attachment_name, insert_after)


if __name__ == '__main__':
    main()
