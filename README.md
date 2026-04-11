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

![My Contributions](https://falling-sand.onrender.com/gif?username=7echkilla&token=dec5744486a0d0d8fd6c71f6d5cf175a3158003b9081fa01d7c3cbeca6073314) 