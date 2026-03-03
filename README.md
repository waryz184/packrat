# Packrat 🐀

A dead-simple GUI to download videos and audio from basically any site — YouTube, Twitter/X, TikTok, SoundCloud, Vimeo, and a thousand others. It's a thin wrapper around [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) with a clean terminal-style interface. No Electron, no browser embedded in the app, just native PyQt6 speed with a hacker aesthetic.

Paste a URL. Pick a format. Done.

---

## Download

| Platform | File | Notes |
|---|---|---|
| macOS | `Packrat-v1.0.0-macos.dmg` | macOS 12+ |
| Windows | `Packrat-v1.0.0-win64.zip` | Windows 10/11, portable |

→ [Latest Release](https://github.com/waryz184/packrat/releases/latest)

---

## Installing on macOS

1. Download `Packrat-v1.0.0-macos.dmg` and open it.
2. Drag **Packrat.app** into your **Applications** folder.
3. Launch Packrat from Applications or Spotlight.

**Gatekeeper warning on first launch?** macOS may block the app because it's not signed with an Apple certificate. Fix: right-click on Packrat in Applications → **Open** → confirm. Only needed once.

---

## Installing on Windows (portable)

1. Download `Packrat-v1.0.0-win64.zip` and extract it anywhere — your Desktop, a USB drive, wherever.
2. Open the extracted folder and double-click **Packrat.exe**.

That's it. Nothing gets installed, nothing goes in the registry. Your settings are saved in a `packrat.ini` file right next to the exe — move the folder and everything comes with it.

**Windows Defender warning?** Windows may show a SmartScreen popup ("Windows protected your PC") because the exe isn't signed. Click **More info** → **Run anyway**.

---

## Running from source

If you'd rather run it directly (or you're on Linux), it's straightforward.

**You'll need:**
- Python 3.9+
- FFmpeg — required for merging streams and converting formats

```bash
# Install FFmpeg if you haven't already
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Ubuntu/Debian
```

**Then:**
```bash
git clone https://github.com/waryz184/packrat.git
cd packrat
pip install -r requirements.txt
python3 main.py
```

`./run.sh` does the same thing if you prefer.

---

## How it works

Paste a URL in the input bar at the top, choose a format from the dropdown, and hit Enter or click Download. Downloads show up in the queue with a progress bar. Switch to the logs tab if something goes wrong and you want to see what yt-dlp is actually doing.

Files land in `~/Downloads/Packrat` by default (macOS/Linux) or `Documents\Packrat` on Windows. You can change that in Settings.

**Formats:**
- `best` — highest quality available
- `1080p`, `720p`, `480p`, `360p` — specific resolution
- `audio` — audio only, original format
- `mp3`, `aac`, `flac` — converted audio

---

## If something breaks

**Download fails right away** → check that FFmpeg is accessible (`ffmpeg -version` in your terminal). Also peek at the logs tab for the actual error.

**YouTube downloads failing or slow** → YouTube changes things constantly. Update yt-dlp: `pip install -U yt-dlp`

**"No module named PyQt6"** → run `pip install -r requirements.txt`.

**App won't open on macOS** → right-click → Open (see Gatekeeper note above).

**Windows Defender blocks the exe** → click More info → Run anyway.

---

## Contributing

PRs are welcome. Fork, branch, commit, push, open a PR — the usual.

---

*Not affiliated with YouTube, yt-dlp, or any supported platform. MIT license.*
