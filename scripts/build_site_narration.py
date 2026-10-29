"""Build the voice-over for the intro site (site/).

Reads every narration line (`.caps > .cap`) from site/index.html, voices
each one with the Kokoro text-to-speech model, and writes:

  site/assets/narration.mp3  one track for the whole film
  site/assets/narration.js   per-chapter timing the player retimes to

The HTML stays the source of truth and is authored in "script time". A
spoken line usually runs longer than the slot its subtitle had, so each
chapter is stretched, never squeezed: line i starts no earlier than its
scripted time and no earlier than the end of line i-1 plus a pause. The
player maps every scripted time through the resulting anchors
(piecewise-linear), so the visuals keep landing on the words.

Rerun this after changing any narration line. It needs ffmpeg and a Python
environment with kokoro-onnx, numpy and soundfile, plus the model files
from https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0):

  python build_site_narration.py --model kokoro-v1.0.onnx --voices voices-v1.0.bin
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

SITE = Path(__file__).resolve().parent.parent / "site"
SAMPLE_RATE = 24000
GAP = 0.4    # silence between consecutive lines, seconds
TAIL = 1.2   # minimum hold after a chapter's last line

# Spoken forms for words the model reads wrongly. Subtitles keep the
# written form.
PRONOUNCE = {
    r"\bOriveda\b": "Ori-vay-da",
    r"\boriveda\b": "Ori-vay-da",
    r"\bADRs\b": "A D Rs",
    r"\bADR\b": "A D R",
}


def spoken(text: str) -> str:
    for pattern, replacement in PRONOUNCE.items():
        text = re.sub(pattern, replacement, text)
    return text


def attrs(tag: str) -> dict[str, str]:
    return {k: html.unescape(v) for k, v in re.findall(r'([\w-]+)="([^"]*)"', tag)}


def read_chapters(index: Path) -> list[dict]:
    source = index.read_text(encoding="utf-8")
    chapters = []
    for match in re.finditer(r'(<section class="scene"[^>]*>)(.*?)</section>', source, re.S):
        head = attrs(match.group(1))
        lines = []
        for cap in re.finditer(r'(<p class="cap"[^>]*>)(.*?)</p>', match.group(2), re.S):
            a = attrs(cap.group(1))
            text = " ".join(html.unescape(re.sub(r"<[^>]+>", "", cap.group(2))).split())
            lines.append({"at": float(a["data-at"]), "text": text, "say": a.get("data-say") or spoken(text)})
        chapters.append({"id": head["id"], "dur": float(head["data-duration"]), "lines": lines})
    return chapters


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model", required=True, help="kokoro-v1.0.onnx")
    parser.add_argument("--voices", required=True, help="voices-v1.0.bin")
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args()

    kokoro = Kokoro(args.model, args.voices)
    chapters = read_chapters(SITE / "index.html")
    timing: dict[str, dict] = {}
    track: list[np.ndarray] = []

    for ch in chapters:
        clips, starts = [], []
        for i, line in enumerate(ch["lines"]):
            audio, sr = kokoro.create(line["say"], voice=args.voice, speed=args.speed, lang="en-us")
            assert sr == SAMPLE_RATE, sr
            clips.append(audio.astype(np.float32))
            length = len(audio) / sr
            if i == 0:
                start = line["at"]
            else:
                prev = ch["lines"][i - 1]
                start = max(starts[-1] + (line["at"] - prev["at"]), starts[-1] + prev["len"] + GAP)
            line["len"] = round(length, 3)
            starts.append(round(start, 3))
            print(f'{ch["id"]:>11} {start:6.2f}s  {length:5.2f}s  {line["say"]}')

        last = ch["lines"][-1]
        new_dur = round(max(starts[-1] + (ch["dur"] - last["at"]), starts[-1] + last["len"] + TAIL), 3)
        anchors = [[0, 0]] + [[line["at"], s] for line, s in zip(ch["lines"], starts)] + [[ch["dur"], new_dur]]
        timing[ch["id"]] = {"dur": new_dur, "anchors": anchors, "lines": [line["len"] for line in ch["lines"]]}

        buf = np.zeros(int(round(new_dur * SAMPLE_RATE)), dtype=np.float32)
        for clip, s in zip(clips, starts):
            at = int(round(s * SAMPLE_RATE))
            buf[at:at + len(clip)] += clip[: max(0, len(buf) - at)]
        track.append(buf)

    film = np.concatenate(track)
    peak = float(np.max(np.abs(film))) or 1.0
    film *= 0.89 / peak  # about -1 dBFS

    out_mp3 = SITE / "assets" / "narration.mp3"
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "narration.wav"
        sf.write(wav, film, SAMPLE_RATE)
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-b:a", "64k", str(out_mp3)],
            check=True,
        )

    total = sum(t["dur"] for t in timing.values())
    payload = {"src": "assets/narration.mp3", "voice": f"Kokoro-82M {args.voice}", "total": round(total, 3), "chapters": timing}
    (SITE / "assets" / "narration.js").write_text(
        "// Generated by scripts/build_site_narration.py. Do not edit by hand.\n"
        f"window.ORIVEDA_NARRATION = {json.dumps(payload, indent=1)};\n",
        encoding="utf-8",
    )
    print(f"\n{len(timing)} chapters, {total:.1f}s, {out_mp3.stat().st_size / 1e6:.2f} MB -> {out_mp3}")


if __name__ == "__main__":
    main()
