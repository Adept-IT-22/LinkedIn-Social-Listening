import unittest
from services.icp_scores.company_industry_score import score_company_industry, find_industry
from utils.industries import industries

class TestCompanyIndustryScore(unittest.TestCase):

    def setUp(self):
        # Sample ICP details with allowed industries
        self.icp_details = {
            "industries": {
                "Default": set().union(*industries.values())
            }
        }

    def test_exact_match_score_25(self):
        self.assertEqual(score_company_industry("Outsourcing/Offshoring", self.icp_details), 25)

    def test_exact_match_score_20(self):
        self.assertEqual(score_company_industry("Healthcare", self.icp_details), 25)

    def test_exact_match_score_15(self):
        self.assertEqual(score_company_industry("Education", self.icp_details), 5)

    def test_exact_match_score_10(self):
        self.assertEqual(score_company_industry("Design", self.icp_details), 0)

    def test_exact_match_score_5(self):
        self.assertEqual(score_company_industry("Arts", self.icp_details), 5)

    def test_fuzzy_match(self):
        # This should match "Retail" closely
        self.assertEqual(score_company_industry("Retailing", self.icp_details), 15)

    def test_non_matching_industry(self):
        self.assertEqual(score_company_industry("Rocket Science", self.icp_details), 0)

    def test_empty_string(self):
        self.assertEqual(score_company_industry("", self.icp_details), 0)

    def test_none_icp(self):
        self.assertEqual(score_company_industry("Retail", None), 0)

    def test_none_industry(self):
        self.assertEqual(score_company_industry(None, self.icp_details), 0)

    def test_find_industry_exact(self):
        self.assertEqual(find_industry("Higher Education"), "Education")

    def test_find_industry_fuzzy(self):
        self.assertEqual(find_industry("Hospital & Health Care"), "Healthcare")

    def test_find_industry_low_score(self):
        self.assertIsNone(find_industry("XyzIndustry"))

    def test_find_industry_blank(self):
        self.assertIsNone(find_industry("  "))


if __name__ == "__main__":
    unittest.main()
