from datetime import datetime
import random
from typing import Dict

def pick_random_headers() -> Dict[str, str]:
    rnd = random.Random()

    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Contact: xbartalos@stuba.sk",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36, Contact: xbartalos@stuba.sk",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36, Contact: xbartalos@stuba.sk",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1, Contact: xbartalos@stuba.sk",
    ]
    langs = ["en-US,en;q=0.9", "en-GB,en;q=0.9", "en-US;q=0.8,en;q=0.7"]
    refs = ["https://www.google.com/", "https://www.bing.com/", "https://duckduckgo.com/", "https://openlibrary.org/"]
    # xffs = [None, "203.0.113.45", "198.51.100.23", "192.0.2.14"]
    static = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}


    pick = (lambda pool: (rnd.choice(pool) if pool else None))

    headers = {}
    headers.update(static)


    ua = pick(uas)
    if ua:
        headers["User-Agent"] = ua + str(datetime.now().timestamp())

    lang = pick(langs)
    if lang:
        headers["Accept-Language"] = lang

    ref = pick(refs)
    if ref:
        headers["Referer"] = ref

    # xff = pick(xffs)
    # if xff:
    #     headers["X-Forwarded-For"] = xff

    final = {str(k): str(v) for k, v in headers.items() if v is not None}

    return final
