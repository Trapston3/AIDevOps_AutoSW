"""Render docs/responses/*.txt into dark terminal-style PNG screenshots."""
import html
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><style>
  body {{ margin:0; background:#0d1117; font-family:'Cascadia Code','Consolas',monospace; }}
  .win {{ width:980px; }}
  .bar {{ display:flex; align-items:center; gap:8px; background:#161b22; padding:10px 14px;
         border-bottom:1px solid #30363d; border-radius:10px 10px 0 0; }}
  .dot {{ width:12px; height:12px; border-radius:50%; }}
  .title {{ color:#8b949e; font-size:13px; margin-left:8px; }}
  .body {{ padding:18px 20px; color:#c9d1d9; font-size:13.5px; line-height:1.55;
           white-space:pre-wrap; word-wrap:break-word; border-radius:0 0 10px 10px; }}
  .p {{ color:#7ee787; font-weight:bold; }}
  .h {{ color:#79c0ff; }}
</style></head><body><div class="win">
  <div class="bar">
    <span class="dot" style="background:#ff5f56"></span>
    <span class="dot" style="background:#ffbd2e"></span>
    <span class="dot" style="background:#27c93f"></span>
    <span class="title">{title}</span>
  </div>
  <div class="body">{content}</div>
</div></body></html>"""


def render(txt_path: Path, png_path: Path, title: str) -> None:
    raw = txt_path.read_text(encoding="utf-8", errors="replace")
    # Highlight the user prompt line(s) and hermes banner lines
    esc = html.escape(raw)
    esc = re.sub(r"^(&gt;\s.*)$", r'<span class="p">\1</span>', esc, flags=re.M)
    content = esc

    page_html = TEMPLATE.format(title=html.escape(title), content=content)
    tmp = OUT / "_tmp_render.html"
    tmp.write_text(page_html, encoding="utf-8")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1024, "height": 800})
        page.goto(tmp.as_uri())
        page.wait_for_timeout(250)
        page.locator(".win").screenshot(path=str(png_path))
        browser.close()

    print(f"[ok] {png_path.name} ({png_path.stat().st_size} bytes)")


def main() -> None:
    shots = [
        ("step01_hermes_response.txt", "01_zero_shot_scaffold_response.png",
         "Hermes Agent CLI - Step 1 (Zero-shot): TabSplit FastAPI scaffold"),
        ("step02_hermes_response.txt", "02_zero_shot_tests_response.png",
         "Hermes Agent CLI - Step 2 (Zero-shot): pytest suite generation"),
        ("step04_hermes_response.txt", "04_fewshot_docstrings_response.png",
         "Hermes Agent CLI - Step 4 (Few-shot): Google-style docstrings"),
        ("step03b_verification.txt", "03b_fewshot_error_envelope_verification.png",
         "Step 3 follow-up - replaying the 4 few-shot examples against the API"),
        ("step05_hermes_response.txt", "05_cot_netting_response.png",
         "Hermes Agent CLI - Step 5 (Chain-of-thought): balance netting"),
        ("step06_hermes_response.txt", "06_cot_debug_response.png",
         "Hermes Agent CLI - Step 6 (Chain-of-thought): rounding bug root cause"),
        ("step06b_red_test.txt", "06b_red_test_failure.png",
         "Step 6 RED state - failing rounding test before the fix (reproduced)"),
        ("step07_hermes_response.txt", "07_cot_netting_tests_response.png",
         "Hermes Agent CLI - Step 7 (Zero-shot): netting test suite"),
    ]
    for txt, png, title in shots:
        src = ROOT / "docs" / "responses" / txt
        if src.exists() and src.stat().st_size > 200:
            render(src, OUT / png, title)
        else:
            print(f"[skip] {txt} (missing or too small)")


if __name__ == "__main__":
    main()
