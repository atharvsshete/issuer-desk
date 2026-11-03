"""Score the fixed SEC excerpts; no network or training during evaluation."""
import csv
import json
import re
from pathlib import Path
from demo import classify

ROOT = Path(__file__).resolve().parent
DIRECTORY = ("Barclays Bank PLC", "Barclays Capital Inc.", "BofA Finance LLC",
             "Bank of America Corporation", "Nomura America Finance, LLC",
             "The Goldman Sachs Group, Inc.")

def phrases(line, baseline):
    if baseline or line.startswith("Issuer:"):
        return baseline
    names = [name for name in DIRECTORY if name in line]
    if len(names) != 1 or re.search(r"\b(not|joint|co-issuer)\b", line, re.I):
        return None
    name = names[0]
    pattern = r"\b(?:issued by|obligations of)\s+" + re.escape(name) + r"(?=$|[\s.,(])"
    return name if re.search(pattern, line, re.I) else None

def main():
    cases = json.loads((ROOT/"public-excerpts.json").read_text(encoding="utf8"))
    with (ROOT/"public-results.csv").open("w",newline="",encoding="utf8") as f:
        writer=csv.writer(f)
        methods=["exact","phrase","model_assisted"]
        writer.writerow(["case","expected",*methods])
        counts={m:[0,0,0] for m in methods}
        for case in cases:
            line=case["excerpt"]
            exact=classify([line],False,DIRECTORY)[0]
            predictions=[exact,phrases(line,exact),classify([line],True,DIRECTORY)[0]]
            writer.writerow([case["id"],case["expected"],*[p or "HOLD" for p in predictions]])
            for m,p in zip(methods,predictions):
                bucket=2 if p is None else int(p!=case["expected"])
                counts[m][bucket]+=1
        for m,(correct,wrong,held) in counts.items():
            print(f"{m}: {correct} correct issuer suggestions, {wrong} wrong, {held} held")
if __name__=="__main__":
    main()

