"""Keep the standalone skill and the installable Codex package in sync."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    plugin = root / "plugins" / "figma-to-roblox-ui"
    files = {
        root / "SKILL.md": plugin / "skills" / "figma-to-roblox-ui" / "SKILL.md",
        root / "LICENSE": plugin / "LICENSE",
    }
    stale = []
    for source, destination in files.items():
        content = source.read_bytes()
        if args.check:
            if not destination.is_file() or destination.read_bytes() != content:
                stale.append(str(destination.relative_to(root)))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
    if stale:
        parser.exit(1, "Out of sync: " + ", ".join(stale) + "\nRun python scripts/sync_codex_skill.py\n")
    print("Codex package is in sync." if args.check else "Codex package refreshed.")


if __name__ == "__main__":
    main()
