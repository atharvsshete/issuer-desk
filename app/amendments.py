"""Independent synthetic amendments to one confirmed offering excerpt."""
from collections import Counter

ORIGINAL = {"version": "Original", "series": "AF-27", "lines": [
    "Issuer: Alder Funding LLC", "Guarantor: Alder Holdings Inc"]}
REVISIONS = [
    {"version": "A", "series": "AF-27", "lines": ["Issuer: Alder Funding LLC", "Guarantor: Vale Trust Co"]},
    {"version": "B", "series": "AF-27", "lines": ["Issuer: Vale Trust Co", "Guarantor: Alder Holdings Inc"]},
    {"version": "C", "series": "AF-27", "lines": ["Guarantor: Alder Holdings Inc"]},
]

def compare(original, revision, classify, directory):
    if not revision["series"] or original["series"] != revision["series"]:
        return "Hold for research", "Series identifiers do not match.", None, []
    before, _, _ = classify(original["lines"], True)
    after, evidence, why = classify(revision["lines"], True)
    if not after:
        return "Hold for research", why + ". Request the issuer terms for this series.", None, []
    if after != before:
        return "Issuer changed", "Read the new issuer line before recording a fresh decision.", after, evidence
    def non_guarantor(lines):
        return Counter(line for line in lines if not line.startswith("Guarantor: "))
    if non_guarantor(original["lines"]) == non_guarantor(revision["lines"]):
        if Counter(original["lines"]) == Counter(revision["lines"]):
            return "Excerpt unchanged", "No issuer review triggered.", None, []
        old_lines = Counter(original["lines"])
        new_lines = Counter(revision["lines"])
        changed = set(old_lines - new_lines) | set(new_lines - old_lines)
        simple_labels = {"Guarantor: " + name for name in directory}
        if not changed.issubset(simple_labels):
            return "Hold for research", "The guarantor field contains unverified wording. Check the full amendment.", None, []
        return "Only the guarantor changed", "No issuer review triggered. The original confirmation stays with the original.", None, []
    return "Review revised wording", "The candidate is the same. Check the revised evidence.", after, evidence

