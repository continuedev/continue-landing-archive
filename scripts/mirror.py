#!/usr/bin/env python3
"""Mirror https://www.continue.dev/ into a fully static site directory.

Keeps index.html byte-identical to production except for one appended
<style> tag that hides sign-in links (removing them from the DOM would be
undone by React hydration).
"""
import os
import re
import sys
import urllib.request

BASE = "https://www.continue.dev"
OUT = "/Users/nate/gh/continuedev/continue-landing"

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


def fetch(url, binary=True):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
        ctype = r.headers.get("Content-Type", "")
    return data, ctype


def save(relpath, data):
    relpath = relpath.lstrip("/")
    dest = os.path.join(OUT, relpath)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    return dest


def main():
    html_bytes, _ = fetch(BASE + "/")
    html = html_bytes.decode("utf-8")
    print(f"fetched index: {len(html)} bytes")

    # --- collect root-relative asset refs from HTML (path part only) ---
    refs = set()
    for m in re.finditer(r'(?:src|href)="(/[^"]+)"', html):
        u = m.group(1)
        if u.startswith("/_next/image"):
            continue  # handled separately
        if u in ("/", "/export"):
            continue
        refs.add(u.split("?")[0])

    # --- download queue with recursive scan of js/css ---
    downloaded = {}
    queue = sorted(refs)
    while queue:
        path = queue.pop()
        if path in downloaded:
            continue
        url = BASE + path
        try:
            data, ctype = fetch(url)
        except Exception as e:
            print(f"WARN failed {path}: {e}")
            continue
        downloaded[path] = len(data)
        save(path, data)
        # scan js/css for further chunk/media references
        if path.endswith(".js") or path.endswith(".css"):
            text = data.decode("utf-8", errors="ignore")
            for m in re.finditer(r'static/(?:chunks|media)/[A-Za-z0-9._\-]+\.(?:js|css|woff2|woff|ttf|png|jpg|jpeg|svg|gif|webp|avif|mp4|ico)', text):
                sub = "/_next/" + m.group(0)
                if sub not in downloaded:
                    queue.append(sub)
            # css url() refs
            if path.endswith(".css"):
                for m in re.finditer(r'url\(([^)]+)\)', text):
                    u = m.group(1).strip("'\"")
                    if u.startswith("data:") or u.startswith("http"):
                        continue
                    if u.startswith("/"):
                        sub = u.split("?")[0].split("#")[0]
                    else:
                        base_dir = os.path.dirname(path)
                        sub = os.path.normpath(os.path.join(base_dir, u.split("?")[0].split("#")[0]))
                        if not sub.startswith("/"):
                            sub = "/" + sub
                    if sub not in downloaded:
                        queue.append(sub)

    print(f"downloaded {len(downloaded)} assets")

    # --- hero image served via /_next/image optimizer ---
    # All srcset variants share the path /_next/image (query ignored by static
    # hosts), so store the highest-resolution variant at that literal path.
    hero_q = "/_next/image?url=https%3A%2F%2Fha51p4k2fb4na0qd.public.blob.vercel-storage.com%2Fblog%2Fsecurity-chores-cloud-agents%2Fhero.png&w=3840&q=75"
    data, ctype = fetch(BASE + hero_q)
    save("/_next/image", data)
    print(f"hero image: {len(data)} bytes, content-type {ctype}")

    # --- write index.html with appended hide-signin style ---
    hide = ('<style id="static-mirror-hide-signin">'
            'a[href="/export"],a[href^="https://app.continue.dev"]{display:none !important}'
            "</style>")
    assert "</body></html>" in html
    out_html = html.replace("</body></html>", hide + "</body></html>")
    save("/index.html", out_html.encode("utf-8"))
    print("wrote index.html (+hide style)")

    # sanity: report where sign-in / export appear
    for pat in ["/export", "app.continue.dev", "Sign in"]:
        print(f"index.html occurrences of {pat!r}:", out_html.count(pat))


if __name__ == "__main__":
    main()
