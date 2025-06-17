import unittest
from services.icp_scores.company_location_score import score_company_location
from utils.locations import locations

class TestCompanyLocationScore(unittest.TestCase):

    def setUp(self):
        self.icp_with_locations = {
            "locations": {
                "North American Countries": {"United States", "Canada"},
                "U.S. Cities": {"New York City", "San Francisco"},
                "European Countries": {"Germany", "France"},
                "European Cities": {"Berlin", "Paris"},
                "African Countries": {"Kenya", "Nigeria"},
                "African Cities": {"Nairobi", "Lagos"},
            }
        }
        DEFAULT_COMPANY_LOCATIONS = set()
        for location_group in locations.values():
            DEFAULT_COMPANY_LOCATIONS.update(location_group)

        self.fallback_icp = {"company_locations": DEFAULT_COMPANY_LOCATIONS}  # Empty dict triggers default behavior

    def test_north_american_country(self):
        self.assertEqual(score_company_location("Canada", self.icp_with_locations), 25)

    def test_us_city(self):
        self.assertEqual(score_company_location("New York", self.icp_with_locations), 25)

    def test_european_country(self):
        self.assertEqual(score_company_location("France", self.icp_with_locations), 25)

    def test_european_city_fuzzy_match(self):
        self.assertEqual(score_company_location("berln", self.icp_with_locations), 25)  # fuzzy match to Berlin

    def test_african_country(self):
        self.assertEqual(score_company_location("Kenya", self.icp_with_locations), 15)

    def test_african_city_fuzzy_match(self):
        self.assertEqual(score_company_location("nairobi", self.icp_with_locations), 15)

    def test_default_location_match(self):
        # Nairobi exists in default as well
        self.assertEqual(score_company_location("nairobi", self.fallback_icp), 10)

    def test_non_matching_location(self):
        self.assertEqual(score_company_location("Moon Base Alpha", self.icp_with_locations), 5)

    def test_empty_location(self):
        self.assertEqual(score_company_location("", self.icp_with_locations), 0)

    def test_none_icp(self):
        self.assertEqual(score_company_location("New York", None), 0)

if __name__ == "__main__":
    unittest.main()
