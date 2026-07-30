# Self-Hosted GitHub Stats — Setup Guide

Public github-readme-stats instances are shared by thousands of profiles and constantly hit
GitHub's API rate limit, so cards silently fail. This deploys your own private instance on
Vercel's free tier — same visuals, no rate-limit roulette.

## Step 1 — Create a GitHub token

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. **Generate new token (classic)**
3. Scopes: check **repo** and **read:user**
4. Expiration: "No expiration" is simplest, but means it never rotates — if you'd rather rotate
   periodically, pick 90 days and set a reminder
5. Click Generate, then **copy the token immediately** — GitHub only shows it once

⚠️ Never commit this token to a repo, paste it in a README, or share it anywhere public. Treat
it like a password.

## Step 2 — Fork the stats repo

Fork **[anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats)**
into your own account. Forking (rather than just using the public instance) is what lets you
deploy your own copy with your own token and your own rate limit.

## Step 3 — Deploy to Vercel

1. Go to [vercel.com](https://vercel.com), sign in with GitHub
2. **Add New Project** → import your fork of `github-readme-stats`
3. Framework preset: leave as detected. Plan: **Hobby** (free)
4. Before deploying, add an environment variable:
   - Key: `PAT_1`
   - Value: the token you copied in Step 1
5. Click **Deploy**

Vercel will give you a URL like `https://github-readme-stats-yourname.vercel.app`.

## Step 4 — Verify

Visit these in your browser (swap in your real domain and username):

- `https://YOUR-INSTANCE.vercel.app/api?username=anis-09` — should render a stats card
- `https://YOUR-INSTANCE.vercel.app/api/top-langs/?username=anis-09` — should render languages
- If either shows an error image instead of a card, check: token is set correctly, token has
  `repo` + `read:user` scopes, and the environment variable name is exactly `PAT_1`

## Step 5 — Drop the URL into the README

Open `README.md` and replace every `YOUR-STATS-INSTANCE` with your actual Vercel domain, e.g.:

```
https://github-readme-stats-yourname.vercel.app/api?username=anis-09&show_icons=true&hide_border=true&bg_color=09090B&title_color=7C3AED&icon_color=22D3EE&text_color=F8FAFC&hide_rank=true
```

`hide_rank=true` is included on purpose — the rank badge is weighted heavily toward star count
and total contributions, which makes it look unfairly low on a newer account. The stats
themselves are more representative without it.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Card shows "Something went wrong" | Token missing or wrong scopes — recheck Step 1 |
| Card shows old data | Vercel/browser cache — GitHub itself also caches embedded images for a few hours, this is normal and not a bug |
| 404 on the Vercel URL | Deployment failed — check the Vercel build log for the specific error |
| Works locally, not on GitHub | README is pointing at `localhost` or an old preview URL instead of the production domain |

## Cache behavior

Both Vercel and GitHub's own image proxy cache these SVGs for a period of time — that's a
performance feature (it keeps you well under any API limits), not a fault. If you update your
theme colors and don't see the change immediately, wait a few minutes or append `&cache_seconds=0`
temporarily while testing.
