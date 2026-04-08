#!/usr/bin/env python3
"""
Prepare mailing CSV for Brevo from tennis_players_male.csv.

Reads the raw CSV, deduplicates by email, groups categories,
and outputs a Brevo-compatible CSV ready for import.

Usage:
    python scripts/prepare_mailing.py
    python scripts/prepare_mailing.py --input /path/to/csv --output /path/to/output.csv
"""

import csv
import argparse
from collections import defaultdict
from pathlib import Path

# Default paths
DEFAULT_INPUT = Path.home() / "CURSOR-RAG" / "output" / "tennis_players_male.csv"
DEFAULT_OUTPUT = Path(__file__).parent.parent / "mailing_brevo_import.csv"


def normalize_email(email: str) -> str:
    """Normalize email: strip, lowercase."""
    return email.strip().lower() if email else ""


def load_players(input_path: Path) -> list[dict]:
    """Load players from CSV."""
    players = []
    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            players.append(row)
    print(f"Loaded {len(players)} rows from {input_path}")
    return players


def deduplicate_by_email(players: list[dict]) -> list[dict]:
    """
    Deduplicate players by email address.
    Merge categories and tournaments for the same email.
    Keep the most recent data for name/club.
    """
    by_email = defaultdict(lambda: {
        "vorname": "",
        "nachname": "",
        "email": "",
        "telefon": "",
        "verein": "",
        "kategorien": set(),
        "turniere": set(),
        "count": 0,
    })

    for p in players:
        email = normalize_email(p.get("email", ""))
        if not email or "@" not in email:
            continue

        entry = by_email[email]
        entry["email"] = email
        entry["vorname"] = p.get("vorname", "") or entry["vorname"]
        entry["nachname"] = p.get("nachname", "") or entry["nachname"]
        entry["telefon"] = p.get("telefon", "") or entry["telefon"]
        entry["verein"] = p.get("verein", "") or entry["verein"]
        if p.get("kategorie"):
            entry["kategorien"].add(p["kategorie"])
        if p.get("turnier"):
            entry["turniere"].add(p["turnier"])
        entry["count"] += 1

    # Convert to list
    result = []
    for email, data in sorted(by_email.items()):
        result.append({
            "EMAIL": data["email"],
            "VORNAME": data["vorname"],
            "NACHNAME": data["nachname"],
            "TELEFON": data["telefon"],
            "VEREIN": clean_verein(data["verein"]),
            "KATEGORIEN": ", ".join(sorted(data["kategorien"])),
            "ANZAHL_TURNIERE": str(data["count"]),
        })

    return result


def clean_verein(verein: str) -> str:
    """Remove club number suffix like (4040) from club name."""
    import re
    return re.sub(r"\s*\(\d+\)\s*$", "", verein).strip()


def write_brevo_csv(contacts: list[dict], output_path: Path):
    """Write Brevo-compatible CSV."""
    if not contacts:
        print("No contacts to write!")
        return

    fieldnames = ["EMAIL", "VORNAME", "NACHNAME", "TELEFON", "VEREIN", "KATEGORIEN", "ANZAHL_TURNIERE"]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(contacts)

    print(f"Wrote {len(contacts)} contacts to {output_path}")


def print_stats(contacts: list[dict]):
    """Print mailing list statistics."""
    print("\n--- MAILING LIST STATS ---")
    print(f"Total unique emails: {len(contacts)}")

    # Category distribution
    cats = defaultdict(int)
    for c in contacts:
        for cat in c["KATEGORIEN"].split(", "):
            if cat:
                cats[cat] += 1
    print("\nBy category:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

    # Top clubs
    clubs = defaultdict(int)
    for c in contacts:
        if c["VEREIN"]:
            clubs[c["VEREIN"]] += 1
    print(f"\nUnique clubs: {len(clubs)}")
    print("Top 10 clubs:")
    for club, count in sorted(clubs.items(), key=lambda x: -x[1])[:10]:
        print(f"  {club}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Prepare mailing CSV for Brevo")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Input CSV path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV path")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}")
        return

    players = load_players(args.input)
    contacts = deduplicate_by_email(players)
    print_stats(contacts)
    write_brevo_csv(contacts, args.output)
    print(f"\nDone! Import {args.output} into Brevo.")


if __name__ == "__main__":
    main()
