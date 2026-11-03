"""Replay the frozen label rules on new issuers, then probe the first-row assumption."""
import csv
import json
from filing_eval import ROOT, DIRECTORY, score

directory = (*DIRECTORY, "Morgan Stanley Finance LLC", "Morgan Stanley",
             "HSBC USA Inc.", "Citigroup Global Markets Holdings Inc.", "Citigroup Inc.",
             "Royal Bank of Canada")
records = json.loads((ROOT/"new-issuers.json").read_text(encoding="utf8"))
with (ROOT/"new-issuer-results.csv").open("w",newline="",encoding="utf8") as f:
    w=csv.writer(f)
    w.writerow(["id","expected","exact","alias_rule"])
    for case in records:
        exact,alias=score(case["row"], directory)
        w.writerow([case["id"],case["expected"],exact or "HOLD",alias or "HOLD"])

# Each list represents issuer rows returned in reading order for a synthetic filing.
# The requested series is B. Only the first issuer row reaches the existing scorer.
a,b = "Royal Bank of Canada","HSBC USA Inc."
with (ROOT/"series-stress-results.csv").open("w",newline="",encoding="utf8") as f:
    w=csv.writer(f)
    w.writerow(["order","series_A_issuer","series_B_expected","first_row_result","correct"])
    for first in ["A","B"]:
        for issuer_a,issuer_b in [(a,b),(b,a),(a,a),(b,b)]:
            first_name=issuer_a if first=="A" else issuer_b
            _,pick=score("Issuer: "+first_name,directory)
            w.writerow([first,issuer_a,issuer_b,pick,pick==issuer_b])


