"""Build the offline demo and report observed outcomes against authored labels."""
import csv
import json
import re
from pathlib import Path
from model import predicts_issuer
from amendments import ORIGINAL, REVISIONS, compare

ROOT = Path(__file__).resolve().parent
A, B, T = "Alder Funding LLC", "Alder Holdings Inc", "Vale Trust Co"
MASTER = {A:"E01", B:"E02", T:"E03"}
# Fixture ID, source lines for one synthetic note, expected issuer (None means unresolved).
CASES = [
 ("01",[f"Issuer: {A}",f"Guarantor: {B}"],A),
 ("02",[f"Issuer: {B}",f"Trustee: {T}"],B),
 ("03",[f"The new notes are issued by {A}.",f"{B} will guarantee the notes."],A),
 ("04",[f"{B} will issue these notes.",f"{T} acts as trustee."],B),
 ("05",[f"The senior notes are obligations of {A}."],A),
 ("06",[f"Guarantor: {B}"],None),
 ("07",[f"Issuer: {A}",f"Issuer: {B}"],None),
 ("08",["Issuer: Alder"],None),
 ("09",[f"These notes are not issued by {A}."],None),
 ("10",[f"{A} and {B} will issue the notes."],None),
 ("11",["Issuer: Birch Capital Ltd"],None),
 ("12",[f"{A} brought this debenture to market."],A),
 ("13",[f"The notes issued by other companies are distributed by {A}."],None),
]

def classify(lines, assisted, directory=MASTER):
    found = []
    for n, line in enumerate(lines,1):
        names = [name for name in directory if name in line]
        if any(re.search(p,line,re.I) for p in [r"\bnot\b",r"\bjoint",r"\bco-issuer"]):
            return None, [], "Complex or negative wording"
        if len(names)>1:
            return None, [], "Multiple entities on one line"
        if line.startswith("Issuer:"):
            name=line.partition(":")[2].strip()
            if name not in directory:
                return None, [], "No exact directory entry"
            found.append((name,n))
        elif assisted and names and predicts_issuer(line.replace(names[0],"entity")):
            found.append((names[0],n))
    if len({name for name,_ in found})!=1:
        return None, [], "Conflicting candidates" if found else "No supported candidate"
    return found[0][0], [n for _,n in found], "Review candidate"

def main():
    payload=[]
    with (ROOT/"results.csv").open("w",newline="",encoding="utf8") as f:
        w=csv.writer(f);w.writerow(["case","expected","baseline","local_model_assisted"])
        for case,lines,truth in CASES:
            routes=[classify(lines,assisted) for assisted in [False,True]]
            w.writerow([case,truth or "hold",*[r[0] or "hold" for r in routes]])
            payload.append(dict(case=case,lines=lines,routes=routes))
    revisions = [dict(v, decision=compare(ORIGINAL, v, classify, MASTER)) for v in REVISIONS]
    data=json.dumps(dict(cases=payload,entities=MASTER,original=ORIGINAL,revisions=revisions)).replace("<","\\u003c")
    (ROOT/"review.html").write_text((ROOT/"template.html").read_text(encoding="utf8").replace("/*DATA*/",data),encoding="utf8")
    for assisted in [False,True]:
        picks=[(classify(lines,assisted)[0],truth) for _,lines,truth in CASES]
        print("assisted",assisted,"correct candidates",sum(p==t and p is not None for p,t in picks),"wrong candidates",sum(p is not None and p!=t for p,t in picks),"holds",sum(p is None for p,t in picks))
if __name__=="__main__":
    main()

