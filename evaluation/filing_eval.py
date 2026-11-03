"""Replay scoring of issuer rows retrieved by a full-filing literal search."""
import csv
import json
import re
from pathlib import Path

from app.demo import classify
from evaluation.public_eval import DIRECTORY

ROOT = Path(__file__).resolve().parents[1]

def score(row, directory=DIRECTORY):
    exact = classify([row], False, directory)[0]
    # Experimental normalization: remove a trailing, fully quoted alias clause.
    normalized = re.sub(r'\s+\(“[^”]+”(?: or “[^”]+”)?\)$', '', row)
    alias = classify([normalized], False, directory)[0]
    return exact, alias

def main():
    records = json.loads((ROOT/"data"/"filing-search.json").read_text(encoding="utf8"))
    with (ROOT/"results"/"filing-results.csv").open("w",newline="",encoding="utf8") as f:
        writer=csv.writer(f)
        writer.writerow(["filing","expected","row_found","exact","alias_experiment"])
        for r in records:
            exact,alias=score(r["row"])
            writer.writerow([r["id"],r["expected"],bool(r["row"]),exact or "HOLD",alias or "HOLD"])

if __name__=="__main__":
    main()

