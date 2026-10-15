# Explosive Content

**Stop guessing what to record. Find the YouTube topics strangers already watch.**

One B2B lead generation video: 447,348 views. Its channel: 10,300 subscribers. That gap is the topic you want. 🌴

You run a B2B company. You know video brings leads. And recording time is the first thing your calendar eats. 🐬

So you pick a topic that feels important, record it, publish it.. and the views come mostly from people who already know you. The comments stay quiet. An afternoon gone. No new conversations.

That's not a talent problem. It's a guessing problem, and guessing gets stale fast. The market already tells you what it wants to watch. You just need to know where to look.

Picture a search results page. Look for a video with **more views than its channel has subscribers**. A channel with 1,000 subscribers, one video with 3,000 views. Who watched the other 2,000? Strangers. The fans didn't do that. The **topic** did. Right now a channel smaller than yours may be pulling in the strangers you want. 🐯

This free Claude Code skill hunts for exactly that, keyword by keyword. It searches YouTube for the phrases you want to be found for, keeps the videos that beat their own channel, throws out the noise (Shorts, paid ads, tiny channels), and hands you one proven topic per keyword. Then it writes the script. Your afternoon goes into a topic with evidence behind it, not hope. 🐬

Free. No sign-up. Built for B2B topics (change two word lists in `keywords.json` for any other market). Not for you if you want dance trends or viral pranks.

## We ran it on our own business first

25 B2B sales keywords. 20 came back explosive. 3 came back dead.

| # | Keyword | Reach (views ÷ subscribers) |
|---|---|---|
| 1 | B2B lead generation | 43x |
| 2 | B2B cold email | 23x |
| 3 | Build a sales pipeline | 23x |
| 4 | AI sales stack | 18x |
| 5 | B2B sales closer | 18x |
| 6 | Founder-led sales | 13x |
| 7 | B2B prospecting | 12x |
| 8 | AI GTM | 11x |
| 9 | LinkedIn prospecting | 11x |
| 10 | Control the sales conversation | 9x |

The dead ones left a bitter taste. 🐬 "Cost of inaction", "stop being needy in sales", "stop discounting". That's the heart of what we teach.. and nobody searches for it. Not one video beat its channel.

So our titles changed. The title names what the buyer wants (leads, bigger deals, a call that closes). Our method lives inside the video. Full list with every proof video: [examples/b2b-sales-2026-10.md](./examples/b2b-sales-2026-10.md). 🐯

## What you get

| You type | You get |
|---|---|
| `/explosive-content` | The full run: scan, one honest outlier per keyword, ranked table, what it tells you |
| `/explosive-content next` | The next 3 topics you haven't used yet |
| `/explosive-content script "<keyword>"` | A recording-ready script: one hook, 5 chapters, every line something you say |

## How it filters the noise

A raw "views beat subscribers" list is mostly junk. Our first pass put a product video at #1: 240,000 views on a 937-subscriber channel. Strangers didn't find that topic. An ad budget did, most likely. 🌴 So the finder keeps a video only if:

- views beat the channel's subscribers, with at least 2,000 views
- the channel has at least 500 subscribers (below that, one share skews everything)
- it's long-form, 3 minutes or more (Shorts inflate the ratio)
- likes are at least 0.3% of views (paid ads get views, not likes)
- the title is on your topic and in English, published since 2022

Then the skill (not the code) picks the one outlier per keyword that genuinely fits your buyer, and marks keywords with no honest outlier as "no proven demand yet". 🐬

## Install

```bash
git clone https://github.com/SimonTheSalesBooster/explosive-content ~/explosive-content
cp ~/explosive-content/explosive-content.md ~/.claude/commands/
python3 ~/explosive-content/tools/explosive_content.py --selftest
```

Plain Python, no dependencies. The self-test runs known-good videos that must pass and known-bad ones (Shorts, ads, tiny channels, off-topic, non-English, your own channel) that must be caught.

Then put your own phrases in `keywords.json` and type `/explosive-content`. One run gives you your own ranked list, your dead keywords, and a script for the topic at the top. 🐯 Run it again every month: topics cool down, new ones heat up.

### Get a free YouTube API key

1. Go to https://console.cloud.google.com and create a project (free).
2. Search "YouTube Data API v3", click **Enable**.
3. **Credentials** → **Create credentials** → **API key**.
4. `export YOUTUBE_API_KEY=your-key` (add it to your shell profile).

The free quota is 10,000 units a day. A full run of 25 keywords uses about 5,000.

## What's in the repo

| File | What it is |
|---|---|
| `explosive-content.md` | The skill: scan, judge, briefs, scripts, ✅/❌ tracking |
| `tools/explosive_content.py` | The finder: YouTube search, filters, ranking, self-test |
| `keywords.json` | Our 25 B2B sales keywords. Replace them with yours |
| `examples/b2b-sales-2026-10.md` | Our real October 2026 run, every proof video linked |
| `explosive-content-guide.pdf` | The method and our top 10 on 2 printable pages |

---

## Who made this

**[Strategy Sprints](https://www.strategysprints.com)**, Simon Severino. We help B2B founders take control of the sales conversation. 2,400+ founders have gone through our programs. 🐯

Want more skills like this, plus a community of owners to use them with? 🌴 Join the Sprint Club: https://www.strategysprints.com
