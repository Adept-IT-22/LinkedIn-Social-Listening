import unittest
from services.icp_scores.find_icp import find_icp, fallback_icp
from utils.icp import icps

class TestFindIcp(unittest.TestCase):

    def test_small_business(self):
        result = find_icp("1 to 50")
        self.assertIn("employees", result)
        self.assertEqual(icps["Small Businesses"]["employees"], result["employees"])

    def test_mid_size_company(self):
        result = find_icp("120 to 150")
        self.assertIn("employees", result)
        self.assertEqual(icps["Mid-Size Companies"]["employees"], result["employees"])

    def test_large_enterprise(self):
        result = find_icp("5000")
        self.assertIn("employees", result)
        self.assertEqual(icps["Large Enterprises"]["employees"], result["employees"])

    def test_to_unknown(self):
        result = find_icp("10001 to unknown")
        self.assertIn("employees", result)
        self.assertEqual(icps["Large Enterprises"]["employees"], result["employees"])

    def test_missing_employee_count(self):
        result = find_icp("Employee Count Not Found")
        self.assertIn("Unclassified", result)
        self.assertEqual(result["Unclassified"], fallback_icp)

    def test_non_matching_range(self):
        result = find_icp("5 - 10")
        # This might match Small Businesses depending on your logic
        self.assertIn("employees", result)

    def test_malformed_string(self):
        result = find_icp("abcde")
        self.assertIn("Unclassified", result)
        self.assertEqual(result["Unclassified"], fallback_icp)

    def test_empty_string(self):
        result = find_icp("")
        self.assertIn("Unclassified", result)
        self.assertEqual(result["Unclassified"], fallback_icp)

if __name__ == "__main__":
    unittest.main()
