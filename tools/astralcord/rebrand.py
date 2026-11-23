#!/usr/bin/env python3
"""Rebrand a Serein source snapshot as AstralCord.

Run from anywhere after replacing the tree with a fresh Serein checkout and staging it
(`git add -A`), because files are found through the Git index:

    python3 tools/astralcord/rebrand.py

Changed: everything a user sees or the OS keys on. That covers the name in the interface and
all translations, the app ID, the executable, the installer, the AppImage, the Start Menu
shortcut and tray, the data and credential-store names, and the update source (this fork's
GitHub releases).

Kept: internal identifiers that upstream extensions and the extension catalog rely on
(`.serein-extension` packages, the `serein_*` extension ABI, `__SEREIN_*` page scripts,
`SEREIN_*` environment variables), the Cargo package name `serein`, the upstream extension
catalog URL, font family IDs, macOS bundle paths (macOS isn't built here), and the
"Serein contributors" credits in code.

Safe to re-run: every rule is a no-op on text that is already rebranded.
"""
import pathlib
import re
import subprocess
import sys

NAME = "AstralCord"
LOWER = "astralcord"
APP_ID = "com.astralcord.client"
UPSTREAM_ID = "cz.viceverse.serein"
REPO = "HeavenlyDemon659/AstralCord"
ROOT = pathlib.Path(__file__).resolve().parents[2]

changed: dict[str, set[str]] = {}
problems: list[str] = []


def tracked(*pathspecs: str) -> list[pathlib.Path]:
    out = subprocess.run(["git", "ls-files", "-z", "--", *pathspecs], cwd=ROOT,
                         capture_output=True, check=True).stdout.decode()
    return [ROOT / p for p in out.split("\0") if p]


