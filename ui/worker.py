import sys
import os
import time
import re
from PyQt6.QtCore import QThread, pyqtSignal


def _get_base_dir():
    """Return the directory that contains the exe (frozen) or the script."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _patch_path():
    """Inject ffmpeg dir into PATH. Works for both the portable bundle and dev mode."""
    base = _get_base_dir()
    ffmpeg_dir = os.path.join(base, "ffmpeg")
    if os.path.isdir(ffmpeg_dir):
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        return

    # dev fallback on macOS: Homebrew locations
    if sys.platform == "darwin":
        extra = ["/opt/homebrew/bin", "/usr/local/bin"]
        os.environ["PATH"] = os.pathsep.join(extra) + os.pathsep + os.environ.get("PATH", "")


class DownloadWorker(QThread):
    progress   = pyqtSignal(float, str, str)  # percent, speed, eta
    info_ready = pyqtSignal(str, str, str)    # title, uploader, thumbnail_url
    finished   = pyqtSignal(bool, str)
    log_line   = pyqtSignal(str, str)

    FORMAT_MAP = {
        "best":  "bestvideo+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "720p":  "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "480p":  "bestvideo[height<=480]+bestaudio/best[height<=480]",
        "360p":  "bestvideo[height<=360]+bestaudio/best[height<=360]",
        "audio": "bestaudio/best",
        "mp3":   "bestaudio/best",
        "aac":   "bestaudio/best",
        "flac":  "bestaudio/best",
        "remux": "bestvideo+bestaudio/best",
    }

    def __init__(self, url, fmt, output_dir, parent=None):
        super().__init__(parent)
        self.url = url
        self.fmt = fmt
        self.output_dir = output_dir
        self._paused = False
        self._cancelled = False

    def run(self):
        try:
            import yt_dlp
            _patch_path()

            fmt_string = self.FORMAT_MAP.get(self.fmt, "bestvideo+bestaudio/best")

            opts = {
                "format": fmt_string,
                "outtmpl": f"{self.output_dir}/%(title)s.%(ext)s",
                "progress_hooks": [self._progress_hook],
                "quiet": True,
                "no_warnings": False,
                "logger": self._Logger(self),
            }

            if self.fmt == "mp3":
                opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }]
            elif self.fmt == "aac":
                opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "aac"}]
            elif self.fmt == "flac":
                opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "flac"}]

            with yt_dlp.YoutubeDL(opts) as ydl:
                self.log_line.emit("info", f"Fetching metadata: {self.url}")
                info = ydl.extract_info(self.url, download=False)
                if info:
                    title = info.get("title", "Unknown title")
                    uploader = info.get("uploader", "")
                    thumb = info.get("thumbnail", "")
                    self.info_ready.emit(title, uploader, thumb)
                    self.log_line.emit("info", f"Starting: {title}")

                if self._cancelled:
                    self.finished.emit(False, "Cancelled")
                    return

                ydl.download([self.url])

            if not self._cancelled:
                self.finished.emit(True, "Download complete")

        except Exception as e:
            self.log_line.emit("error", str(e))
            self.finished.emit(False, str(e))

    def _progress_hook(self, d):
        if self._cancelled:
            raise Exception("Cancelled")

        while self._paused:
            time.sleep(0.2)
            if self._cancelled:
                raise Exception("Cancelled")

        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            pct = (downloaded / total * 100) if total else 0
            speed = d.get("speed", 0) or 0
            eta = d.get("eta", 0) or 0
            self.progress.emit(pct, self._fmt_speed(speed), self._fmt_eta(eta))
        elif status == "finished":
            self.progress.emit(100, "", "")
            self.log_line.emit("success", "Post-processing…")

    @staticmethod
    def _fmt_speed(bps):
        if bps < 1024:
            return f"{bps:.0f} B/s"
        elif bps < 1024 ** 2:
            return f"{bps / 1024:.1f} KB/s"
        return f"{bps / 1024 ** 2:.1f} MB/s"

    @staticmethod
    def _fmt_eta(seconds):
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60:02d}s"
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"

    def pause(self):  self._paused = True
    def resume(self): self._paused = False
    def cancel(self): self._cancelled = True; self._paused = False

    class _Logger:
        def __init__(self, worker):
            self.w = worker
        def debug(self, msg):
            if msg.startswith("[debug]"):
                return
            self.w.log_line.emit("info", msg)
        def info(self, msg):    self.w.log_line.emit("info", msg)
        def warning(self, msg): self.w.log_line.emit("warning", msg)
        def error(self, msg):   self.w.log_line.emit("error", msg)
