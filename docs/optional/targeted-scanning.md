# Optional · Targeted Scanning

⚙️ *Optional but recommended for this build.* Why this build **never runs full library scans**, and how new local media still appears in Jellyfin within minutes.

---

## The problem

Two things make Jellyfin's normal scanning unreliable here:

1. **Full scans hang** on the **Instant** (Gelato streaming) libraries — `ffprobe` chokes on the virtual/streaming items, so "Scan All Libraries" crawls and parks (the classic stall at ~88%).
2. **Real-time monitoring misses files** that land while Jellyfin is restarting (events aren't replayed), so new downloads sometimes don't show until a manual scan.

So this build disables the full **Scan Media Library** task entirely and replaces it with *targeted* scanning.

---

## The solution: two parts

### 1. Targeted Scans plugin

Adds a `POST /Library/ScanPath` endpoint that creates a single item instantly — **under a second, regardless of library size** — instead of scanning a whole library.

Install (custom repo — see [`../08-jellyfin.md`](../08-jellyfin.md)):
- Repo: `https://raw.githubusercontent.com/d3v1l1989/targeted-scans/main/manifest.json`
- Project: [d3v1l1989/targeted-scans](https://github.com/d3v1l1989/targeted-scans)

### 2. The reconcile script

[`scripts/jellyfin-reconcile.py`](../../scripts/jellyfin-reconcile.py) is a small watchdog that:

- queries Jellyfin's API for everything it already has indexed,
- walks your **local** library folders on disk,
- diffs them, and for anything on disk but missing from Jellyfin, calls the plugin's `ScanPath` to add **just that file** — instantly, never a full scan.

It only touches the real libraries (Movies/Shows/Anime), never the Instant ones.

---

## Setup

1. Generate a Jellyfin API key: *Dashboard → API Keys*.
2. Test it (dry run shows what it *would* scan):

```bash
DRY_RUN=1 JELLYFIN_URL=http://localhost:8096 JELLYFIN_API_KEY=YOURKEY \
LIBRARY_ROOTS=/srv/media/library/movies,/srv/media/library/tv,/srv/media/library/anime \
python3 /opt/scripts/jellyfin-reconcile.py
```

3. Schedule it (every 5 minutes, with a lock so runs don't overlap) — `crontab -e`:

```bash
*/5 * * * * /usr/bin/flock -n /tmp/jf-reconcile.lock env \
  JELLYFIN_URL=http://localhost:8096 JELLYFIN_API_KEY=YOURKEY \
  LIBRARY_ROOTS=/srv/media/library/movies,/srv/media/library/tv,/srv/media/library/anime \
  /usr/bin/python3 /opt/scripts/jellyfin-reconcile.py > /var/log/jellyfin-reconcile.log 2>&1
```

---

## Result

New local media appears in Jellyfin within ~5 minutes, with **zero full scans** — so the Instant libraries never get scanned (and never hang), and nothing slips through the cracks during restarts. It's a self-healing safety net on top of Seerr's import notification and real-time monitoring.

⬅️ Back to [`08-jellyfin.md`](../08-jellyfin.md)
