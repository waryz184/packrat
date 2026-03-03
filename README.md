# Packrat 🐀

A dead-simple GUI to download videos and audio from basically any site — YouTube, Twitter/X, TikTok, SoundCloud, Vimeo, and a thousand others. It's a thin wrapper around [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) with a clean terminal-style interface. No Electron, no browser embedded in the app, just native PyQt6.

Paste a URL. Pick a format. Done.

---

## Installing (macOS .dmg)

Grab the latest `Packrat-1.0.0.dmg` from the [Releases](#) page, open it, drag the app to Applications, done.

**First launch might get blocked by macOS** — it'll say something about "unidentified developer". Just right-click the app in your Applications folder and choose **Open**, then confirm. You only need to do this once.

---

## Running from source

If you'd rather run it directly (or you're on Linux or Windows), it's pretty straightforward.

**You'll need:**
- Python 3.9 or newer
- FFmpeg — required for merging streams and converting formats

```bash
# Install FFmpeg if you haven't already
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Ubuntu/Debian
```

**Then:**
```bash
git clone https://github.com/YOUR_USERNAME/Packrat.git
cd Packrat
pip install -r requirements.txt
python3 main.py
```

That's it. `./run.sh` does the same thing if you prefer.

---

## How it works

The interface is intentionally minimal. There's an input bar at the top — paste your URL there, choose a format from the dropdown, and hit Enter or click Download. Downloads show up in the queue with a progress bar. Switch to the logs tab if something goes wrong and you want to see what yt-dlp is actually doing.

Files land in `~/Downloads/Packrat` by default. You can change that in Settings.

**Formats:**
- `best` — highest quality, whatever that is for the site
- `1080p`, `720p`, `480p`, `360p` — specific resolution
- `audio` — audio only, original format
- `mp3`, `aac`, `flac` — converted audio

---

## Building the .app yourself

You need `py2app` for this:

```bash
pip install py2app
python3 setup.py py2app
```

Then to package it into a `.dmg` for sharing:

```bash
./make_dmg.sh
```

---

## If something breaks

**Download fails right away** → check that FFmpeg is installed (`ffmpeg -version` in your terminal). Also peek at the logs tab for the actual error.

**YouTube downloads failing or slow** → YouTube changes things constantly. Update yt-dlp: `pip install -U yt-dlp`

**"No module named PyQt6"** → you skipped the install step. Run `pip install -r requirements.txt`.

**App won't open on macOS** → see the Gatekeeper note above (right-click → Open).

---

## Contributing

PRs are welcome. Fork, branch, commit, push, open a PR — the usual.

---

*Not affiliated with YouTube, yt-dlp, or any supported platform. MIT license.*