def text_of(path: pathlib.Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
        return None


def apply(rule: str, paths, func) -> None:
    for path in paths:
        text = text_of(path)
        if text is None:
            continue
        new = func(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.setdefault(rule, set()).add(str(path.relative_to(ROOT)))


def must(path: str, old: str, new: str, *, count: int | None = None) -> None:
    """Exact edit that must apply (or already be applied)."""
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    found = text.count(old)
    if found == 0:
        if new and new in text:
            return  # already rebranded
        problems.append(f"{path}: expected text not found: {old[:70]!r}")
        return
    if count is not None and found != count:
        problems.append(f"{path}: expected {count}x {old[:60]!r}, found {found}")
        return
    file.write_text(text.replace(old, new), encoding="utf-8")
    changed.setdefault("exact edits", set()).add(path)


def rename(old: str, new: str) -> None:
    src, dst = ROOT / old, ROOT / new
    if src.exists():
        subprocess.run(["git", "mv", "-f", old, new], cwd=ROOT, check=True)
        changed.setdefault("renamed files", set()).add(f"{old} -> {new}")
    elif not dst.exists():
        problems.append(f"missing file to rename: {old}")


# --- shared patterns -----------------------------------------------------------------------
# Rust string literals: raw strings first (r"C:\" ends at its quote), then char literals (so a
# '"' char can't shift the pairing), then ordinary and byte strings.
TOKEN = re.compile(
    r'b?r(#*)".*?"\1'  # raw (byte) strings
    r"|'(?:[^'\\\n]|\\.)'"  # char literals
    r'|"(?:[^"\\]|\\.)*"',  # ordinary and byte strings
    re.S,
)
# Upstream URLs that must keep pointing at Serein (e.g. the extension catalog).
NOT_UPSTREAM = r"(?<!ViceVerse-cz/)(?<!ViceVerse-cz\|)"
KEEP_AFTER = r"(?!\.(?:app|ico|TrayState|TrayCallback|CustomCaption)\b| Custom\b| Name\b| contributors\b)"
DISPLAY = re.compile(NOT_UPSTREAM + r"\bSerein\b" + KEEP_AFTER)
# Lowercase name as a word in packaging paths and commands; never `.serein-extension`,
# `_serein_x` identifiers or SEREIN_* variables.
LOWER_WORD = re.compile(r"(?<![A-Za-z0-9_.])serein(?![A-Za-z0-9])")


def rust_display(text: str) -> str:
    return TOKEN.sub(lambda m: m.group(0) if m.group(0).startswith("'") else DISPLAY.sub(NAME, m.group(0)), text)


def update_source() -> None:
    """Updates, the AppImage's update information and the Website/Report Issue menu items
    follow the GitHub repository that builds the app."""
    up = "apps/desktop/src/updater.rs"
    must(up, 'const RELEASES: &str = "https://api.github.com/repos/ViceVerse-cz/Serein/releases";\n',
         "/// GitHub \"owner/repo\" this build updates from. GitHub Actions builds get it from\n"
         "/// GITHUB_REPOSITORY; set ASTRALCORD_REPO to override. Empty turns update checks off.\n"
         "pub const REPO: &str = match option_env!(\"ASTRALCORD_REPO\") {\n"
         "\tSome(repo) => repo,\n"
         "\tNone => match option_env!(\"GITHUB_REPOSITORY\") {\n"
         "\t\tSome(repo) => repo,\n"
         "\t\tNone => \"\",\n"
         "\t},\n"
         "};\n"
         "/// This fork's GitHub page, for the Website and Report Issue menu items.\n"
         "pub fn project_url(path: &str) -> String {\n"
         "\tlet repo = if REPO.is_empty() { \"" + REPO + "\" } else { REPO };\n"
         "\tformat!(\"https://github.com/{repo}{path}\")\n"
         "}\n", count=1)
    must(up, '\tlet endpoint = if nightly {\n\t\tformat!("{RELEASES}?per_page=100")\n\t} else {\n\t\tformat!("{RELEASES}/latest")\n\t};\n',
         '\tif REPO.is_empty() {\n\t\treturn Err("This build has no update source configured.".into());\n\t}\n'
         '\tlet endpoint = if nightly {\n\t\tformat!("https://api.github.com/repos/{REPO}/releases?per_page=100")\n'
         '\t} else {\n\t\tformat!("https://api.github.com/repos/{REPO}/releases/latest")\n\t};\n', count=1)
    must(up, '"https://github.com/ViceVerse-cz/Serein/releases/download/{}/{name}",',
         '"https://github.com/{REPO}/releases/download/{}/{name}",', count=1)
    must(up, 'format!("serein-{tag}-Linux-X64.AppImage")', 'format!("astralcord-{tag}-Linux-X64.AppImage")', count=1)
    must(up, 'format!("serein-{tag}-{os}-{arch}.zip")', 'format!("astralcord-{tag}-{os}-{arch}.zip")', count=1)

    main_rs = "apps/desktop/src/main.rs"
    must(main_rs, 'egui::OpenUrl::new_tab(\n\t\t\t\t\t\t"https://github.com/ViceVerse-cz/Serein",\n\t\t\t\t\t)',
         'egui::OpenUrl::new_tab(updater::project_url(""))', count=1)
    must(main_rs, 'egui::OpenUrl::new_tab(\n\t\t\t\t\t\t"https://github.com/ViceVerse-cz/Serein/issues/new/choose",\n\t\t\t\t\t)',
         'egui::OpenUrl::new_tab(updater::project_url("/issues/new/choose"))', count=1)

    must("packaging/appimage/build.py",
         '    information = f"gh-releases-zsync|ViceVerse-cz|Serein|{channel}|serein-*-Linux-X64.AppImage.zsync"\n'
         '    url = f"https://github.com/ViceVerse-cz/Serein/releases/download/v{version}/serein-v{version}-Linux-X64.AppImage"\n',
         '    owner, repo = os.environ.get("GITHUB_REPOSITORY", "' + REPO + '").split("/", 1)\n'
         '    information = f"gh-releases-zsync|{owner}|{repo}|{channel}|astralcord-*-Linux-X64.AppImage.zsync"\n'
         '    url = f"https://github.com/{owner}/{repo}/releases/download/v{version}/astralcord-v{version}-Linux-X64.AppImage"\n',
         count=1)


def upstream_housekeeping() -> None:
    """Drop Serein's own CI/release workflows (they need Serein's secrets and include a daily
    release cron) and keep Serein's README under docs/ when a fresh snapshot brings it back."""
    for wf in sorted((ROOT / ".github/workflows").glob("*.yml")):
        if wf.name != "build.yml":
            subprocess.run(["git", "rm", "-q", "-f", "--ignore-unmatch", wf.relative_to(ROOT).as_posix()],
                           cwd=ROOT, check=True)
            wf.unlink(missing_ok=True)
            changed.setdefault("removed upstream workflows", set()).add(wf.name)
    readme = ROOT / "README.md"
    if readme.exists() and "AstralCord" not in "\n".join(readme.read_text(encoding="utf-8").splitlines()[:5]):
        text = readme.read_text(encoding="utf-8")
        for old, new in (("](docs/", "]("), ("](packaging/", "](../packaging/"), ("](LICENSE", "](../LICENSE"),
                         ("](THIRD_PARTY_NOTICES.md", "](../THIRD_PARTY_NOTICES.md")):
            text = text.replace(old, new)
        (ROOT / "docs/serein-README.md").write_text(text, encoding="utf-8")
        subprocess.run(["git", "rm", "-q", "-f", "--ignore-unmatch", "README.md"], cwd=ROOT, check=True)
        readme.unlink(missing_ok=True)
        subprocess.run(["git", "add", "docs/serein-README.md"], cwd=ROOT, check=True)
        changed.setdefault("moved upstream README", set()).add("docs/serein-README.md")


def main() -> None:
    code = [p for p in tracked("apps", "crates", "tools", "tests")
            if p.suffix in {".rs", ".toml", ".cjs", ".py", ".json", ".sh"}
            and "tools/astralcord/" not in p.as_posix()]  # never rewrite these scripts themselves
    linux_pkg = tracked("packaging/linux", "packaging/appimage")
    windows_pkg = [p for p in tracked("packaging/windows") if p.suffix in {".nsi", ".ps1", ".cmd", ".py", ".md", ".rc"}]
    templates = tracked(".github/ISSUE_TEMPLATE")

    upstream_housekeeping()

    # 1. Update source first, while the upstream URLs are still verbatim.
    update_source()

    # 2. App ID (Wayland app_id, desktop file, Windows AUMID, keyring service, single instance).
    apply("app id", code + linux_pkg + windows_pkg, lambda t: t.replace(UPSTREAM_ID, APP_ID))

    # 3. Display name in Rust string literals.
    apply("display name in code", [p for p in code if p.suffix == ".rs"], rust_display)

    # 4. Display name in every translation (message IDs are lowercase, values carry the name;
    #    inflected forms such as "Sereinu" keep their ending).
    apply("translations", tracked("crates/ui/locales"), lambda t: t.replace("Serein", NAME))

    # 5. Packaging scripts and issue templates: name, paths, package names, repository.
    def packaging(t: str) -> str:
        t = t.replace("ViceVerse-cz/Serein", REPO)
        t = re.sub(NOT_UPSTREAM + r"\bSerein\b(?!\.ico\b)", NAME, t)
        return LOWER_WORD.sub(LOWER, t)
    apply("packaging", linux_pkg + windows_pkg + templates, packaging)

    # 6. Files whose names users or the desktop see.
    rename("packaging/linux/serein.desktop", "packaging/linux/astralcord.desktop")
    for icon in sorted((ROOT / "packaging/linux/hicolor").glob("*/apps/serein*")):
        rel = icon.relative_to(ROOT).as_posix()
        rename(rel, rel.replace("/serein", "/astralcord"))

    # 7. Executable: the package stays `serein`, the program it builds is `astralcord`.
    toml = (ROOT / "apps/desktop/Cargo.toml").read_text(encoding="utf-8")
    if "autobins = false" not in toml:
        must("apps/desktop/Cargo.toml", 'name = "serein"\nversion.workspace = true\n',
             'name = "serein"\nversion.workspace = true\nautobins = false\n', count=1)
        toml = (ROOT / "apps/desktop/Cargo.toml").read_text(encoding="utf-8")
    if 'name = "astralcord"' not in toml:
        toml = toml.replace("\n[features]\n",
                            '\n# AstralCord: the package keeps its upstream name, the program is `astralcord`.\n'
                            '[[bin]]\nname = "astralcord"\npath = "src/main.rs"\n\n[features]\n', 1)
        (ROOT / "apps/desktop/Cargo.toml").write_text(toml, encoding="utf-8")
    must("apps/desktop/build.rs", "rustc-link-arg-bin=serein=", "rustc-link-arg-bin=astralcord=", count=2)
    must("tools/xtask/src/main.rs", '"serein.exe"', '"astralcord.exe"')
    must("tools/xtask/src/main.rs", '} else {\n\t\t"serein"\n\t};', '} else {\n\t\t"astralcord"\n\t};', count=1)
    must("tools/xtask/src/main.rs", 'format!("serein-{version}-setup.exe")', 'format!("astralcord-{version}-setup.exe")', count=1)

    # 8. Data folders, tray, own-process detection, Windows install checks, file names.
    must("crates/local-store/src/lib.rs", '"serein-development"', '"astralcord-development"')
    must("crates/local-store/src/lib.rs", '.join("serein")', '.join("astralcord")', count=1)
    must("crates/platform/src/tray/linux.rs", '"serein-symbolic"', '"astralcord-symbolic"')
    must("crates/platform/src/tray/linux.rs", '"serein".into()', '"astralcord".into()', count=1)
    must("crates/discord-voice/src/screen/audio_linux.rs", 'c"serein"', 'c"astralcord"', count=1)
    must("crates/discord-voice/src/screen/audio_linux.rs", '"serein"', '"astralcord"')
    must("crates/platform/src/startup.rs", "serein.exe", "astralcord.exe")
    must("apps/desktop/src/main.rs", "hicolor/256x256/apps/serein.png", "hicolor/256x256/apps/astralcord.png", count=1)
    must("apps/desktop/src/main.rs", '"serein-diagnostics.txt"', '"astralcord-diagnostics.txt"', count=1)
    ui = "apps/desktop/src/updater_install.rs"
    must(ui, '"serein.exe"', '"astralcord.exe"')
    must(ui, '"usr/bin/serein"', '"usr/bin/astralcord"', count=1)
    text = (ROOT / ui).read_text(encoding="utf-8")
    (ROOT / ui).write_text(re.sub(r'("sudo [^"\n]*?) serein"', r'\1 astralcord"', text), encoding="utf-8")

    for rule, files in changed.items():
        print(f"{rule}: {len(files)} file(s)")
    if problems:
        print("\nPROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)


if __name__ == "__main__":
    main()
