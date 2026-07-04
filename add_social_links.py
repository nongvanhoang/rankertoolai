"""
Adds/updates social media icons in footer of all HTML files.
Run from: c:\\Users\\Admin\\RankerToolAI\\
Usage: python add_social_links.py
"""

import os, re

HTML_DIR = os.path.join(os.path.dirname(__file__), "html")

SOCIAL_HTML = '''<div style="display:flex;flex-wrap:wrap;gap:0.55rem;margin-top:1rem;">
          <a href="https://twitter.com/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="X (Twitter)" style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;transition:background 150ms,color 150ms;" onmouseover="this.style.background='rgba(255,255,255,0.14)';this.style.color='#f1f5f9'" onmouseout="this.style.background='rgba(255,255,255,0.07)';this.style.color='#94a3b8'">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.253 5.622 5.911-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          </a>
          <a href="https://reddit.com/u/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="Reddit" style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;transition:background 150ms,color 150ms;" onmouseover="this.style.background='rgba(255,69,0,0.2)';this.style.color='#ff4500'" onmouseout="this.style.background='rgba(255,255,255,0.07)';this.style.color='#94a3b8'">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/></svg>
          </a>
          <a href="https://www.linkedin.com/company/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="LinkedIn" style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;transition:background 150ms,color 150ms;" onmouseover="this.style.background='rgba(0,119,181,0.2)';this.style.color='#0077b5'" onmouseout="this.style.background='rgba(255,255,255,0.07)';this.style.color='#94a3b8'">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
          </a>
          <a href="https://www.youtube.com/@rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="YouTube" style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;transition:background 150ms,color 150ms;" onmouseover="this.style.background='rgba(255,0,0,0.2)';this.style.color='#ff0000'" onmouseout="this.style.background='rgba(255,255,255,0.07)';this.style.color='#94a3b8'">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
          </a>
          <a href="https://www.instagram.com/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="Instagram" style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;transition:background 150ms,color 150ms;" onmouseover="this.style.background='rgba(225,48,108,0.2)';this.style.color='#e1306c'" onmouseout="this.style.background='rgba(255,255,255,0.07)';this.style.color='#94a3b8'">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>
          </a>
          <a href="https://www.tiktok.com/@rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="TikTok" style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;transition:background 150ms,color 150ms;" onmouseover="this.style.background='rgba(255,255,255,0.14)';this.style.color='#f1f5f9'" onmouseout="this.style.background='rgba(255,255,255,0.07)';this.style.color='#94a3b8'">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.18 8.18 0 004.78 1.52V6.79a4.85 4.85 0 01-1.01-.1z"/></svg>
          </a>
          <a href="https://www.pinterest.com/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="Pinterest" style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;transition:background 150ms,color 150ms;" onmouseover="this.style.background='rgba(230,0,35,0.2)';this.style.color='#e60023'" onmouseout="this.style.background='rgba(255,255,255,0.07)';this.style.color='#94a3b8'">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 01.083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg>
          </a>
          <a href="https://dev.to/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="Dev.to" style="width:32px;height:32px;border-radius:8px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;transition:background 150ms,color 150ms;font-size:9px;font-weight:900;letter-spacing:-0.5px;" onmouseover="this.style.background='rgba(255,255,255,0.14)';this.style.color='#f1f5f9'" onmouseout="this.style.background='rgba(255,255,255,0.07)';this.style.color='#94a3b8'">DEV</a>
        </div>'''

