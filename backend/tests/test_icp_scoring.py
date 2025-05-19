import unittest
from unittest.mock import patch, MagicMock
from services.icp_scoring import icp_scoring

class TestICPScoring(unittest.TestCase):

    @patch("services.icp_scoring.get_authors")
    @patch("services.icp_scoring.icp_scorer")
    def test_icp_scoring_qualified_author(self, mock_scorer_class, mock_get_authors):
        # Arrange
        mock_get_authors.return_value = [
            "Jane Doe - Chief Operating Officer - Acme Corp - Nairobi - Software - 201 to 500"
        ]

        # Setup the scorer instance and its return values
        mock_scorer = MagicMock()
        mock_scorer.get_icp.return_value = (
            "Mid-Size Companies", 
            {
                "job_titles": {"chief operating officer"},
                "industries": {"Software"},
                "locations": {"African Cities": {"nairobi"}},
                "employees": {"range": (201, 500)}
            }
        )
        mock_scorer.total_score.return_value = 85

        # Replace the class with the mock instance
        mock_scorer_class.return_value = mock_scorer

        # Act
        results = list(icp_scoring(min_score=60))

        # Assert
        self.assertEqual(len(results), 1)
        self.assertIn("author", results[0])
        self.assertIn("icp", results[0])
        self.assertIn("score", results[0])
        self.assertEqual(results[0]["author"]["name"], "Jane Doe")
        self.assertGreaterEqual(results[0]["score"], 50)

    @patch("services.icp_scoring.get_authors")
    @patch("services.icp_scoring.icp_scorer")
    def test_icp_scoring_below_threshold(self, mock_scorer_class, mock_get_authors):
        # Arrange
        mock_get_authors.return_value = [
            "John Doe - Coordinator - Foo Inc - Cape Town - Nonprofit - 1 to 10"
        ]

        mock_scorer = MagicMock()
        mock_scorer.get_icp.return_value = (
            "Small Businesses",
            {
                "job_titles": {"coordinator"},
                "industries": {"Nonprofit"},
                "locations": {"African Cities": {"cape town"}},
                "employees": {"max": 50}
            }
        )
        mock_scorer.total_score.return_value = 20

        mock_scorer_class.return_value = mock_scorer

        # Act
        results = list(icp_scoring(min_score=60))

        # Assert
        self.assertEqual(results, [])

if __name__ == "__main__":
    unittest.main()
