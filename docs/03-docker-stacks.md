# 03 · Docker Stacks

How the containers are organized and brought up. The repo ships a **consolidated** [`docker-compose.yml`](../docker-compose.yml) so you can see the whole stack in one file — but in practice it's split into a few smaller stacks, which is easier to manage and restart independently.

---

## One big file vs. split stacks

Two valid approaches:

- **Single compose file** — everything in one `docker-compose.yml`. Simplest to start with; use the repo's consolidated file as-is.
- **Split stacks (this build)** — grouped by purpose so you can restart one part without touching the rest:

```
/opt/
├── mediastack/      docker-compose.yml + .env   → jellyfin, *arr, jellyseerr,
│                                                   flaresolverr, decypharr, recyclarr, whisper
├── torboxarr/       docker-compose.yml + .env   → torboxarr (usenet)
├── aiostreams/      docker-compose.yml + .env   → aiostreams
└── aiometadata/     docker-compose.yml + .env   → aiometadata + redis
```

Each folder is an independent stack with its **own `.env`**. Pick whichever model you like — the rest of the guide works the same either way.

---

## The `.env` files

Secrets and host-specific values never live in the compose file — they come from `.env`. Start from the template:

```bash
cp .env.example .env
```

Fill in at least:

```bash
PUID=1000          # from `id $USER` in step 02
PGID=1000
TZ=Europe/Belgrade

RENDER_GID=        # only if doing GPU transcoding (getent group render)
```

Service-specific keys (TorBox token, NZBFinder login, TMDB/Trakt, etc.) go into the relevant stack's `.env` as you reach each step. See [`.env.example`](../.env.example) for the full list.

> 🔒 `.env` is git-ignored and must **never** be committed. The compose files only reference `${VARS}` — no secrets in them.

---

## Bringing a stack up

From inside a stack folder:

```bash
cd /opt/mediastack
docker compose up -d        # create/start in the background
docker compose ps           # check status
docker compose logs -f jellyfin   # follow one service's logs
```

Repeat for each stack (`torboxarr`, `aiostreams`, `aiometadata`).

**Order doesn't matter much** — the only hard dependency is Redis before AIOMetadata, which the compose `depends_on` + healthcheck already handles. Everything else discovers each other over the Docker network by container name (e.g. Sonarr reaches Decypharr at `http://decypharr:8282`).

---

## Updating later

```bash
cd /opt/<stack>
docker compose pull          # grab newer images
docker compose up -d         # recreate changed containers
docker image prune -f        # clean up old layers
```

> Tip: pin critical images to a version (this build pins Whisper to `:v1.9.1`) so a `pull` doesn't unexpectedly break something. `:latest` is convenient but can drift.

---

## Verify

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}'
```

You should see your containers `Up`. Each service's web UI is then reachable at `http://<host-ip>:<port>` — the ports are listed per service in [`README.md` → Services](../README.md#services).

---

✅ Containers are running. Next we wire up the download path so the *arr apps have somewhere to send grabs.

➡️ Next: [`04-downloads.md`](04-downloads.md)
