from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List, Mapping


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_projects_csv(records: List[Mapping[str, str]], destination: Path) -> None:
    ensure_parent(destination)
    fieldnames = [
        "urlOfProject",
        "nameOfProject",
        "descriptionOfProject",
        "problemSolved",
        "challengesFaced",
        "technologiesUsed",
    ]
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field, "") for field in fieldnames})


def write_embeddings_placeholder(records: Iterable[Mapping[str, str]], destination: Path) -> None:
    """Persist a placeholder embeddings file to satisfy pipeline outputs."""
    ensure_parent(destination)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["project_url", "field", "embedding"])
        for record in records:
            writer.writerow([record.get("urlOfProject", ""), "pending", ""])


def write_failures(urls: Iterable[str], destination: Path) -> None:
    if not urls:
        return
    ensure_parent(destination)
    with destination.open("w", encoding="utf-8") as handle:
        for url in urls:
            handle.write(f"{url}\n")

