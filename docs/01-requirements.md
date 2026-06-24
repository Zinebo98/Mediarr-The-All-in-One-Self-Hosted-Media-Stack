# 01 · Requirements

What you need before building Mediarr — hardware, software, and accounts. The stack is **streaming-first** (most content is played on-demand from a debrid service), so local horsepower and storage needs are lower than a traditional download-everything setup.

---

## Hardware

| Tier | CPU | RAM | Storage | Notes |
| --- | --- | --- | --- | --- |
| **Minimum** | 2 cores (x86-64) | 4 GB | ~20 GB for OS + appdata | Streaming-only, 1–2 viewers, little/no local transcoding |
| **Recommended** | 4–6 cores | 8–16 GB | SSD for appdata + as much bulk storage as you want to keep locally | Comfortable for the full stack incl. Whisper |
| **This build** | Intel i5-13400 (10c/16t) | 16 GB (VM) | NVMe (appdata) + ZFS pool (media) | Headroom to spare |

Notes:
- **Storage is flexible.** Because the "Instant" libraries stream from debrid, you only need disk for the content you *download and keep*. A pure-streaming setup can run on a tiny disk; a hoarder setup wants bulk storage.
- **Whisper** (AI subtitles) is the heaviest component (CPU-bound). On a 2-core box, leave it out or run it sparingly.
- **Network:** a solid downstream matters most (debrid streaming). Decent upstream only matters if you serve to people outside your home.

## Optional — GPU for hardware transcoding

Only needed if clients can't direct-play and Jellyfin has to **transcode** (or for fast trickplay/HDR tone-mapping). If everything direct-plays, you can skip this entirely.

| GPU | Path in Jellyfin | Notes |
| --- | --- | --- |
| **Intel iGPU (Quick Sync)** | QSV / VAAPI | Best value; excellent HDR tone-mapping. Used in this build — see `optional/hardware-transcoding.md` |
| **AMD** | VAAPI | Works; HDR tone-mapping support is weaker |
| **NVIDIA** | NVENC | Strong, but higher power draw |
| **None** | CPU (software) | Fine if you mostly direct-play; a modern multi-core CPU can do a stream or two |

> If you virtualize (e.g. Proxmox) and want GPU transcoding, the GPU must be **passed through** to the VM — that's the optional hardware guide.

## Software

- A **Linux host with Docker + Docker Compose**. That's the only hard requirement.
- **Proxmox / virtualization is optional** — this build runs the stack in a Debian VM on Proxmox, but it works equally well on a bare-metal Linux box, a NAS that runs Docker, etc.
- A reverse proxy and/or **Tailscale** (optional) for secure remote access.

---

## Accounts & Services

### Free (just need an API key)
| Service | Used by | Purpose |
| --- | --- | --- |
| **TMDB** | AIOMetadata, *arr | Primary metadata + artwork |
| **TheTVDB** | AIOMetadata | Series/anime metadata |
| **Trakt** | AIOMetadata | Watch history + personalized catalogs (needs a free OAuth app) |
| **RPDB** *(optional)* | AIOMetadata | Ratings on posters (`t0-free-rpdb` free key) |
| **OpenSubtitles** | Bazarr | Subtitles (free tier works; VIP is the paid upgrade below) |

### Paid (what this build uses — all optional, with alternatives)
| Service | Cost | Role | If you don't want to pay |
| --- | --- | --- | --- |
| **TorBox Pro** | ~$10/mo | Debrid backend — cached torrents (Decypharr) **and** usenet | **Real-Debrid** (~€3/mo), **AllDebrid**, **Premiumize**; or skip debrid and run a normal torrent client + VPN (needs storage + seeding etiquette) |
| **NZBFinder** | ~$15/yr | Usenet indexer (NZBs for TorBoxarr) | Any usenet indexer (NZBGeek, DrunkenSlug…) + a usenet provider; **or skip usenet** and go torrent-only |
| **OpenSubtitles VIP** | ~$10–15/yr | 1,000 subtitle downloads/day, no ads | Free OpenSubtitles tier (lower daily limit) is fine for light use |

> **The whole paid layer is substitutable.** The cheapest viable path is a single debrid subscription (e.g. Real-Debrid) for torrents and skipping usenet entirely — that alone gives you most of the experience. Usenet (TorBox + NZBFinder) is what adds fast, reliable, well-retained releases on top.

---

## Before you start, create these

1. A **debrid** account (TorBox or alternative) → grab its API token.
2. *(Optional)* a **usenet indexer** account (NZBFinder) → note host/credentials.
3. **TMDB**, **TheTVDB**, and a **Trakt OAuth app** → API keys.
4. *(Optional)* **RPDB**, **OpenSubtitles** (VIP if you want).

Keep these handy — they go into the various `.env` files and service configs in the next steps.

➡️ Next: [`02-host-and-storage.md`](02-host-and-storage.md)
