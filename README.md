# Iran Conflict Intelligence Dashboard

A self-refreshing geopolitical dashboard that auto-fetches the latest Iran conflict
news every day at 07:00 UK time using Claude AI with web search.

---

## How it works

```
07:00 UK time
     │
     ▼
GitHub Actions cron job
     │  runs fetch_news.py
     ▼
Claude API (claude-opus-4-6 + web search)
     │  returns 8 articles as JSON
     ▼
docs/news.json  ◄── committed back to repo
     │
     ▼
GitHub Pages serves index.html
     │  fetches news.json on load
     ▼
Dashboard renders with fresh articles
```

---

## Setup (one-time, ~10 minutes)

### 1. Fork or clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/iran-dashboard.git
cd iran-dashboard
```

### 2. Add your Anthropic API key as a GitHub Secret

1. Go to your repo on GitHub
2. Click **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: your key from https://console.anthropic.com

### 3. Enable GitHub Pages

1. Go to **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / folder: `/docs`
4. Click **Save**

Your dashboard will be live at:
`https://YOUR_USERNAME.github.io/iran-dashboard/`

### 4. Update the news.json URL in index.html

Open `docs/index.html` and find this line near the top of the `<script>` block:

```js
const NEWS_JSON_URL = "./news.json";
```

Change it to your full GitHub Pages URL:

```js
const NEWS_JSON_URL = "https://YOUR_USERNAME.github.io/iran-dashboard/news.json";
```

Commit and push.

### 5. Test the workflow manually

1. Go to **Actions** tab in your GitHub repo
2. Click **Daily news refresh**
3. Click **Run workflow → Run workflow**
4. Watch it fetch news and commit an updated `docs/news.json`

---

## BST / GMT automatic handling

The cron is set to `0 6 * * *` (06:00 UTC), which equals 07:00 BST (British Summer Time, UTC+1).

In winter when the UK returns to GMT (UTC+0), update the cron to `0 7 * * *` in
`.github/workflows/refresh-news.yml`.

---

## Running locally

```bash
# Install dependencies
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run the fetch script
python fetch_news.py

# Open the dashboard
open docs/index.html
```

---

## File structure

```
iran-dashboard/
├── .github/
│   └── workflows/
│       └── refresh-news.yml   # GitHub Actions cron job
├── docs/                      # GitHub Pages root
│   ├── index.html             # The full dashboard
│   └── news.json              # Auto-updated daily by the workflow
├── fetch_news.py              # Claude API fetch script
└── README.md
```

---

## Customising the news prompt

Edit the `SYSTEM_PROMPT` and `USER_PROMPT` strings in `fetch_news.py` to change:
- The number of articles (default: 8)
- The regional focus (currently emphasises Lebanon, Gulf states, Iran internally)
- The scenario labels articles are tagged to
- The topic entirely (swap Iran conflict for any other subject)
