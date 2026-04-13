# 🔬 AI Tools Radar

> Daily intelligence on AI-powered research tools — auto-updated via GitHub Actions.

## 🌐 Live Site

👉 **[https://wangjian945.github.io/AI-tools-radar/](https://wangjian945.github.io/AI-tools-radar/)**

## How It Works

```
[GitHub + arXiv] → [LLM Processing] → [Monash-style HTML] → [GitHub Pages]
      ↑                    ↑                    ↑                   ↑
  Daily scan          Auto-classify        Styled cards        Auto-deploy
```

### Pipeline Steps

1. **Collect** — Scans GitHub Trending + arXiv for new AI research tools
2. **Process** — LLM classifies tools into categories, generates summaries
3. **Render** — Generates a clean, Monash University-style HTML page
4. **Deploy** — Automatically published to GitHub Pages

## Categories

- 📚 Literature Review
- 📊 Data Analysis
- ✍️ Writing & Drafting
- 📈 Visualization
- 💬 Peer Review
- 💻 Coding & Dev
- 🧪 Experiment Design

## Schedule

Runs daily at **08:00 Beijing Time** (00:00 UTC) via GitHub Actions.

You can also trigger manually: **Actions** tab → **Daily AI Tools Update** → **Run workflow**.

## Local Development

```bash
pip install -r requirements.txt
python scripts/pipeline.py
# Open site/index.html in browser
```

## License

All rights reserved.
