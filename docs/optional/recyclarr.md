# Optional · Recyclarr & Quality Profiles

⚙️ *Optional but recommended.* This is the deep-dive on where Sonarr/Radarr quality profiles come from, how to build/customise one, and how **Recyclarr** automates a TRaSH-Guides baseline. If you're happy letting Recyclarr do it, you only need the [Quick start](#quick-start). If you want to understand and tweak, read on.

---

## How quality actually works in *arr

Three pieces combine to decide what gets grabbed and what counts as an "upgrade":

1. **Qualities** — the resolution/source ladder: `WEBDL-1080p`, `Bluray-2160p`, `Remux-2160p`, etc. You order and (optionally) group them in a profile.
2. **Custom Formats (CFs)** — scored tags for *everything else*: HDR/DV, audio (Atmos/TrueHD), release-group tiers, repack/proper, unwanted junk. Each CF has a **score**.
3. **Quality Profile** — ties it together: which qualities are allowed, the **Upgrade Until** cutoff, and the **sum of CF scores** that defines "better." A release's total score + quality position decides if it's grabbed or upgraded.

Hand-building good custom formats (there are dozens) is tedious — which is exactly what Recyclarr solves.

---

## What Recyclarr does

Recyclarr reads a YAML config and **pushes TRaSH-Guides custom formats + quality-profile definitions into Sonarr/Radarr** for you — and keeps them updated on each sync. You get a battle-tested baseline in minutes instead of hours of manual scoring.

- **Skip it** → build profiles by hand (see [Building a profile manually](#building-a-quality-profile-manually)).
- **Use it** → get the baseline, then layer your own tweaks on top.

---

## Quick start

The `recyclarr` container is already in the stack (step 03). Its config lives at `/opt/mediastack/appdata/recyclarr/recyclarr.yml`.

1. Add the templates you want (TRaSH-derived) for each app. A minimal example:

```yaml
sonarr:
  series:
    base_url: http://sonarr:8989
    api_key: !env_var SONARR_API_KEY
    include:
      - template: sonarr-quality-definition-series
      - template: sonarr-v4-quality-profile-web-2160p
      - template: sonarr-v4-custom-formats-web-2160p
      # anime:
      - template: sonarr-v4-quality-profile-anime
      - template: sonarr-v4-custom-formats-anime

radarr:
  movies:
    base_url: http://radarr:7878
    api_key: !env_var RADARR_API_KEY
    include:
      - template: radarr-quality-definition-movie
      - template: radarr-quality-profile-remux-web-2160p
      - template: radarr-custom-formats-remux-web-2160p
```

2. Sync it into Sonarr/Radarr:

```bash
docker exec recyclarr recyclarr sync
```

3. (Optional) run it on a schedule so the baseline stays current (cron, or the container's built-in scheduling).

Full template list + syntax: **[recyclarr.dev](https://recyclarr.dev)**.

---

## Verify in Sonarr/Radarr

After a sync, the profiles + custom formats appear in the app:

- *Settings → Profiles* — your new quality profiles
- *Settings → Custom Formats* — the imported CFs with their scores

---

## Building a quality profile manually

Whether you skip Recyclarr or just want to tweak, here's the profile editor (*Settings → Profiles → +*):

- **Qualities** — drag to order; tick the ones to allow. Group qualities (e.g. WEB-2160p + Bluray-2160p) so they're treated as equal.
- **Upgrade Until** — the cutoff; Sonarr stops upgrading once it reaches this.
- **Custom Formats + scores** — set a score per CF; the profile prefers releases with a higher total.
- **Minimum Custom Format Score** — a floor a release must clear to be grabbed at all.
- **Language** — e.g. require/prefer a language (handy for the anime dual-audio profile).

---

## This build's deviation — no size limits

This setup removes the upper/lower **size limits** (a TRaSH deviation), because short-runtime anime films were being rejected for falling under the minimum size:

*Settings → Quality* → set min/max size for the relevant qualities to unrestricted.

> ⚠️ Do this **after** a Recyclarr sync. If Recyclarr manages your quality *definitions*, it can reset size limits on the next sync — either re-apply afterward, or set the sizes in the Recyclarr config so they persist.

---


⬅️ Back to [`05-arr-suite.md`](../05-arr-suite.md)
