#!/usr/bin/env python3
"""Update all /go/ redirect pages to add enhanced source tracking."""
import re
from pathlib import Path

GO_DIR = Path(__file__).parent / "html" / "go"

NEW_SCRIPT = '''  <script>
    (function() {
      var tool = document.title.match(/Redirecting to (.+?) \\|/)?.[1] || '';
      var ref  = document.referrer ? new URL(document.referrer).pathname : 'direct';
      var params = new URLSearchParams(window.location.search);
      var subid  = params.get('ref') || ref.replace(/\\//g,'_').replace(/^_|_$/g,'') || 'direct';

      if (typeof gtag !== 'undefined') {
        gtag('event', 'affiliate_click', {
          tool:        document.querySelector('[data-tool]')?.dataset.tool || subid,
          source_path: ref,
          sub_id:      subid,
          utm_source:  params.get('utm_source') || '',
          utm_medium:  params.get('utm_medium') || '',
        });
      }

      // Append ref as subid to destination URL for affiliate network tracking
      var destEl = document.querySelector('a[href]');
      if (!destEl) return;
      var dest = new URL(destEl.href);
      ['utm_source','utm_medium','utm_campaign','utm_content','gclid'].forEach(function(k){
        if (params.has(k)) dest.searchParams.set(k, params.get(k));
      });
      // Pass sub_id (each network uses different param — update when you get affiliate links)
      dest.searchParams.set('ref', subid);

      setTimeout(function(){ window.location.replace(dest.toString()); }, 280);
    })();
  </script>'''

updated = 0
for go_page in GO_DIR.iterdir():
    html_file = go_page / "index.html"
    if not html_file.exists():
        continue

    content = html_file.read_text(encoding="utf-8")

    # Replace existing script block
    new_content = re.sub(
        r'<script>\s*\(function\(\)\s*\{.*?}\)\(\);\s*</script>',
        NEW_SCRIPT,
        content,
        flags=re.DOTALL
    )

    if new_content != content:
        html_file.write_text(new_content, encoding="utf-8")
        updated += 1
        print(f"  updated  {go_page.name}")
    else:
        print(f"  skip     {go_page.name}")

print(f"\nDone: {updated} pages updated")
