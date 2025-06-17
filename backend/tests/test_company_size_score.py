import unittest
from services.icp_scores.company_size_score import score_company_size

class TestCompanySizeScore(unittest.TestCase):

    def test_small_business(self):
        icp = {"employees": {"max": 50}}
        self.assertEqual(score_company_size(icp), 15)

    def test_large_enterprise(self):
        icp = {"employees": {"min": 251}}
        self.assertEqual(score_company_size(icp), 20)

    def test_mid_size_range(self):
        icp = {"employees": {"range": (51, 250)}}
        self.assertEqual(score_company_size(icp), 25)

    def test_empty_icp(self):
        self.assertEqual(score_company_size({}), 20)

    def test_missing_employees_key(self):
        icp = {"industries": ["Finance"]}
        self.assertEqual(score_company_size(icp), 20)

    def test_malformed_range(self):
        icp = {"employees": {"range": (1000,)}}  # Invalid range
        self.assertEqual(score_company_size(icp), 20)

    def test_unknown(self):
        icp = {"employees": {"min": 10000}}
        self.assertEqual(score_company_size(icp), 20)

if __name__ == "__main__":
    unittest.main()
