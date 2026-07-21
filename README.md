# continuedev.github.io

Fully static mirror of the **continue.dev** front page ("We have some big news"),
served from GitHub Pages so the Next.js app behind it can be shut down.

The page is byte-identical to the production homepage (HTML, CSS, JS chunks,
fonts, artwork) with exactly one addition: a `<style>` tag appended before
`</body>` that hides the "Sign in" link (`a[href="/export"]`), since the
sign-in/export flow is being retired. Everything else — image, copy, layout,
CSS — is untouched.

This repo is named `continuedev.github.io` (GitHub's org-site convention) so
Pages serves it from the **root** of https://continuedev.github.io/. That
matters: the mirrored HTML and JS reference assets by root-relative paths
(`/_next/...`), which 404 on a project-page sub-path but work at a domain
root — both on the github.io URL for verification and on continue.dev after
DNS cutover.

## Contents

- `index.html` — production HTML + the one hide-sign-in style tag
- `_next/` — all static chunks, fonts, and the hero artwork
  (`_next/image` is a literal file name; browsers request
  `/_next/image?url=...&w=...`, static hosts ignore the query string, so every
  srcset variant resolves to this one high-res PNG)
- `continue-logo-black.svg`, `favicon.png`, `icon-192.png`, `icon-512.png`,
  `noise.png`, `manifest.webmanifest` — root assets
- `_vercel/speed-insights/script.js` — empty stub so the Vercel analytics
  loader doesn't 404 in consoles/logs
- `scripts/mirror.py` — the script that produced this mirror; re-run it if the
  production page changes before DNS cutover
- `.nojekyll` — required: Jekyll would otherwise ignore the underscore-prefixed
  `_next/` and `_vercel/` directories

## Local preview

```bash
python3 -m http.server 8080
# open http://127.0.0.1:8080
```

## Verify, then cut over DNS

1. Verify the live mirror at https://continuedev.github.io/ — it should be
   pixel-identical to https://continue.dev/ minus the Sign in link.
2. In **Settings → Pages → Custom domain**, enter `continue.dev` (this commits
   a `CNAME` file). Verify the domain under org settings if prompted.
3. Change DNS where the `continue.dev` zone is managed (currently Vercel
   nameservers, `vercel-dns-016.com`):

```
A     continue.dev   185.199.108.153
A     continue.dev   185.199.109.153
A     continue.dev   185.199.110.153
A     continue.dev   185.199.111.153
AAAA  continue.dev   2606:50c0:8000::153
AAAA  continue.dev   2606:50c0:8001::153
AAAA  continue.dev   2606:50c0:8002::153
AAAA  continue.dev   2606:50c0:8003::153
CNAME www            continuedev.github.io.
```

4. Back in **Settings → Pages**, enable **Enforce HTTPS** once the certificate
   is issued (can take a few minutes after DNS propagates).

## Refreshing the mirror

```bash
python3 scripts/mirror.py   # re-downloads HTML + all assets from production
```
