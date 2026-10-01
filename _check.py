"""Dev-only link checker. Deleted right after verification; not part of the deployed site."""

import re
import sys
from collections import deque
from urllib.parse import urljoin
from urllib.request import urlopen, Request

BASE = sys.argv[1]
HREF = re.compile(r'href="([^"]+)"', re.IGNORECASE)


def fetch(url):
    try:
        with urlopen(Request(url), timeout=5) as r:
            ctype = r.headers.get("Content-Type", "")
            return r.status, ctype, (r.read() if "html" in ctype else b"")
    except Exception as exc:  # noqa: BLE001
        return getattr(exc, "code", "ERR"), str(exc), b""


seen, broken, ok = set(), [], 0
queue = deque([urljoin(BASE, "index.html")])
while queue:
    url = queue.popleft()
    if url in seen:
        continue
    seen.add(url)
    status, ctype, body = fetch(url)
    tag = "PDF " if "pdf" in ctype else "HTML" if "html" in ctype else "????"
    if status != 200:
        broken.append(f"[{status}] {tag} {url}")
        print("  BROKEN " + broken[-1])
        continue
    ok += 1
    print(f"  ok [{status}] {tag} {url}")
    if "html" in ctype:
        for href in HREF.findall(body.decode("utf-8", "ignore")):
            if href.startswith(("http://", "https://")) and not href.startswith(BASE):
                print(f"     (external, skipped) {href}")
                continue
            t = urljoin(url, href)
            if t.startswith(BASE) and t not in seen:
                queue.append(t)

print(f"\n=== 200 OK: {ok}   broken: {len(broken)} ===")
for b in broken:
    print("  " + b)
sys.exit(1 if broken else 0)
