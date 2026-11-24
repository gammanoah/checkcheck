import os
import urllib.request
from playwright.sync_api import sync_playwright

URL = "https://www.whistlerblackcomb.com/plan-your-trip/ski-and-ride-lessons/never-ever-days"
MARKER = "coming soon"  # compared in lowercase
TOPIC = os.environ["NTFY_TOPIC"]


def fetch_text():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            locale="en-CA",
        )
        page = ctx.new_page()
        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        title = page.title()
        text = page.inner_text("body")
        browser.close()
    return title, text


def notify(message):
    req = urllib.request.Request(
        f"https://ntfy.sh/{TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": "Never Ever Days update", "Priority": "urgent", "Click": URL},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=30)


def main():
    try:
        title, text = fetch_text()
    except Exception as e:
        print(f"Fetch failed: {e}")
        return

    low = text.lower()
    print("Title:", title)
    print("Length:", len(text))
    print("Has 'never ever':", "never ever" in low)
    print("Has 'coming soon':", MARKER in low)
    print("First 300 chars:", text[:300].replace("\n", " "))

    if "never ever" not in low:
        print("Unexpected page content, skipping.")
        return

    if MARKER in low:
        print("Still coming soon.")
    else:
        print("Marker is gone - registration may be open!")
        notify("The Never Ever Days page changed. Registration may be open. Tap to check.")


if __name__ == "__main__":
    main()
