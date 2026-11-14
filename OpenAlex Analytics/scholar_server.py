#!/usr/bin/env python3
"""Optional local helper: serves this folder and lets the dashboard auto-save the .bib file. Python 3 stdlib only."""
import http.server, urllib.parse, json, os, webbrowser, threading
ROOT = os.path.dirname(os.path.abspath(__file__)); PORT = 8000
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a): pass
    def send_json(self, o):
        d = json.dumps(o).encode(); self.send_response(200)
        self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(d))); self.end_headers(); self.wfile.write(d)
    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path
        if p == '/api/ping': return self.send_json({'ok': True})
        if p == '/api/bibs': return self.send_json(sorted(f for f in os.listdir(ROOT) if f.lower().endswith('.bib')))
        super().do_GET()
    def do_POST(self):
        name = os.path.basename(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('name', ['OpenAlex_Collection.bib'])[0])
        open(os.path.join(ROOT, name), 'wb').write(self.rfile.read(int(self.headers['Content-Length']))); self.send_json({'saved': name})
if __name__ == '__main__':
    threading.Timer(1, lambda: webbrowser.open('http://localhost:%d/index.html' % PORT)).start()
    print('Dashboard: http://localhost:%d/index.html  (Ctrl+C to stop)' % PORT)
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
