"""
Windows environment verification script.
Run after SETUP_PROMPT.md installation to confirm everything works.
"""
import os
import sys
import json
import subprocess
import importlib.util
import tempfile
import urllib.request
import shutil

PASS = "OK  "
FAIL = "FAIL"
results = {}


def check(name, ok):
    results[name] = ok
    status = PASS if ok else FAIL
    print(f"  {status} {name}")
    return ok


def module_ok(mod):
    return importlib.util.find_spec(mod) is not None


def cmd_ok(args):
    try:
        r = subprocess.run(args, capture_output=True, timeout=30)
        if r.returncode != 0:
            print(f"    cmd {args[0]} returned {r.returncode}: {r.stderr.decode(errors='replace')[:200]}")
        return r.returncode == 0
    except FileNotFoundError:
        print(f"    cmd {args[0]} not found in PATH")
        print(f"    shutil.which: {shutil.which(args[0])}")
        return False
    except Exception as e:
        print(f"    cmd {args[0]} exception: {e}")
        return False


print("\n=== Step 1: Python ===")
check("python 3.x", sys.version_info >= (3, 8))

print("\n=== Step 2: pip packages ===")
check("requests", module_ok("requests"))
check("beautifulsoup4", module_ok("bs4"))
check("youtube-transcript-api", module_ok("youtube_transcript_api"))
check("yt-dlp", cmd_ok([sys.executable, "-m", "yt_dlp", "--version"]))
check("faster-whisper", module_ok("faster_whisper"))

print("\n=== Step 3: ffmpeg ===")
ffmpeg_path = shutil.which("ffmpeg")
print(f"    shutil.which('ffmpeg'): {ffmpeg_path}")
check("ffmpeg", cmd_ok(["ffmpeg", "-version"]))

print("\n=== Step 4: parse_page.py ===")
script_dir = os.path.dirname(os.path.abspath(__file__))
parse_script = os.path.join(script_dir, "product-page-to-md", "scripts", "parse_page.py")
tmp_prefix = os.path.join(tempfile.gettempdir(), "h123_test")
try:
    r = subprocess.run(
        [sys.executable, parse_script,
         "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
         tmp_prefix],
        capture_output=True, text=True, timeout=30
    )
    text_ok = os.path.exists(tmp_prefix + "_text.txt")
    imgs_ok = os.path.exists(tmp_prefix + "_images.json")
    if r.returncode != 0 or r.stderr:
        print(f"    stdout: {r.stdout[-300:]}")
        print(f"    stderr: {r.stderr[-300:]}")
    if text_ok:
        size = len(open(tmp_prefix + "_text.txt", encoding="utf-8").read())
        check(f"parse_page.py (text {size:,} chars)", size > 100)
    else:
        check("parse_page.py", False)
    check("parse_page.py images.json", imgs_ok)
except Exception as e:
    check("parse_page.py", False)
    print(f"    Error: {e}")

print("\n=== Step 5: fetch_transcript.py ===")
transcript_script = os.path.join(script_dir, "youtube-video-to-md", "scripts", "fetch_transcript.py")
tmp_transcript = os.path.join(tempfile.gettempdir(), "h123_transcript", "output.json")
try:
    # dQw4w9WgXcQ = Rick Astley, globally available, has auto-generated EN captions
    r = subprocess.run(
        [sys.executable, transcript_script, "dQw4w9WgXcQ", tmp_transcript],
        capture_output=True, text=True, timeout=60
    )
    if os.path.exists(tmp_transcript):
        data = json.load(open(tmp_transcript, encoding="utf-8"))
        check(f"fetch_transcript.py ({len(data)} segments)", len(data) > 0)
    else:
        print(f"    stdout: {r.stdout[-400:]}")
        print(f"    stderr: {r.stderr[-400:]}")
        check("fetch_transcript.py", False)
except Exception as e:
    check("fetch_transcript.py", False)
    print(f"    Error: {e}")

print("\n=== Step 6: skills installed ===")
claude_skills = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), ".claude", "skills")
check("product-page skill", os.path.exists(os.path.join(claude_skills, "product-page-to-md", "SKILL.md")))
check("youtube skill", os.path.exists(os.path.join(claude_skills, "youtube-video-to-md", "SKILL.md")))

print("\n=== Step 7: output folder ===")
check("C:\\health-research\\ingredients", os.path.exists(r"C:\health-research\ingredients"))

# Final verdict
failed = [k for k, v in results.items() if not v]
print(f"\n{'='*40}")
if failed:
    print(f"FAILED ({len(failed)} items): {failed}")
    sys.exit(1)
else:
    print(f"All {len(results)} checks passed!")
