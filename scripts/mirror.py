#!/usr/bin/env python3
"""Copy the sandbox providers' index, in the format conches before the
move read (format 1, files under providers/), from conch-integrations'
site into OUT, checking each file against the hash its index gives.

    mirror.py OUT
"""

import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

SITE = "https://amitgb14.github.io/conch-integrations"


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read()


def main(out):
    out = Path(out)
    # The legacy copy, once conch-integrations builds one; until then its
    # own index is still format 1, as it was before the move.
    for base in (SITE + "/legacy", SITE):
        try:
            index = json.loads(get(base + "/index.json"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            raise
        if index.get("format") == 1:
            break
    else:
        raise SystemExit("no format-1 index at " + SITE)
    for e in index.get("providers", []):
        path = e["file"]
        if not path.startswith("providers/") or ".." in path:
            raise SystemExit(f"{e.get('name')}: file {path!r}")
        data = get(base + "/" + path)
        if hashlib.sha256(data).hexdigest() != e["sha256"]:
            raise SystemExit(f"{e['name']}: its file does not match the index's hash")
        (out / path).parent.mkdir(parents=True, exist_ok=True)
        (out / path).write_bytes(data)
    (out / "index.json").write_text(json.dumps(index, indent=2) + "\n")
    (out / "index.html").write_text(
        '<!DOCTYPE html><meta charset="utf-8"><title>moved</title>'
        '<p>The registry moved to <a href="https://amitgb14.github.io/conch-integrations/">conch-integrations</a>.</p>\n')
    print(f"{len(index.get('providers', []))} providers mirrored from {base}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
