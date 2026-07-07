#!/usr/bin/env python3
"""
RankerToolAI — Local API Proxy
Forwards requests to Claude (Anthropic) and kie.ai with CORS headers.
Run: python social_agent/api_proxy.py
"""
import json, time, urllib.request, urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 7842


def extract_image_url(data):
    """Try multiple response formats to find image URL."""
    if isinstance(data, list) and data:
        data = {'data': data}
    checks = [
        lambda d: (d.get('data') or [{}])[0].get('url'),
        lambda d: (d.get('images') or [{}])[0].get('url'),
        lambda d: (d.get('result') or {}).get('url'),
        lambda d: d.get('image_url'),
        lambda d: d.get('url'),
        lambda d: d.get('output_url'),
        lambda d: ((d.get('output') or [None])[0]) if isinstance(d.get('output'), list) else None,
    ]
    for fn in checks:
        try:
            v = fn(data)
            if v and isinstance(v, str) and v.startswith('http'):
                return v
        except Exception:
            pass
    return None


class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length).decode('utf-8'))
        except Exception:
            self.send_error(400, 'Bad JSON'); return

        try:
            if self.path == '/claude':
                result = self._proxy_claude(body)
            elif self.path == '/kieai':
                result = self._proxy_kieai(body)
            elif self.path == '/ping':
                result = {'ok': True, 'port': PORT}
            else:
                self.send_error(404); return

            payload = json.dumps(result, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_cors()
            self.end_headers()
            self.wfile.write(payload)

        except urllib.error.HTTPError as e:
            body_err = e.read().decode('utf-8', errors='replace')
            self._send_error(e.code, body_err)
        except Exception as e:
            self._send_error(500, str(e))

    def _send_error(self, code, msg):
        payload = json.dumps({'error': msg}).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors()
        self.end_headers()
        self.wfile.write(payload)

    def _proxy_claude(self, body):
        api_key = body.pop('api_key', '')
        if not api_key:
            raise Exception('Missing Claude API key')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=json.dumps(body).encode('utf-8'),
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())

    def _proxy_kieai(self, body):
        api_key = body.pop('api_key', '')
        endpoint = body.pop('endpoint', 'https://api.kie.ai/v1/images/generations')
        status_tpl = body.pop('status_endpoint', '')  # e.g. https://api.kie.ai/v1/tasks/{task_id}

        if not api_key:
            raise Exception('Missing kie.ai API key')

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(body).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())

        # Synchronous response?
        url = extract_image_url(data)
        if url:
            return {'url': url, 'raw': data}

        # Async: has task_id → poll
        task_id = (data.get('task_id') or data.get('id') or
                   data.get('request_id') or data.get('taskId'))

        if task_id and status_tpl:
            poll_url = status_tpl.replace('{task_id}', str(task_id))
            print(f'  [kie.ai] Polling task {task_id}...', flush=True)
            for attempt in range(72):  # max ~6 min
                time.sleep(5)
                poll_req = urllib.request.Request(
                    poll_url,
                    headers={'Authorization': f'Bearer {api_key}'},
                    method='GET'
                )
                with urllib.request.urlopen(poll_req, timeout=20) as r:
                    sd = json.loads(r.read())
                url = extract_image_url(sd)
                if url:
                    print(f'  [kie.ai] Done after {(attempt+1)*5}s', flush=True)
                    return {'url': url, 'raw': sd}
            raise Exception('kie.ai generation timed out after 6 minutes')

        # Return raw if we can't interpret
        return {
            'url': None, 'raw': data,
            'hint': 'Cannot extract image URL. Configure status_endpoint in Settings if kie.ai uses async generation.'
        }


if __name__ == '__main__':
    print(f'\n  RankerToolAI API Proxy')
    print(f'  Listening on http://localhost:{PORT}')
    print(f'  Routes: /claude  /kieai  /ping')
    print('  Press Ctrl+C to stop.\n')
    try:
        HTTPServer(('localhost', PORT), ProxyHandler).serve_forever()
    except KeyboardInterrupt:
        print('\n  Proxy stopped.')