SOCIAL_INLINE = '<div style="display:flex;flex-wrap:wrap;gap:0.55rem;margin-top:0.75rem;">' + ''.join([
    '<a href="https://twitter.com/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="X" style="width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;" onmouseover="this.style.background=\'rgba(255,255,255,0.14)\';this.style.color=\'#f1f5f9\'" onmouseout="this.style.background=\'rgba(255,255,255,0.07)\';this.style.color=\'#94a3b8\'"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.737-8.835L1.254 2.25H8.08l4.253 5.622 5.911-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></a>',
    '<a href="https://reddit.com/u/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="Reddit" style="width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;" onmouseover="this.style.background=\'rgba(255,69,0,0.2)\';this.style.color=\'#ff4500\'" onmouseout="this.style.background=\'rgba(255,255,255,0.07)\';this.style.color=\'#94a3b8\'"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/></svg></a>',
    '<a href="https://www.linkedin.com/company/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="LinkedIn" style="width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;" onmouseover="this.style.background=\'rgba(0,119,181,0.2)\';this.style.color=\'#0077b5\'" onmouseout="this.style.background=\'rgba(255,255,255,0.07)\';this.style.color=\'#94a3b8\'"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></a>',
    '<a href="https://www.youtube.com/@rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="YouTube" style="width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;" onmouseover="this.style.background=\'rgba(255,0,0,0.2)\';this.style.color=\'#ff0000\'" onmouseout="this.style.background=\'rgba(255,255,255,0.07)\';this.style.color=\'#94a3b8\'"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg></a>',
    '<a href="https://www.instagram.com/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="Instagram" style="width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;" onmouseover="this.style.background=\'rgba(225,48,108,0.2)\';this.style.color=\'#e1306c\'" onmouseout="this.style.background=\'rgba(255,255,255,0.07)\';this.style.color=\'#94a3b8\'"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg></a>',
    '<a href="https://www.tiktok.com/@rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="TikTok" style="width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;" onmouseover="this.style.background=\'rgba(255,255,255,0.14)\';this.style.color=\'#f1f5f9\'" onmouseout="this.style.background=\'rgba(255,255,255,0.07)\';this.style.color=\'#94a3b8\'"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.28 6.28 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.69a8.18 8.18 0 004.78 1.52V6.79a4.85 4.85 0 01-1.01-.1z"/></svg></a>',
    '<a href="https://www.pinterest.com/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="Pinterest" style="width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;" onmouseover="this.style.background=\'rgba(230,0,35,0.2)\';this.style.color=\'#e60023\'" onmouseout="this.style.background=\'rgba(255,255,255,0.07)\';this.style.color=\'#94a3b8\'"><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.373 0 0 5.373 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.405.042-3.441.218-.937 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 01.083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.632-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0z"/></svg></a>',
    '<a href="https://dev.to/rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="Dev.to" style="width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.1);display:flex;align-items:center;justify-content:center;color:#94a3b8;text-decoration:none;font-size:8px;font-weight:900;letter-spacing:-0.5px;" onmouseover="this.style.background=\'rgba(255,255,255,0.14)\';this.style.color=\'#f1f5f9\'" onmouseout="this.style.background=\'rgba(255,255,255,0.07)\';this.style.color=\'#94a3b8\'">DEV</a>',
]) + '</div>'

def process_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    if "footer-brand" not in content:
        return False, "no footer-brand"

    # Already updated (has new social icons)
    if 'rankertoolai" rel="noopener noreferrer" target="_blank" aria-label="Reddit"' in content:
        return False, "already has social icons"

    # Pattern A: has old 3-icon social div (multi-line)
    old_social_pattern = re.compile(
        r'<div style="display:flex;gap:0\.75rem;margin-top:1rem;">.*?</div>',
        re.DOTALL
    )
    if old_social_pattern.search(content):
        new_content = old_social_pattern.sub(SOCIAL_HTML, content)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True, "replaced old 3-icon bar"

    # Pattern B: multi-line footer — tagline <p> followed by </div>
    tagline_multiline = re.compile(
        r'(<p class="footer-tagline">[^<]*</p>)\s*\n(\s*</div>)',
        re.MULTILINE
    )
    if tagline_multiline.search(content):
        new_content = tagline_multiline.sub(
            lambda m: m.group(1) + "\n        " + SOCIAL_HTML + "\n" + m.group(2),
            content
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True, "added (multi-line footer)"

    # Pattern C: minified footer — inline <p style=...> followed by </div>
    # e.g. ...footer-tagline text.</p></div>
    inline_p = re.compile(r'(<p [^>]*>[^<]+</p>)(</div>)', re.MULTILINE)
    # Only apply inside footer-brand
    brand_block = re.compile(
        r'(<div class="footer-brand">)(.*?)(</div>)',
        re.DOTALL
    )
    m = brand_block.search(content)
    if m:
        inner = m.group(2)
        if '</p>' in inner and SOCIAL_INLINE[:30] not in inner:
            new_inner = inner.rstrip() + SOCIAL_INLINE
            new_content = content[:m.start()] + m.group(1) + new_inner + m.group(3) + content[m.end():]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True, "added (minified footer)"

    return False, "pattern not matched"

def main():
    updated = 0
    skipped = 0
    errors = []

    for root, dirs, files in os.walk(HTML_DIR):
        # Skip go/ redirect pages (no point adding social there)
        if "\\go\\" in root or "/go/" in root:
            continue
        for fname in files:
            if not fname.endswith(".html"):
                continue
            fpath = os.path.join(root, fname)
            rel = fpath.replace(HTML_DIR + os.sep, "")
            ok, reason = process_file(fpath)
            if ok:
                print(f"  [OK] {rel} — {reason}")
                updated += 1
            else:
                skipped += 1

    print(f"\nDone: {updated} files updated, {skipped} skipped")

if __name__ == "__main__":
    main()
