# continuedev.github.io

Redirect stub: https://continuedev.github.io/ → https://continue.dev/

The continue.dev sites are served by GitHub Pages from these repos:

| Host | Repo |
| --- | --- |
| continue.dev | [`continue-home`](https://github.com/continuedev/continue-home) |
| docs.continue.dev | [`continue`](https://github.com/continuedev/continue) (`docs-site/`, deployed by `.github/workflows/docs-gh-pages.yml`) |
| blog.continue.dev | [`continue-blog`](https://github.com/continuedev/continue-blog) (Astro) |

This org-site repo exists only so the bare `continuedev.github.io` URL doesn't
serve a stale duplicate of the homepage. It previously held the first static
mirror of the front page (see git history) before `continue-home` became
canonical.
