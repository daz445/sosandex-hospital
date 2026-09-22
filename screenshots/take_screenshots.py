import asyncio
from playwright.async_api import async_playwright

PAGES = [
    ("dashboard", "/"),
    ("schedule", "/schedule"),
    ("doctors", "/doctors"),
    ("patients", "/patients"),
    ("appointments", "/appointments"),
    ("admin", "/admin"),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        for name, path in PAGES:
            await page.goto(f"http://localhost:8000{path}")
            await page.wait_for_load_state("networkidle")
            await page.screenshot(path=f"screenshots/{name}.png", full_page=True)
            print(f"  ✓ {name}.png")
        await browser.close()

asyncio.run(main())
