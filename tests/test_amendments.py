import unittest
from app.amendments import ORIGINAL, REVISIONS, compare
from app.demo import MASTER, classify

class AmendmentReview(unittest.TestCase):
    def test_three_amendments(self):
        expected = [("Only the guarantor changed", None), ("Issuer changed", "Vale Trust Co"), ("Hold for research", None)]
        for revision, (status, name) in zip(REVISIONS, expected):
            with self.subTest(revision=revision["version"]):
                actual, _, candidate, lines = compare(ORIGINAL, revision, classify, MASTER)
                self.assertEqual((actual,candidate), (status,name))
                self.assertEqual(lines, [1] if name else [])

    def test_series_mismatch(self):
        result=compare(ORIGINAL,dict(REVISIONS[1],series="OTHER"), classify, MASTER)
        self.assertEqual((result[0],result[2]), ("Hold for research",None))

    def test_issuer_evidence_reworded(self):
        revision=dict(ORIGINAL,lines=["The senior notes are obligations of Alder Funding LLC."])
        self.assertEqual(compare(ORIGINAL,revision,classify, MASTER)[0],"Review revised wording")

    def test_guarantor_line_with_issuer_cross_reference(self):
        revision = dict(REVISIONS[0], lines=[
            ORIGINAL["lines"][0],
            "Guarantor: Vale Trust Co (see revised issuer terms in Annex B)",
        ])
        status, _, candidate, _ = compare(ORIGINAL, revision, classify, MASTER)
        self.assertEqual((status, candidate), ("Hold for research", None))

    def test_unchanged(self):
        self.assertEqual(compare(ORIGINAL,ORIGINAL,classify, MASTER)[0],"Excerpt unchanged")

if __name__=="__main__":
    unittest.main()

