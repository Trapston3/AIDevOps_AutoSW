"""Capture live evidence screenshots: Swagger UI + final test run via Playwright."""
import subprocess
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "screenshots"


def shoot(url: str, png: str, width: int = 1280, height: int = 900, full: bool = True) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / png), full_page=full)
        browser.close()
    print(f"[ok] {png}")


def run(cmd: list[str], png: str, title: str) -> None:
    import sys
    sys.path.insert(0, str(ROOT))
    from make_screenshots import render
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, shell=True)
    txt = ROOT / "docs" / "responses" / f"{png.replace('.png', '.txt')}"
    txt.write_text(f"$ {cmd[0] if isinstance(cmd[0], str) else cmd}\n\n{proc.stdout}{proc.stderr}", encoding="utf-8")
    render(txt, OUT / png, title)


if __name__ == "__main__":
    shoot("http://127.0.0.1:8010/docs", "08_live_swagger_ui.png")
    run(
        [r'curl -s http://127.0.0.1:8010/health && echo "" && curl -s -X POST http://127.0.0.1:8010/groups -H "Content-Type: application/json" -d "{\"name\":\"Goa Trip\",\"members\":[\"Asha\",\"Ben\"]}" && echo "" && curl -s -X POST http://127.0.0.1:8010/groups/1/expenses -H "Content-Type: application/json" -d "{\"description\":\"Dinner\",\"amount\":42.5,\"paid_by\":\"Asha\"}" && echo "" && curl -s -X POST http://127.0.0.1:8010/groups/1/expenses -H "Content-Type: application/json" -d "{\"description\":\"Bad\",\"amount\":-5,\"paid_by\":\"Ben\"}" && echo "" && curl -s http://127.0.0.1:8010/groups/99'],
        "09_live_api_session.png",
        "TabSplit live API session - curl against uvicorn (localhost:8010)",
    )
