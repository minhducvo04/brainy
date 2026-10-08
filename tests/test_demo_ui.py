import http.client
import json
import threading
from http.server import ThreadingHTTPServer

import pytest
from brain.demo_ui import Handler


@pytest.fixture
def server():
    calls = []
    class FakeHandler(Handler):
        @staticmethod
        def backend(action, payload):
            calls.append((action, payload))
            if payload.get('question') == 'fail':
                raise RuntimeError('SECRET must not escape')
            return {'answer': 'A cited answer', 'sources': ['source:slack'], 'datasets': ['alice-brain']}
    instance = ThreadingHTTPServer(('127.0.0.1', 0), FakeHandler)
    worker = threading.Thread(target=instance.serve_forever, daemon=True)
    worker.start()
    yield instance, calls
    instance.shutdown()
    instance.server_close()
    worker.join()


def request(server, path, body=None, origin=None):
    connection = http.client.HTTPConnection(*server.server_address)
    headers = {'Content-Type': 'application/json'}
    if origin:
        headers['Origin'] = origin
    connection.request('GET' if body is None else 'POST', path,
                       None if body is None else json.dumps(body), headers)
    response = connection.getresponse()
    status, content = response.status, response.read().decode()
    connection.close()
    return status, content


def test_http_ui_ask_and_confirmed_share(server):
    instance, calls = server
    status, page = request(instance, '/')
    assert status == 200 and 'Ask Brainy' in page
    status, answer = request(instance, '/api/ask', {'user': 'alice', 'question': 'why?'})
    assert status == 200 and json.loads(answer)['sources'] == ['source:slack']
    assert request(instance, '/api/share', {'confirm': 'no'})[0] == 400
    assert len(calls) == 1
    assert request(instance, '/api/share', {'confirm': 'share-alice-with-bob'})[0] == 200
    assert len(calls) == 2


def test_http_rejects_foreign_origin_unknown_user_and_hides_error(server):
    instance, calls = server
    assert request(instance, '/api/ask', {'user': 'alice', 'question': 'why?'}, 'https://evil.example')[0] == 403
    assert request(instance, '/api/ask', {'user': 'carol', 'question': 'why?'})[0] == 400
    assert not calls
    status, error = request(instance, '/api/ask', {'user': 'alice', 'question': 'fail'})
    assert status == 502 and 'SECRET' not in error
    assert request(instance, '/../../README.md')[0] == 404
