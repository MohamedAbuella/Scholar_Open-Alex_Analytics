#!/usr/bin/env python3
"""Local helper: serves the dashboard, queries Google Scholar, saves .bib files. Python 3 stdlib only."""
import http.server, urllib.request, urllib.parse, json, re, os, html, webbrowser, threading
ROOT = os.path.dirname(os.path.abspath(__file__)); PORT = 8000
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
      'Accept-Language': 'en-US,en;q=0.9', 'Accept': 'text/html,application/xhtml+xml',
      # pre-accepted cookie consent (UK/EU visitors otherwise get a consent page instead of results)
      'Cookie': 'CONSENT=YES+cb; SOCS=CAESHAgBEhJnd3NfMjAyMzA4MTAtMF9SQzIaAmVuIAEaBgiAo_CmBg'}
strip = lambda s: html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None
import queue, time
JOBS = queue.Queue()

def browser_worker():
    """One real browser window (your installed Edge/Chrome) does all Scholar requests, so Google's
    'Verifying...' JavaScript check passes. A CAPTCHA, if shown, is solved by you in that window."""
    with sync_playwright() as p:
        ctx = None
        for ch in ('msedge', 'chrome', None):
            try:
                kw = dict(user_data_dir=os.path.join(ROOT, '.browser_profile'), headless=False, locale='en-US')
                if ch: kw['channel'] = ch
                ctx = p.chromium.launch_persistent_context(**kw); break
            except Exception as e:
                print('Browser launch failed (%s): %s' % (ch, str(e)[:120]))
        if not ctx: print('No browser could be started.'); return
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        print('Browser window ready - keep it open (you may minimise it).')
        while True:
            url, box, ev = JOBS.get()
            try:
                if 'scholar.bib' in url:
                    box.append(ctx.request.get(url).text())
                else:
                    page.goto(url, wait_until='domcontentloaded', timeout=60000)
                    for _ in range(180):   # up to 3 min: verification page / CAPTCHA resolves, results appear
                        h = page.content()
                        if 'gs_or' in h or 'did not match any' in h or 'scholar.bib' in h or 'gs_res_ccl' in h and 'Verifying' not in h and 'gs_captcha' not in h: break
                        time.sleep(1)
                    box.append(h)
            except Exception as e:
                box.append('')
            ev.set()

def get(url):
    if not sync_playwright: return ''
    box, ev = [], threading.Event(); JOBS.put((url, box, ev)); ev.wait(300)
    return box[0] if box else ''

def parse(page):
    if 'CAPTCHA' == page or 'gs_captcha' in page or 'unusual traffic' in page: return {'captcha': True, 'items': []}
    items = []
    for b in re.split(r'(?=<div[^>]*class="[^"]*\bgs_or\b)', page):
        t = re.search(r'<h3 class="gs_rt"[^>]*>(.*?)</h3>', b, re.S)
        if not t or 'gs_or' not in b[:300]: continue
        a = re.search(r'<a href="([^"]+)"', t.group(1))
        title = re.sub(r'^\[(PDF|HTML|BOOK|B|CITATION)\]\s*', '', strip(re.sub(r'<span class="gs_ctg2">.*?</span>', '', t.group(1))))
        meta = strip((re.search(r'<div class="gs_a">(.*?)</div>', b, re.S) or [0, ''])[1])
        parts = meta.split(' - ')
        y = re.search(r'\b(19|20)\d\d\b', parts[1] if len(parts) > 1 else meta)
        cid = re.search(r'data-cid="([^"]+)"', b)
        c = re.search(r'Cited by (\d+)', b)
        items.append({'cid': cid.group(1) if cid else '', 'title': title, 'url': a.group(1) if a else '',
                      'authors': parts[0], 'venue': re.sub(r',?\s*(19|20)\d\d$', '', parts[1]).strip() if len(parts) > 1 else '',
                      'year': int(y.group(0)) if y else 0, 'snippet': strip((re.search(r'<div class="gs_rs">(.*?)</div>', b, re.S) or [0, ''])[1]),
                      'cites': int(c.group(1)) if c else 0})
    note = ''
    if not items:
        open(os.path.join(ROOT, 'scholar_debug.html'), 'w', encoding='utf-8').write(page)
        ti = re.search(r'<title[^>]*>(.*?)</title>', page, re.S)
        note = 'Page received (%d bytes), title: "%s". Saved as scholar_debug.html' % (len(page), strip(ti.group(1)) if ti else 'none')
    return {'captcha': False, 'items': items, 'note': note}

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a): pass
    def send_json(self, o):
        d = json.dumps(o).encode(); self.send_response(200)
        self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(d))); self.end_headers(); self.wfile.write(d)
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
        if u.path == '/api/ping': return self.send_json({'ok': True})
        if u.path == '/api/bibs': return self.send_json(sorted(f for f in os.listdir(ROOT) if f.lower().endswith('.bib')))
        if u.path == '/api/search':
            prm = {'q': q.get('q', ''), 'start': q.get('start', 0), 'hl': 'en', 'as_sdt': '0,5', 'as_ylo': q.get('lo', ''), 'as_yhi': q.get('hi', '')}
            for k in ('as_sauthors', 'as_publication', 'as_epq', 'as_oq', 'as_eq', 'as_occt', 'as_rr'):   # advanced options
                if q.get(k): prm[k] = q[k]
            url = 'https://scholar.google.com/scholar?' + urllib.parse.urlencode(prm)
            if not sync_playwright: return self.send_json({'captcha': False, 'items': [], 'note': 'Playwright is not installed. Run:  python -m pip install playwright'})
            return self.send_json(parse(get(url)))
        if u.path == '/api/bibtex':
            p = get('https://scholar.google.com/scholar?q=info:%s:scholar.google.com/&output=cite&hl=en' % q['cid'])
            m = re.search(r'href="(https://scholar\.googleusercontent\.com/scholar\.bib[^"]+)"', p)
            return self.send_json({'bib': get(html.unescape(m.group(1))) if m else '', 'captcha': p == 'CAPTCHA' or 'gs_captcha' in p})
        super().do_GET()
    def do_POST(self):
        name = os.path.basename(urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get('name', ['Scholar_Collection.bib'])[0])
        body = self.rfile.read(int(self.headers['Content-Length']))
        open(os.path.join(ROOT, name), 'wb').write(body); self.send_json({'saved': name})

if __name__ == '__main__':
    if sync_playwright: threading.Thread(target=browser_worker, daemon=True).start()
    threading.Timer(1, lambda: webbrowser.open('http://localhost:%d/index.html' % PORT)).start()
    print('Dashboard: http://localhost:%d/index.html  (Ctrl+C to stop)' % PORT)
    http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
