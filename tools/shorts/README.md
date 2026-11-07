# Shorts maker

Makes a 26-second vertical Short (1080x1920) with Jean-Phil from one entry in `topics.json`.
Everything is drawn in code (pixel sprite, Jersey 10 font, chiptune made with numpy), so there are no stock assets or licenses to track.

```
python3 tools/shorts/make_short.py next            # first topic without "posted"
python3 tools/shorts/make_short.py scam-dms out/   # a specific topic
```

Languages: set `"lang"` on a topic (en, nl, fr, es, de, pt, id). Accents are stripped only on the big pixel plates (the pixel font has none); speech bubbles keep them.
Ready-made videos: a topic with `"video": "file.mp4"` is not rendered; that file on the `media` branch is uploaded as is.

Output: `<id>.mp4` and `<id>_check.jpg` (four frames to check by eye) in `.shorts/` (git-ignored) or the folder you give.

## Posting (YouTube @geopolcoins)
1. Push the mp4 to the `media` branch so it has a raw URL:
   `https://raw.githubusercontent.com/sakkesakke/geopolcoins/media/<id>.mp4`
2. In YouTube Studio (built-in browser, already signed in by the owner) open `/videos/upload?d=ud`,
   fetch the raw URL in the page, set it on `input[name=Filedata]` with a DataTransfer, then fill
   title / description / tags from `topics.json`, "Not made for kids", altered content "No", visibility Public.
3. Set `"posted": "<date>"` on the topic and open a PR.

Rules: education only, no price talk or promises, always "Entertainment only. Not financial advice. DYOR."

## Voice (human-like narration)
`.github/workflows/voice.yml` (run it from the Actions tab or the API, input `ids` = `queue` or a list) renders the topics,
then `voice.py` lets Jean-Phil read his speech bubbles with **Chatterbox Multilingual** by Resemble AI
(MIT, https://github.com/resemble-ai/chatterbox), music ducked under the voice.
The voice is spoken first at a calm pace; the scenes then stretch to fit it (`<id>.timing.json`, read by make_short.py
and score.py), so nothing is sped up. Input `voice` = `default` (Chatterbox's own voice) or a clip in `voices/`.
Those clips come from synthetic **Kokoro** voices (hexgrad/kokoro, Apache-2.0) via `make_voices.py`; run
`voice-samples.yml` to hear every voice (mp3s land in `media/voice-samples/`). No real person's voice is cloned.
It runs on GitHub because the model comes from Hugging Face. Indonesian uses the Malay voice (closest language).
Voiced files go to the `media` branch and the topic gets `"video": "<id>.mp4"`, so scheduling uploads the voiced version.
Chatterbox adds Resemble's inaudible PerTh watermark (marks the audio as AI-generated). The voice belongs to a cartoon
character, not a real person, so YouTube's "altered or synthetic content" label (meant for realistic people and events) stays "No".
