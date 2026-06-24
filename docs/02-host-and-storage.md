# 02 · Host & Storage

The foundation. Get the folder layout and permissions right here and every later step "just works"; get them wrong and you'll fight import errors and broken hardlinks forever.

---

## The host

You need **one Linux machine running Docker + Docker Compose**. That's it. How you get there is up to you:

- **Bare metal** — simplest; install Debian/Ubuntu + Docker and go.
- **VM (this build)** — a Debian VM on a Proxmox host. Good if the box does other things too. Only relevant extra step: if you want GPU transcoding, the GPU must be passed through to the VM — see [`optional/hardware-transcoding.md`](optional/hardware-transcoding.md).
- **NAS / mini-PC** — anything that runs Docker works.

Install Docker (official convenience script) if you don't have it:

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # log out/in after
```

---

## A single user & group for everything

Every container runs as the **same UID/GID** so all files have consistent ownership. This is what lets the *arr apps **hardlink / instant-move** between downloads and your library instead of slow copies.

```bash
id $USER          # note your uid/gid, e.g. 1000:1000
```

Use those as `PUID` / `PGID` in your `.env` (next step). Pick one identity and use it everywhere.

---

## Folder layout

The golden rule: **downloads and the media library live on the same filesystem**, so moves are atomic (instant) and hardlinks work.

```
/srv/media/                     ← one filesystem (mount the whole thing into containers)
├── library/
│   ├── movies/                 ← Radarr root
│   ├── tv/                     ← Sonarr root (standard)
│   └── anime/                  ← Sonarr root (anime series only; anime FILMS go to movies/)
└── downloads/                  ← download client output

/mnt/debrid/                    ← debrid FUSE mount (created by Decypharr, see step 04)

/opt/<stack>/appdata/<service>/ ← each container's /config (Jellyfin, Sonarr, …)
```

Create it and set ownership:

```bash
sudo mkdir -p /srv/media/library/{movies,tv,anime} /srv/media/downloads
sudo chown -R 1000:1000 /srv/media      # use YOUR PUID:PGID
```

Why a separate **anime** root: Jellyfin handles anime series better as their own library (correct ordering, metadata agents, naming). Anime **movies** stay in `movies/` — only series go to `anime/`.

---

## How the mounts reach the containers

Inside the compose files you'll see two important mount styles:

- `/srv/media:/srv/media` — the library + downloads, mounted **the same path inside and out**. Keeping the path identical everywhere avoids "works in Radarr, breaks in Jellyfin" path-mismatch bugs.
- `/mnt/debrid:/mnt/debrid:rslave` (and `rshared` on Decypharr) — the debrid FUSE mount. Decypharr *creates* the mount (`rshared` so it propagates out), and the other containers *consume* it (`rslave` so they see it appear). This is what makes streamed debrid content visible to Jellyfin/the *arr apps.

> You don't need to fully understand mount propagation — just don't change `rshared`/`rslave` on those lines; they're what makes the debrid mount show up everywhere.

---

## Storage sizing (recap from step 01)

- **Streaming-first:** local disk only holds what you deliberately download + appdata. A small SSD is enough.
- **Hoarding:** add bulk storage for `/srv/media/library`. Any filesystem works — this build uses ZFS (a stripe for re-acquirable media, a separate pool for the one dataset that needs backup), but ext4/btrfs/whatever is fine.

---

✅ At this point you have: a Docker host, a single UID/GID identity, and the `/srv/media` tree owned by it.

➡️ Next: [`03-docker-stacks.md`](03-docker-stacks.md)
