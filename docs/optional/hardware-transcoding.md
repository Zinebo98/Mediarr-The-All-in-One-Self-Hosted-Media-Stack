# Optional · Hardware Transcoding (Intel iGPU passthrough)

How I gave a headless Jellyfin VM hardware-accelerated transcoding and HDR tone mapping by passing the host's **Intel UHD 730 iGPU** through to it.

> ⚙️ **Optional & hardware-specific.** This walks through **Intel iGPU** passthrough (QSV) on a Proxmox VM. If you're on **bare metal**, skip the passthrough steps and go straight to the Jellyfin config. On **AMD** use VAAPI, on **NVIDIA** use NVENC, and if your clients direct-play you may not need any of this at all.

## The problem

The media VM had no GPU, so Jellyfin transcoded in software. A single 4K HDR remux's trickplay generation ran for **10.5 hours** before I killed it; CPU sat near 100% across all vCPUs during any HDR transcode. The discrete GPU (an RX 590) was already passed through to a separate gaming VM, but the CPU's **integrated** GPU was unused — ideal for QSV transcoding (low power, excellent HDR tone mapping).

## Environment

- **Host:** Proxmox VE 9, ASUS B660M, Intel i5-13400 (UHD 730 iGPU)
- **Guest:** Debian 13 VM running the media stack in Docker
- IOMMU already enabled (the RX 590 passthrough proved VT-d was on)

## Steps

### 1. Enable the iGPU in BIOS
With a discrete GPU installed, the board disabled the iGPU by default. Set **iGPU Multi-Monitor = Enabled** so both GPUs are active. After reboot, `lspci -nn | grep -i vga` showed the Intel device (`8086:4682`) alongside the AMD card.

### 2. Bind the iGPU to `vfio-pci` on the host
The iGPU sat alone in its own IOMMU group (clean isolation). Bound it to vfio so Proxmox's own driver wouldn't claim it:

```bash
# /etc/modprobe.d/vfio.conf
options vfio-pci ids=8086:4682
softdep i915 pre: vfio-pci
```
```bash
printf "vfio\nvfio_iommu_type1\nvfio_pci\n" >> /etc/modules
update-initramfs -u -k all
reboot
```
Verified with `lspci -nnk -s 00:02.0` → `Kernel driver in use: vfio-pci`.

### 3. Attach the iGPU to the VM
```bash
qm snapshot 106 pre-igpu        # safety net
qm set 106 -machine q35
qm set 106 -hostpci0 0000:00:02,pcie=1
qm stop 106 && qm start 106
```
Used **q35** for proper PCIe topology. Kept the snapshot in case the machine-type change broke boot (it didn't — networking survived).

### 4. Swap the kernel inside the VM
The VM ran the Debian **cloud** kernel, which ships **without the `i915` driver**, so `/dev/dri` never appeared. Installed the standard kernel + firmware + Intel media driver (after enabling `non-free-firmware` / `non-free`):

```bash
apt install -y linux-image-amd64 firmware-misc-nonfree intel-media-va-driver-non-free vainfo
```

The cloud and generic kernels shared a version, so GRUB kept booting cloud. Removed the cloud kernel so the generic one (with `i915`) became default, then rebooted. `uname -r` no longer contained `cloud`, and `/dev/dri/renderD128` finally appeared. `vainfo` confirmed **`VAProfileHEVCMain10`** (4K HDR 10-bit) and **`VAProfileAV1Profile0`** decode.

### 5. Pass `/dev/dri` into the Jellyfin container
```yaml
devices:
  - /dev/dri:/dev/dri
group_add:
  - "991"          # the VM's `render` group GID (getent group render)
environment:
  - LIBVA_DRIVER_NAME=iHD
```

### 6. Configure Jellyfin
Dashboard → Playback → Transcoding: **Intel QuickSync (QSV)**, device `/dev/dri/renderD128`, enable HEVC / HEVC-10bit / AV1 decode, and **VPP tone mapping** (the OpenCL tone-map path fails on the LinuxServer image because it has no OpenCL runtime). Enabled the same HW acceleration for trickplay.

## Result

`intel_gpu_top` during a 4K HDR Dolby-Vision transcode showed the **Video**, **Video Enhance** (tone map) and **Render** engines all active — the full decode → tone-map → encode pipeline on the iGPU. CPU usage dropped from ~600% (software) to background noise, and trickplay that took 10.5 hours now completes in minutes.

## Gotchas worth remembering

- **Cloud kernels have no `i915`.** This silently blocked `/dev/dri` until the kernel swap.
- **Identical kernel versions** (cloud vs generic) make GRUB pick the wrong one — remove the unwanted kernel rather than fighting boot order.
- **OpenCL tone mapping ≠ VPP tone mapping.** The LinuxServer image lacks OpenCL; use VPP on Intel.
- **Hardware acceleration does nothing for library *scanning*** — only for playback/extraction. Diagnose those separately.
