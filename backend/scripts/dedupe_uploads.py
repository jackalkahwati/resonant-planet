"""Remove duplicate uploaded datasets by planet identifier."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path


def parse_planet_name(path: Path) -> str:
    stem = path.stem
    if "_nasa_" in stem:
        parts = stem.split("_nasa_")
        return parts[-1].split("_")[0]
    return stem


def dedupe(directory: Path, dry_run: bool = True) -> list[Path]:
    directory = directory.expanduser().resolve()
    if not directory.exists():
        raise FileNotFoundError(directory)

    grouped: dict[str, list[Path]] = defaultdict(list)
    for csv_file in directory.glob("*.csv"):
        key = parse_planet_name(csv_file)
        grouped[key].append(csv_file)

    removed: list[Path] = []
    for key, files in grouped.items():
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        for duplicate in files[1:]:
            removed.append(duplicate)
            if not dry_run:
                duplicate.unlink()

    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, default=Path("uploads"))
    parser.add_argument("--dry-run", action="store_true", help="List duplicates without deleting")
    args = parser.parse_args()

    removed = dedupe(args.directory, dry_run=args.dry_run)
    if removed:
        print("Duplicates marked for removal:")
        for path in removed:
            print(" -", path)
    else:
        print("No duplicates found.")


if __name__ == "__main__":
    main()


