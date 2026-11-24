"""Alert when Whistler's Never Ever Days page stops saying "Coming Soon"."""
import os
import urllib.request

URL = "https://www.whistlerblackcomb.com/plan-your-trip/ski-and-ride-lessons/never-ever-days"
MARKER = "Coming Soon"  # shown on the page until registration opens
TOPIC = os.environ["NTFY_TOPIC"]  # your private ntfy topic, stored as a GitHub secret


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (personal page checker)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
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
        print(f"Fetch failed, will retry next run: {e}")
        return

    # If the page didn't load properly (blocked, error page), don't send a false alert.
    if "Never Ever Days" not in html:
        print("Unexpected page content, skipping.")
        return

    if MARKER in html:
        print("Still coming soon.")
    else:
        print("Marker is gone - registration may be open!")
        notify("The Never Ever Days page changed. Registration may be open. Tap to check.")


if __name__ == "__main__":
    main()
