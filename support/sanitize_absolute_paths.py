#!/usr/bin/env python3
import os
import re
import sys
import tempfile
import zipfile
from collections import Counter
from pathlib import Path

ATLAS_DIR_NAME = "world-history-atlas"


def get_documents_dir() -> Path:
    """Resolve the user's Documents folder the way KDE (and other XDG desktops) do."""
    home = Path.home()

    # 1. Explicit environment override (rarely set, but cheap to honor)
    env = os.environ.get("XDG_DOCUMENTS_DIR")
    if env:
        return Path(env).expanduser()

    # 2. ~/.config/user-dirs.dirs, which KDE reads and writes
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", home / ".config"))
    user_dirs = config_home / "user-dirs.dirs"
    if user_dirs.is_file():
        for line in user_dirs.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"""\s*XDG_DOCUMENTS_DIR=(["']?)(.*?)\1\s*$""", line)
            if m:
                return Path(m.group(2).replace("$HOME", str(home)))

    # 3. Default
    return home / "Documents"


def build_prefix_regex(atlas_dir: Path) -> re.Pattern:
    """Match the atlas dir with or without the /var prefix (Fedora Atomic/Kinoite
    symlinks /home -> /var/home), plus the symlink-resolved variant, and capture
    the rest of the path up to the next delimiter so it can be reported."""
    variants = set()
    for p in (str(atlas_dir), os.path.realpath(atlas_dir)):
        if p.startswith("/var/home/"):
            p = p[len("/var"):]
        variants.add(p)
    alternatives = "|".join(re.escape(v) for v in sorted(variants, key=len, reverse=True))
    # The /var prefix must be part of the match, otherwise "/var" would be left
    # behind in front of "..".
    return re.compile(rf"(?:/var)?(?:{alternatives})([^\"'<>|\n]*)")


if len(sys.argv) != 2:
    sys.exit(f"Usage: {sys.argv[0]} project.qgz")

path = sys.argv[1]

documents_dir = get_documents_dir()
atlas_dir = documents_dir / ATLAS_DIR_NAME
ABS_PREFIX = build_prefix_regex(atlas_dir)

print(f"Documents folder: {documents_dir}")
print(f"Atlas folder:     {atlas_dir}" + ("" if atlas_dir.is_dir() else "  (warning: does not exist)"))

sanitized = Counter()
gps_removed = 0


def record_path(m: re.Match) -> str:
    sanitized[m.group(0)] += 1
    return ".." + m.group(1)


fd, tmp = tempfile.mkstemp(suffix=".qgz", dir=os.path.dirname(os.path.abspath(path)))
os.close(fd)

try:
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.endswith(".qgs"):
                xml = data.decode("utf-8")
                xml, n1 = re.subn(r"\s*<ProjectGpsSettings\b[^>]*/>", "", xml)
                xml, n2 = re.subn(
                    r"\s*<ProjectGpsSettings\b.*?</ProjectGpsSettings>", "", xml, flags=re.S
                )
                gps_removed += n1 + n2
                xml = ABS_PREFIX.sub(record_path, xml)
                data = xml.encode("utf-8")
            zout.writestr(item, data)
    os.replace(tmp, path)
except Exception:
    os.unlink(tmp)
    raise

# --- Report ---
if gps_removed:
    print(f"\n✔ Project GPS settings sanitized ({gps_removed} <ProjectGpsSettings> element(s) removed).")
else:
    print("\n– No <ProjectGpsSettings> found; nothing to sanitize.")

if sanitized:
    total = sum(sanitized.values())
    print(f"\n✔ Sanitized {total} absolute path occurrence(s) ({len(sanitized)} unique):")
    for old, count in sorted(sanitized.items()):
        new = ABS_PREFIX.sub(lambda m: ".." + m.group(1), old)
        suffix = f"  (x{count})" if count > 1 else ""
        print(f"  {old}  ->  {new}{suffix}")
else:
    print("\n– No absolute paths matched; nothing to sanitize.")