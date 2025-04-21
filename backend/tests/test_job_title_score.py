import unittest
from services.icp_scores.job_title_score import score_job_title
import services.icp_scores.job_title_score
class TestJobTitleScore(unittest.TestCase):

    def setUp(self):
        self.mock_icp = {
            "job_titles": {
                "CEO", "Chief Technology Officer", "Director of Operations", 
                "Marketing Manager", "Customer Service Specialist"
            }
        }
        self.fallback_icp = {"job_titles": services.icp_scores.job_title_score.DEFAULT_JOB_TITLES}  # triggers DEFAULT_JOB_TITLES

    def test_founder_like_title(self):
        self.assertEqual(score_job_title("Chief Technology Officer", self.mock_icp), 25)

    def test_director_like_title(self):
        self.assertEqual(score_job_title("Operations Director", self.mock_icp), 25)

    def test_manager_title(self):
        self.assertEqual(score_job_title("Marketing Manager", self.mock_icp), 15)

    def test_specialist_title(self):
        self.assertEqual(score_job_title("Customer Service Specialist", self.mock_icp), 15)

    def test_default_icp_score(self):
        self.assertEqual(score_job_title("Team Lead", self.fallback_icp),15)

    def test_no_matching_title(self):
        self.assertEqual(score_job_title("Intern", self.mock_icp), 0)

    def test_low_fuzzy_score(self):
        self.assertEqual(score_job_title("Totally Random Title", self.mock_icp), 0)

    def test_empty_job_title(self):
        self.assertEqual(score_job_title("", self.mock_icp), 0)

    def test_none_job_title(self):
        self.assertEqual(score_job_title(None, self.mock_icp), 0)

    def test_none_icp(self):
        self.assertEqual(score_job_title("CEO", None), 0)


if __name__ == '__main__':
    unittest.main()
