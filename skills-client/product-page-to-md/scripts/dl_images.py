#!/usr/bin/env python3
"""
從 images.json 下載產品相關圖片（過濾 icon/svg/navigation）
Usage: python dl_images.py <images_json> <output_dir> [max=15]
"""
import sys, json, os, requests

images_json = sys.argv[1]
output_dir  = sys.argv[2]
max_imgs    = int(sys.argv[3]) if len(sys.argv) > 3 else 15

os.makedirs(output_dir, exist_ok=True)
imgs = json.load(open(images_json))

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# 過濾掉明顯是 UI 元素的圖
skip_kw = ["icon", "logo", "banner", "arrow", "star", "close", "menu",
           "badge", "check", "button", "spinner", "loading", "avatar",
           "flag", "thumbnail", "sprite", "pixel", "track"]

def is_product_img(url):
    low = url.lower()
    if any(kw in low for kw in skip_kw):
        return False
    if ".svg" in low:
        return False
    return True

filtered = [u for u in imgs if is_product_img(u)][:max_imgs]
print(f"過濾後: {len(filtered)} 張（原 {len(imgs)} 張）")

count = 0
for i, url in enumerate(filtered):
    ext = url.split("?")[0].rsplit(".", 1)[-1][:4].lower()
    if ext not in ["jpg", "jpeg", "png", "webp"]:
        ext = "jpg"
    path = os.path.join(output_dir, f"img_{i+1:02d}.{ext}")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200 and len(r.content) > 5000:  # 跳過 < 5KB 的小圖
            with open(path, "wb") as f:
                f.write(r.content)
            print(f"OK  img_{i+1:02d}.{ext}  {len(r.content)//1024} KB  {url[:70]}")
            count += 1
        else:
            print(f"SKIP  {r.status_code} or too small  {url[:70]}")
    except Exception as e:
        print(f"ERR  {e}  {url[:70]}")

print(f"\n下載完成: {count} 張 → {output_dir}")
