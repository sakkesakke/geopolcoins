# Shorts maker

Makes a 26-second vertical Short (1080x1920) with Jean-Phil from one entry in `topics.json`.
Everything is drawn in code (pixel sprite, Jersey 10 font, chiptune made with numpy), so there are no stock assets or licenses to track.

```
python3 tools/shorts/make_short.py next            # first topic without "posted"
python3 tools/shorts/make_short.py scam-dms out/   # a specific topic
```

Output: `<id>.mp4` and `<id>_check.jpg` (four frames to check by eye) in `.shorts/` (git-ignored) or the folder you give.

## Posting (YouTube @geopolcoins)
1. Push the mp4 to the `media` branch so it has a raw URL:
   `https://raw.githubusercontent.com/sakkesakke/geopolcoins/media/<id>.mp4`
2. In YouTube Studio (built-in browser, already signed in by the owner) open `/videos/upload?d=ud`,
   fetch the raw URL in the page, set it on `input[name=Filedata]` with a DataTransfer, then fill
   title / description / tags from `topics.json`, "Not made for kids", altered content "No", visibility Public.
3. Set `"posted": "<date>"` on the topic and open a PR.

Rules: education only, no price talk or promises, always "Entertainment only. Not financial advice. DYOR."
