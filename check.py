import os
import re
import urllib.request

URL = "https://www.whistlerblackcomb.com/plan-your-trip/ski-and-ride-lessons/never-ever-days"
MARKER = "Coming Soon"
TOPIC = os.environ["NTFY_TOPIC"]


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-CA,en;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("HTTP status:", resp.status)
        return resp.read().decode("utf-8", errors="replace")


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
        html = fetch(URL)
    except Exception as e:
        print(f"Fetch failed: {e}")
        return

    title = re.search(r"<title>(.*?)</title>", html, re.S)
    print("Length:", len(html))
    print("Title:", title.group(1).strip() if title else None)
    print("Has 'Never Ever':", "Never Ever" in html)
    print("Has 'Coming Soon':", "Coming Soon" in html)
    print("First 300 chars:", html[:300].replace("\n", " "))

    if "Never Ever" not in html:
        print("Unexpected page content, skipping.")
        return

    if MARKER in html:
        print("Still coming soon.")
    else:
        print("Marker is gone - registration may be open!")
        notify("The Never Ever Days page changed. Registration may be open. Tap to check.")


if __name__ == "__main__":
    main()
