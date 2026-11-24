zQ<div align="center">
  <img src="packaging/linux/hicolor/256x256/apps/astralcord.png" width="128" alt="AstralCord logo">
  <h1>AstralCord</h1>
  <p>A fast, native Discord client written in Rust, for Windows and Linux.</p>
</div>

AstralCord is a native desktop client built with Rust, [egui](https://github.com/emilk/egui) and
[wgpu](https://wgpu.rs). There's no Electron and no web wrapper, so it starts quickly and uses
little memory. It supports:

- Servers, DMs and threads
- Voice and video calls, including screen share and noise suppression
- Themes and extensions
- A tray icon and global push-to-talk

> [!WARNING]
> **Unofficial and not endorsed by Discord.** Like Serein, AstralCord talks to Discord's servers
> directly with your account. Discord's Terms of Service don't allow this, and accounts can be
> terminated for it. Use it at your own risk, ideally not on an account you can't afford to lose.

## Download

Open this repo's **Releases** page and grab the newest release marked **Pre-release**
(`v1.0.0-nightly.…`):

| Platform | File | How to run |
|---|---|---|
| Windows 10/11 | `astralcord-…-Windows-X64-Setup.exe` | Run the installer (no admin needed) |
| Windows, no install | `astralcord-…-Windows-X64.zip` | Unzip it and run `astralcord.exe` |
| Linux, any distro | `astralcord-…-Linux-X64.AppImage` | `chmod +x` it, then run it |

### Linux AppImage requirements

The AppImage uses GTK 4 and WebKitGTK 6.0 from your system, plus Vulkan for drawing. Install them once.

On **Arch, Garuda or Manjaro**:

```sh
sudo pacman -S --needed gtk4 webkitgtk-6.0 vulkan-icd-loader libpulse alsa-lib gst-plugins-base-libs fuse3
```

On **Ubuntu 24.04+ or Debian**:

```sh
sudo apt install libgtk-4-1 libwebkitgtk-6.0-4 libvulkan1 libpulse0 libasound2t64 \
  libgstreamer-plugins-base1.0-0 fuse3
```

Saved logins go to your desktop's keyring (GNOME Keyring or KWallet) when one is running.
Otherwise AstralCord keeps them in a private file in its data folder.

## Updates

AstralCord updates itself from this repo's releases (**Settings → Updates**). This works for the
Windows installer, the Windows zip and the AppImage. Every push to `main` builds a new release
automatically.

## Where your data lives

- Windows: `%LOCALAPPDATA%\astralcord`
- Linux: `~/.local/share/astralcord`

## How it's built

[`.github/workflows/build.yml`](.github/workflows/build.yml) runs on GitHub Actions for every push
to `main`:

1. It builds the Windows installer and zip.
2. It builds the Linux AppImage in parallel.
3. It publishes them, with checksums, as a pre-release tagged `v1.0.0-nightly.<date>.<run>`.

To build locally, follow Serein's instructions in [`docs/serein-README.md`](docs/serein-README.md).
The pinned toolchain is Rust 1.99.1. Run `cargo xtask package` on Windows, or
`cargo xtask package --format appimage` on Linux.


## License

Like Serein, AstralCord is available under either the [MIT](LICENSE-MIT) or the
[Apache 2.0](LICENSE-APACHE) license, at your option. Third-party notices are in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
