#!/usr/bin/env python3
"""
jellyfin-reconcile.py

Compares the video files on disk against what Jellyfin already has in its
library, and triggers an INSTANT targeted scan for anything that's on disk
but missing from Jellyfin. It never runs a full library scan, so it won't
touch the Gelato / streaming libraries and won't hang.

Targeted scanning uses the "Targeted Scans" plugin's /Library/ScanPath
endpoint (https://github.com/d3v1l1989/targeted-scans). If that plugin is
not installed the script falls back to Jellyfin's native /Library/Media/Updated
(which works but is slower/delayed).

Usage:
    JELLYFIN_URL=http://localhost:8096 \
    JELLYFIN_API_KEY=xxxxxxxxxxxx \
    python3 jellyfin-reconcile.py

Optional:
    LIBRARY_ROOTS=/srv/media/library/movies,/srv/media/library/tv
    DRY_RUN=1     # report what's missing but don't trigger scans
"""

import os
import sys
import json
import urllib.request
import urllib.error

JELLYFIN_URL = os.environ.get("JELLYFIN_URL", "http://localhost:8096").rstrip("/")
API_KEY = os.environ.get("JELLYFIN_API_KEY", "")
DRY_RUN = os.environ.get("DRY_RUN", "") not in ("", "0", "false", "False")

# Real on-disk library roots to reconcile. NOT the Gelato/streaming libs.
LIBRARY_ROOTS = [
    p.strip()
    for p in os.environ.get(
        "LIBRARY_ROOTS",
        "/srv/media/library/movies,/srv/media/library/tv",
    ).split(",")
    if p.strip()
]

VIDEO_EXTS = {".mkv", ".mp4", ".avi", ".m4v", ".ts", ".wmv", ".mov", ".mpg", ".mpeg"}


def api(method, path, body=None):
    url = JELLYFIN_URL + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f'MediaBrowser Token="{API_KEY}"')
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw.strip() else {}


def known_paths():
    """Every file path Jellyfin currently has indexed (movies + episodes)."""
    res = api(
        "GET",
        "/Items?Recursive=true&IncludeItemTypes=Movie,Episode"
        "&Fields=Path&enableImages=false&enableUserData=false",
    )
    paths = set()
    for item in res.get("Items", []):
        p = item.get("Path")
        if p:
            paths.add(os.path.normpath(p))
    return paths


def disk_video_files(root):
    out = []
    for dirpath, _dirs, files in os.walk(root):
        for f in files:
            if os.path.splitext(f)[1].lower() in VIDEO_EXTS:
                out.append(os.path.normpath(os.path.join(dirpath, f)))
    return out


def scan_path(path):
    """Try the Targeted Scans plugin first; fall back to native media-updated."""
    try:
        r = api("POST", "/Library/ScanPath", {"Path": path})
        return r.get("Status", "OK"), r.get("Message", "")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Plugin not installed -> native fallback (slower, may be delayed)
            try:
                api(
                    "POST",
                    "/Library/Media/Updated",
                    {"Updates": [{"Path": path, "UpdateType": "Created"}]},
                )
                return "QueuedNative", "via /Library/Media/Updated (install the plugin for instant scans)"
            except urllib.error.HTTPError as e2:
                return "Failed", f"HTTP {e2.code}"
        return "Failed", f"HTTP {e.code}"


def main():
    if not API_KEY:
        sys.exit("ERROR: set JELLYFIN_API_KEY (Dashboard > API Keys)")

    try:
        known = known_paths()
    except urllib.error.HTTPError as e:
        sys.exit(f"ERROR querying Jellyfin (/Items): HTTP {e.code} - check URL/API key")

    missing = []
    for root in LIBRARY_ROOTS:
        if not os.path.isdir(root):
            print(f"WARN: root not found, skipping: {root}")
            continue
        for f in disk_video_files(root):
            if f not in known:
                missing.append(f)

    if not missing:
        print(f"In sync - {len(known)} items indexed, nothing new on disk.")
        return

    print(f"Found {len(missing)} file(s) on disk not in Jellyfin:")
    for f in missing:
        if DRY_RUN:
            print(f"  [dry-run] would scan: {f}")
            continue
        status, msg = scan_path(f)
        print(f"  {status:14} {f}  {('- ' + msg) if msg else ''}")


if __name__ == "__main__":
    main()
