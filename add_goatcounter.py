#!/usr/bin/env python3
"""
GoatCounter analytics script inserter for blog pages.
Replaces analytics placeholders or inserts before </body>.
"""
import re
from pathlib import Path

GOATCOUNTER_SCRIPT = '''<script data-goatcounter="https://daisuki-koshian.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'''

def process_html_file(filepath):
    """Add GoatCounter script to an HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Check for analytics placeholder comments
    analytics_patterns = [
        r'<!--\s*Analytics[^>]*-->',
        r'<!--\s*analytics[^>]*-->',
        r'<!--\s*Analytics placeholder[^>]*-->'
    ]
    
    replaced = False
    for pattern in analytics_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, GOATCOUNTER_SCRIPT, content)
            replaced = True
            break
    
    # If no placeholder found, insert before </body>
    if not replaced:
        if '</body>' in content:
            content = content.replace('</body>', f'{GOATCOUNTER_SCRIPT}\n</body>')
        else:
            print(f"Warning: No </body> tag found in {filepath}")
            return False
    
    # Only write if content changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    blog_dir = Path('/tmp/blog-work')
    html_files = list(blog_dir.glob('**/index.html'))
    
    modified_count = 0
    for html_file in html_files:
        if process_html_file(html_file):
            print(f"✓ Modified: {html_file.relative_to(blog_dir)}")
            modified_count += 1
        else:
            print(f"○ Skipped: {html_file.relative_to(blog_dir)}")
    
    print(f"\nTotal: {modified_count}/{len(html_files)} files modified")

if __name__ == '__main__':
    main()
