# Falling Sand

Animate GitHub contributions

The project uses GitHub's GraphQL API over REST API.

```
app/
  routes.py        → HTTP endpoints only
  github.py        → GitHub API + OAuth exchange
  db.py            → persistence (SQLite)
  auth.py          → OPTIONAL (we’ll add clean helpers)
  gif.py           → image generation
  __init__.py      → app setup
```
