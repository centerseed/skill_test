#!/usr/bin/env python3
"""
抓取 YouTube 字幕並存成 JSON。
優先順序：手動英文字幕 > 自動英文字幕 > Whisper 語音辨識
Usage: python fetch_transcript.py <video_id> <output_path>
輸出 JSON 陣列：[{start, duration, text}, ...]
"""
import sys, json, os, subprocess, tempfile

video_id    = sys.argv[1]
output_path = sys.argv[2]
video_url   = f"https://www.youtube.com/watch?v={video_id}"


def try_subtitle():
    from youtube_transcript_api import YouTubeTranscriptApi
    try:
        api = YouTubeTranscriptApi()
        tlist = api.list(video_id)
        transcript = None
        for t in tlist:
            if not t.is_generated and t.language_code.startswith("en"):
                transcript = t.fetch()
                break
        if transcript is None:
            for t in tlist:
                if t.language_code.startswith("en"):
                    transcript = t.fetch()
                    break
        if transcript is None:
            return None
        return [{"start": s.start, "duration": s.duration, "text": s.text} for s in transcript]
    except Exception as e:
        print(f"字幕抓取失敗：{e}", file=sys.stderr)
        return None


def try_whisper():
    # 下載音訊到暫存目錄
    tmp_dir = tempfile.gettempdir()
    audio_template = os.path.join(tmp_dir, f"{video_id}.%(ext)s")
    audio_path = os.path.join(tmp_dir, f"{video_id}.wav")

    print("無英文字幕，改用 Whisper 語音辨識...", file=sys.stderr)
    print("下載音訊中（需要 ffmpeg，首次辨識需下載模型約 145MB）...", file=sys.stderr)

    result = subprocess.run(
        [sys.executable, "-m", "yt_dlp", "-x", "--audio-format", "wav", "--audio-quality", "0",
         "-o", audio_template, "--no-playlist", video_url],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        print(f"yt-dlp 下載失敗：{result.stderr}", file=sys.stderr)
        sys.exit(3)

    # yt-dlp 有時會輸出 .wav 以外的副檔名
    if not os.path.exists(audio_path):
        candidates = [f for f in os.listdir(tmp_dir)
                      if f.startswith(video_id) and not f.endswith(".json")]
        if not candidates:
            print("找不到下載的音訊檔案", file=sys.stderr)
            sys.exit(4)
        audio_path = os.path.join(tmp_dir, candidates[0])

    print(f"音訊下載完成：{audio_path}", file=sys.stderr)
    print("Whisper 辨識中（CPU 模式，長影片需數分鐘）...", file=sys.stderr)

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("請先安裝 faster-whisper：python -m pip install faster-whisper", file=sys.stderr)
        sys.exit(5)

    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments_gen, _ = model.transcribe(audio_path, language="en")
    segments = [
        {"start": round(seg.start, 2),
         "duration": round(seg.end - seg.start, 2),
         "text": seg.text.strip()}
        for seg in segments_gen
    ]

    # 清理暫存音訊
    try:
        os.remove(audio_path)
    except Exception:
        pass

    return segments


# --- 主流程 ---
segments = try_subtitle()
source = "subtitle"

if segments is None:
    segments = try_whisper()
    source = "whisper"

os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(segments, f, ensure_ascii=False, indent=2)

total = sum(s["duration"] for s in segments)
print(f"OK [{source}]: {len(segments)} segments, {int(total//60)}:{int(total%60):02d} → {output_path}")
