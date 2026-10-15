---
name: explosive-content
description: "Find the YouTube topics strangers watch. Searches YouTube for your keywords, keeps the videos that got MORE views than their channel has subscribers, picks one honest outlier per keyword, and turns each into a recording-ready script or article brief. Free Claude Code skill by Strategy Sprints."
---

# /explosive-content: find the topics strangers watch

A video that gets 3,000 views on a channel with 1,000 subscribers reached people who never subscribed. The creator's fans didn't do that. The **topic** did. That's the signal this skill hunts for, keyword by keyword, so you record what your market already wants to watch.

Usage:
- `/explosive-content`: full run (scan, judge, briefs).
- `/explosive-content next`: read the last run and give me the next 3 topics I haven't used.
- `/explosive-content script "<keyword>"`: write the script for one topic from the last run.

## Step 0: Setup (first run only)
1. The user needs a free YouTube Data API key in the env var `YOUTUBE_API_KEY` (README: "Get a free YouTube API key"). If it's missing, stop and show those steps.
2. `python3 tools/explosive_content.py --selftest` must print `selftest PASS`.
3. Ask for (or read) `keywords.json`: 15-25 phrases the user wants to be found for, in the words their buyer types. Mix what buyers WANT ("more leads", "close bigger deals") with what the user teaches. Add `exclude_channels` (their own channel IDs). Outside B2B sales, set `topic_terms` / `off_topic_terms` to their market's words.

## Step 1: Scan (code)
```bash
python3 tools/explosive_content.py --keywords keywords.json --out runs
```
Rules built in: views > channel subscribers, channel >= 500 subscribers, >= 2,000 views, >= 3 minutes (Shorts inflate the ratio), published since 2022, English, title on-topic, likes >= 0.3% of views (promoted ads get views without likes). Quota: about 5,000 of the free 10,000 daily units for 25 keywords; a same-day rerun reads the search cache and costs nothing. On HTTP 403/429 quota errors: stop, rerun tomorrow, say so.

## Step 2: Judge (you, not code)
Read `runs/latest.json` → `per_keyword`. The code filter is coarse on purpose. For each keyword pick the ONE outlier that is genuinely about the user's topic for the user's buyer:
- Drop reuploads of someone else's content, tool ads dressed as tutorials, consumer or street sales when the user sells B2B, job-seeker videos.
- Prefer a higher ratio, then the closer fit to the user's buyer.
- One video per keyword. Rank by ratio. Keep the top 20.
- A keyword with no honest outlier goes to **"No proven demand yet"**. That is a finding, not a gap to fill with a weak pick. (In our own run, the problems we solve had zero demand while the outcomes buyers want exploded. Put the want in the title, the method inside the video.)

Show the user the ranked table: keyword, ratio, views / subscribers, proof video link, channel. Then 3 lines: what it tells them.

## Step 3: Briefs and scripts
For each pick (or the one the user names), write a brief: SEO title (50-70 characters, keyword first), the angle the outlier proves, and what the user adds that the outlier lacks (their method, their numbers, their story).

When the user wants the full script, the default format is:
- **One hook**: 3-6 spoken lines. The viewer's problem in their words, then the promise. The keyword is spoken out loud.
- **Exactly 5 chapters** with `##` headings that work as YouTube chapter titles: under 50 characters, each names what the viewer gets.
- **Every line is something you say.** No timestamps, no "[B-roll]", no production notes.
- **~1,100-1,400 words** (about 10 minutes).
- **Two calls to action**: one in the middle, one at the end. Nothing else.
- Make it concrete: a scene, a person or a number in every chapter. If a person is made up, say so on tape. Never invent results.

For an article instead of a video: same title, the hook becomes a 40-90 word direct answer in the first paragraph, the 5 chapters become 5 sections.

## Step 4: Track (✅/❌)
Log every published piece in `runs/used.md` (keyword, title, link, date). After 30 days compare its views with the user's channel median: above = ✅ (make a second video on that keyword), below = ❌ (don't repeat the angle). Rerun the scan monthly; topics cool down and new ones heat up.

## Never
- Never call a keyword hot from one lucky video. One outlier per keyword is a lead, two keywords pointing the same way is a pattern.
- Never copy the outlier's content. Copy the topic, bring your own method.
