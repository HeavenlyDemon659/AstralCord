<div align="center">
  <img src="src-tauri/icons/icon.png" width="128" alt="AstralCord logo">
  <h1>AstralCord</h1>
  <p>A tiny, Rust-based Discord client for Linux and Windows.</p>
</div>

AstralCord runs Discord's own web app inside a lightweight native shell written in Rust with [Tauri](https://tauri.app). It's far smaller than the official client, and it supports:

- Voice and video calls
- Themes, plus plugins via shelter, Vencord and Equicord
- Rich Presence and push-to-talk
- A tray icon and multiple profiles

AstralCord is a renamed fork of [Dorion](https://github.com/SpikeHD/Dorion) by SpikeHD. All the clever parts are theirs.

## Download

Get the latest build from this repo's **Releases** page:

| Platform | File | How to run |
|---|---|---|
| Windows 10/11 | `AstralCord_<version>_x64-setup.exe` | Run the installer |
| Windows (no install) | `AstralCord_<version>_win64_portable.zip` | Unzip it and run `AstralCord.exe` |
| Linux, any distro (Arch, Fedora, ...) | `AstralCord_<version>_linux_x64_portable.tar.gz` | Extract it and run `./AstralCord` |
| Debian / Ubuntu / Mint | `AstralCord_<version>_amd64.deb` | `sudo apt install ./AstralCord_<version>_amd64.deb` |

Windows uses Microsoft Edge WebView2, which is already part of Windows 10/11. The Linux build bundles its own Chromium (CEF) runtime, which is what makes voice calls work.

Settings are stored in:

- `%APPDATA%\astralcord` on Windows
- `~/.config/astralcord` on Linux

Portable builds keep everything next to the program instead.

## How builds work

Every push to `main` runs [`.github/workflows/build.yml`](.github/workflows/build.yml) on GitHub Actions:

1. It builds Linux and Windows in parallel.
2. It publishes the files as a Release named after the version in `src-tauri/tauri.conf.json` (for example `v7.0.1`).

To ship an update, bump `version` in `src-tauri/tauri.conf.json` and `src-tauri/Cargo.toml`, then push. Installed copies check this repo's Releases for new versions.

## Building locally

You need [Node.js](https://nodejs.org), [pnpm](https://pnpm.io), [Rust](https://rustup.rs) 1.96+ and the [Tauri prerequisites](https://tauri.app/start/prerequisites/). On Linux you also need `cmake` and `ninja`, because the CEF wrapper is compiled during the build.

```sh
pnpm install
pnpm shupdate          # fetch the bundled shelter fallback
pnpm build:updater     # Windows/macOS only
pnpm tauri build       # add: -c src-tauri/tauri.linux.conf.json on Linux
```

The output goes to `src-tauri/target/release/`, and installers go to `bundle/`. Set `ASTRALCORD_REPO=owner/repo` when building outside GitHub Actions to enable update checks.

## Notes

- Some in-app settings pages are loaded from Dorion's online plugins, so they may still mention "Dorion".
- AstralCord isn't affiliated with or endorsed by Discord or the Dorion project. Discord's Terms of Service don't allow client modifications, so use it at your own risk.

## License

[GPL-3.0](LICENSE), the same as Dorion. If you share builds, share the source too. This repo already does that.
