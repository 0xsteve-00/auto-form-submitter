#!/usr/bin/env python3
"""
Auto Form Submitter — Automate web form submissions for testnets & waitlists.
Usage:
  python submit.py --config config.yaml
  python submit.py --config config.yaml --wallets wallets.csv --batch 10
"""

import asyncio
import argparse
import csv
import json
import random
import time
import sys
from pathlib import Path

import yaml
from playwright.async_api import async_playwright


def load_config(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def load_wallets(path: str) -> list[dict]:
    """Load wallets from CSV or JSON."""
    p = Path(path)
    if p.suffix == ".json":
        with open(p) as f:
            return json.load(f)
    elif p.suffix == ".csv":
        with open(p, newline="") as f:
            return list(csv.DictReader(f))
    else:
        raise ValueError(f"Unsupported file format: {p.suffix}")


def random_delay(min_ms=50, max_ms=150):
    return random.randint(min_ms, max_ms)


async def human_type(page, selector: str, text: str):
    """Type text with human-like delays."""
    el = await page.query_selector(selector)
    if not el:
        print(f"  ⚠️ Selector not found: {selector}")
        return False
    await el.click()
    await page.wait_for_timeout(random.randint(200, 500))
    await page.fill(selector, "")
    for char in text:
        await page.type(selector, char, delay=random_delay(40, 120))
    return True


async def handle_challenge(page, timeout=45):
    """Handle Akamai/Cloudflare challenges by waiting."""
    html = await page.content()
    if "Challenge Validation" in html or "challenge" in html.lower()[:500]:
        print(f"  🛡️ Challenge detected — waiting {timeout}s...")
        await page.wait_for_timeout(timeout * 1000)
        return True
    return False


async def submit_form(config: dict, wallet: dict = None, proxy: str = None):
    """Submit a single form."""
    url = config["url"]
    fields = config.get("fields", [])
    checkboxes = config.get("checkboxes", [])
    submit_sel = config.get("submit", "button[type='submit']")
    wait_for = config.get("wait_for", 10)
    success_check = config.get("success_check", "")
    stealth = config.get("stealth", True)
    warmup_url = config.get("warmup", "")

    async with async_playwright() as p:
        launch_args = ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
        if stealth:
            launch_args.append("--disable-blink-features=AutomationControlled")

        browser = await p.chromium.launch(headless=True, args=launch_args)
        ctx_kwargs = {
            "viewport": {"width": 1440, "height": 900},
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/148.0.0.0 Safari/537.36",
        }
        if proxy:
            ctx_kwargs["proxy"] = {"server": proxy}

        context = await browser.new_context(**ctx_kwargs)
        page = await context.new_page()

        if stealth:
            await page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => false});"
            )

        try:
            # Warmup visit (get cookies)
            if warmup_url:
                print(f"  🌐 Warmup: {warmup_url}")
                await page.goto(warmup_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(random.randint(3000, 6000))
                await page.evaluate(
                    '() => { const b = document.getElementById("onetrust-accept-btn-handler"); if(b) b.click(); }'
                )

            # Load form
            print(f"  📝 Loading: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(random.randint(3000, 6000))

            # Handle challenge
            await handle_challenge(page)

            # Fill fields
            for field in fields:
                sel = field["selector"]
                val = field.get("value", "")
                ftype = field.get("type", "text")

                # Replace placeholders
                if wallet:
                    for k, v in wallet.items():
                        val = val.replace(f"{{{k}}}", str(v))

                if ftype == "select":
                    try:
                        await page.select_option(sel, label=val)
                        print(f"  ✅ Select: {sel} → {val}")
                    except Exception as e:
                        print(f"  ⚠️ Select failed: {sel} — {e}")
                else:
                    ok = await human_type(page, sel, val)
                    if ok:
                        print(f"  ✅ Fill: {sel} → {val[:30]}...")

            # Checkboxes
            for cb_sel in checkboxes:
                try:
                    await page.evaluate(
                        f'() => document.querySelectorAll("{cb_sel}").forEach(cb => '
                        '{ if(!cb.checked) cb.click(); })'
                    )
                    print(f"  ☑️ Checkbox: {cb_sel}")
                except Exception as e:
                    print(f"  ⚠️ Checkbox failed: {cb_sel} — {e}")

            await page.wait_for_timeout(random.randint(500, 1500))

            # Submit
            print(f"  🚀 Submitting...")
            try:
                await page.click(submit_sel, timeout=5000)
            except Exception:
                await page.evaluate(
                    f'() => document.querySelector("{submit_sel}")?.click()'
                )

            # Wait and check
            await page.wait_for_timeout(wait_for * 1000)

            # Handle post-submit challenge
            await handle_challenge(page)

            # Check success
            body = await page.inner_text("body")
            url_after = page.url

            if success_check and success_check.lower() in body.lower():
                print(f"  ✅ SUCCESS! (keyword: {success_check})")
                return True
            elif "activate" in url_after.lower():
                print(f"  ✅ SUCCESS! (redirected to activate)")
                return True
            else:
                print(f"  ❌ No success signal. URL: {url_after[:60]}")
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
        finally:
            await browser.close()


async def batch_submit(config_path: str, wallets_path: str, batch_size: int = 5):
    """Submit forms in batches."""
    config = load_config(config_path)
    wallets = load_wallets(wallets_path)
    proxy = config.get("proxy", "")

    print(f"📋 Config: {config_path}")
    print(f"👥 Wallets: {len(wallets)}")
    print(f"📦 Batch size: {batch_size}")
    print("=" * 50)

    results = {"success": 0, "failed": 0, "errors": 0}

    for i in range(0, len(wallets), batch_size):
        batch = wallets[i : i + batch_size]
        print(f"\n🔄 Batch {i // batch_size + 1} ({len(batch)} wallets)")

        for j, wallet in enumerate(batch):
            name = wallet.get("name", wallet.get("email", f"wallet_{i+j}"))
            print(f"\n  [{j+1}/{len(batch)}] {name}")

            try:
                ok = await submit_form(config, wallet, proxy)
                if ok:
                    results["success"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                print(f"  ❌ Exception: {e}")
                results["errors"] += 1

            # Delay between submissions
            if j < len(batch) - 1:
                delay = random.randint(5, 15)
                print(f"  ⏳ Waiting {delay}s...")
                await asyncio.sleep(delay)

        # Longer delay between batches
        if i + batch_size < len(wallets):
            delay = random.randint(30, 60)
            print(f"\n  ⏳ Batch cooldown {delay}s...")
            await asyncio.sleep(delay)

    print(f"\n{'=' * 50}")
    print(f"📊 Results:")
    print(f"  ✅ Success: {results['success']}")
    print(f"  ❌ Failed:  {results['failed']}")
    print(f"  💥 Errors:  {results['errors']}")


def main():
    parser = argparse.ArgumentParser(description="Auto Form Submitter")
    parser.add_argument("--config", required=True, help="YAML config file")
    parser.add_argument("--wallets", help="CSV/JSON wallets file")
    parser.add_argument("--batch", type=int, default=5, help="Batch size")
    parser.add_argument("--proxy", help="Proxy URL (http/socks5)")
    args = parser.parse_args()

    if args.wallets:
        asyncio.run(batch_submit(args.config, args.wallets, args.batch))
    else:
        config = load_config(args.config)
        if args.proxy:
            config["proxy"] = args.proxy
        asyncio.run(submit_form(config))


if __name__ == "__main__":
    main()
