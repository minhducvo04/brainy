"""Local demo: run from the repository containing the existing Cognee state."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_LOCK = threading.Lock()


def run_backend(action, payload):
    if action == '/api/ask':
        args = ['ask', '--user', payload['user'], payload['question']]
    else:
        args = ['share', '--owner', 'alice', '--to', 'bob']
    env = os.environ.copy()
    # The server may come from a worktree; the CLI must use the launch cwd's code/state.
    env.pop('PYTHONPATH', None)
    result = subprocess.run([sys.executable, '-m', 'brain.cli', *args],
                            capture_output=True, text=True, timeout=180, env=env)
    if result.returncode:
        raise RuntimeError('Backend operation failed')
    # Some SDKs log to stdout. Accept the final JSON object, never return raw logs.
    decoder = json.JSONDecoder()
    for offset, char in enumerate(result.stdout):
        if char != '{':
            continue
        try:
            value, end = decoder.raw_decode(result.stdout[offset:])
            if isinstance(value, dict) and not result.stdout[offset + end:].strip():
                return value
        except ValueError:
            pass
    raise RuntimeError('Backend response was not JSON')


class Handler(BaseHTTPRequestHandler):
    backend = staticmethod(run_backend)

    def log_message(self, *_):
        pass

    def send_data(self, status, value, content_type='application/json'):
        data = value.encode() if isinstance(value, str) else json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)

    def local_request(self):
        port = self.server.server_address[1]
        allowed = {f'127.0.0.1:{port}', f'localhost:{port}'}
        host = self.headers.get('Host', '')
        origin = self.headers.get('Origin')
        return host in allowed and (origin is None or origin == f'http://{host}')

    def do_GET(self):
        if not self.local_request():
            return self.send_data(403, {'error': 'Local requests only.'})
        if self.path != '/':
            return self.send_data(404, {'error': 'Not found.'})
        self.send_data(200, Path(__file__).with_suffix('.html').read_text(), 'text/html; charset=utf-8')

    def do_POST(self):
        if not self.local_request():
            return self.send_data(403, {'error': 'Local requests only.'})
        if self.path not in {'/api/ask', '/api/share'}:
            return self.send_data(404, {'error': 'Not found.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 8192 or self.headers.get('Content-Type') != 'application/json':
                raise ValueError()
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError()
            if self.path == '/api/ask':
                if payload.get('user') not in {'alice', 'bob'}:
                    raise ValueError()
                question = payload.get('question')
                if not isinstance(question, str) or not question.strip() or len(question) > 2000:
                    raise ValueError()
            elif payload.get('confirm') != 'share-alice-with-bob':
                raise ValueError()
        except (ValueError, TypeError):
            return self.send_data(400, {'error': 'Check the question, user, or sharing confirmation.'})
        if not _LOCK.acquire(blocking=False):
            return self.send_data(409, {'error': 'Another request is running. Please wait and try again.'})
        try:
            result = self.backend(self.path, payload)
            self.send_data(200, result)
        except Exception:
            self.send_data(502, {'error': 'The brain could not complete this request. Check local service configuration and try again.'})
        finally:
            _LOCK.release()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Brainy demo: http://127.0.0.1:{server.server_address[1]}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
