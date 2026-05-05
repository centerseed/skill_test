#!/usr/bin/env python3
"""
抓取產品頁，輸出：文字（txt）+ 圖片 URL 清單（json）
Usage: python parse_page.py <url> <output_prefix>
輸出：{prefix}_text.txt, {prefix}_images.json
"""
import sys, json, re, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url    = sys.argv[1]
prefix = sys.argv[2]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.5",
}

r = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
r.raise_for_status()
print(f"Fetched: {r.status_code} — {len(r.text):,} chars")

soup = BeautifulSoup(r.text, "html.parser")
for tag in soup(["script", "style", "nav", "footer", "noscript"]):
    tag.decompose()

text = soup.get_text(separator="\n", strip=True)
text = re.sub(r"\n{3,}", "\n\n", text)

with open(f"{prefix}_text.txt", "w", encoding="utf-8") as f:
    f.write(text)
print(f"Text: {len(text):,} chars → {prefix}_text.txt")

# 提取圖片 URL
imgs, seen = [], set()
for tag in soup.find_all(["img", "source"]):
    for attr in ["src", "data-src", "srcset"]:
        raw = tag.get(attr, "")
        for part in raw.split(","):
            src = part.strip().split(" ")[0]
            if not src or src in seen or src.startswith("data:"):
                continue
            seen.add(src)
            full = urljoin(r.url, src)
            if any(ext in full.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                imgs.append(full)

# 去掉 ?width= 重複
deduped, seen_base = [], set()
for img in imgs:
    base = img.split("?")[0]
    if base not in seen_base:
        seen_base.add(base)
        deduped.append(img)

with open(f"{prefix}_images.json", "w", encoding="utf-8") as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)
print(f"Images: {len(deduped)} URLs → {prefix}_images.json")
