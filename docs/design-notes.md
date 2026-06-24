# Design Notes — Decisions & Trade-offs

The *why* behind the build. Anyone can wire containers together; these are the choices that took thought, each framed as **decision → reasoning → trade-off**.

---

### Intel iGPU (QuickSync) over the discrete RX 590

**Decision:** transcode on the Intel iGPU, not the AMD card.
**Why:** the workload is 4K HDR → SDR **tone mapping**, which QSV does in hardware fast and cleanly. On AMD/Linux, HDR tone mapping needs OpenCL, which Polaris (RX 590) supports poorly — it would have fallen back to slow software. The iGPU also idles at a few watts vs the RX 590's tens of watts, which matters on a 24/7 box.
**Trade-off:** required iGPU passthrough to the VM (BIOS + vfio + kernel swap). Worth it — software trickplay once took 10.5 hours per file; on the iGPU it's minutes.

### VPP tone mapping, not OpenCL tone mapping

**Decision:** use Jellyfin's **VPP** tone mapping.
**Why:** the LinuxServer Jellyfin image has no OpenCL runtime, so the OpenCL tone-map path throws a fatal ffmpeg error. VPP is Intel-native and needs no OpenCL.
**Trade-off:** VPP is marginally less refined than a tuned OpenCL tonemap — but it actually works, and looks great.

### Targeted scanning instead of full library scans

**Decision:** disable Jellyfin's full "Scan Media Library" task; use the Targeted Scans plugin + a reconcile script.
**Why:** full scans hang on the Instant (streaming) libraries, and real-time monitoring misses files during restarts. Targeted per-path scanning adds new items instantly without ever scanning the streaming libraries.
**Trade-off:** one extra moving part (a cron script) — but it's a self-healing safety net and the only reliable option given the Instant libraries.

### Prefer-IPv4 rather than disabling IPv6

**Decision:** make the host/containers prefer IPv4 (`gai.conf`) instead of killing IPv6.
**Why:** the VM advertised IPv6 with no working route, so apps stalled trying it first. Fully disabling IPv6 would have broken Tailscale (which uses IPv6 internally).
**Trade-off:** IPv6 stays "on" but unused for public traffic — slightly less clean than a full disable, but keeps remote access working.

### ZFS stripe for media, separate pool for the irreplaceable data

**Decision:** media lives on a 2-disk **stripe** (no redundancy); the one dataset that matters sits on its own pool.
**Why:** media is re-acquirable, so capacity beats redundancy there. Backing it up would waste disks. The single irreplaceable dataset is isolated so it *can* be protected without dragging the whole pool along.
**Trade-off:** lose either media disk and the media pool is gone — an accepted risk, because re-downloading is cheap and the important data is elsewhere.

### Two debrid backends (Decypharr + TorBoxarr)

**Decision:** Decypharr for TorBox **torrents**, TorBoxarr for TorBox **usenet**.
**Why:** Decypharr handles TorBox torrents brilliantly but doesn't support TorBox usenet — so a second shim (TorBoxarr, emulating SABnzbd) covers NZBs from NZBFinder. Torrents = instant cached pulls; usenet = excellent retention/quality.
**Trade-off:** two download clients to maintain instead of one — but each is best-in-class at its job.

### No size limits (a deliberate TRaSH deviation)

**Decision:** remove the upper/lower size caps in the quality profiles.
**Why:** short-runtime anime films were perfect quality but fell *under* TRaSH's minimum-size floor and got rejected. Dropping the limits fixed it.
**Trade-off:** occasionally a release is larger/smaller than "ideal" — acceptable for never missing a good file.

### Anime as its own library + indexer-tag routing

**Decision:** a separate Anime library, and `anime-only` / `standard-tv` tags routing indexers.
**Why:** Jellyfin handles anime better as its own library (ordering, artwork), and the tags stop Sonarr wasting searches on anime trackers for regular shows (and vice-versa).
**Trade-off:** a bit more setup (tags + a second root) for cleaner results and faster searches. (Anime *films* stay in Movies — only series get the anime treatment.)

### Whisper as a narrow, last-resort subtitle fallback *(planned)*

**Decision:** Whisper (AI speech-to-text) only for anime dubs with no adequate English subtitle, tuned `small.en` / int8 / CPU-capped. *(Designed but not yet wired in — see doc 07.)*
**Why:** real subtitle providers cover ~everything else; Whisper is slow and not as clean as human subs, so it's the floor, not the default. The model/quantisation/CPU cap keep it from starving the box.
**Trade-off:** transcribed subs are imperfect — fine as a "something is better than nothing" fallback.

### Catalogs/templates: standing on community work

**Decision:** base AIOMetadata catalogs on **luckynumb3rs** and AIOStreams on **Tam-Taro's Complete template**, then customise.
**Why:** these are well-maintained, sensible baselines — no reason to hand-build hundreds of catalogs and filter rules from scratch.
**Trade-off:** none, really — you inherit good defaults and tweak. Credit where due (both linked in `10-streaming-tier.md`).

### Single account, local-only

**Decision:** one user, LAN-only, no internet-facing access.
**Why:** it's a personal build; not exposing it removes a whole class of security/maintenance concerns.
**Trade-off:** no remote sharing as-is — but that's the intended sc