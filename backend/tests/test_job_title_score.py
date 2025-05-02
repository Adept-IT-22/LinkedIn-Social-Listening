import unittest
from fuzzywuzzy import fuzz
from services.icp_scores.job_title_score import score_job_title
import services.icp_scores.job_title_score

class TestJobTitleScore(unittest.TestCase):
    def setUp(self):
        self.mock_icp = {
            "job_titles": {
                #Tier 1 (25 pts)
                "Manager", "Head of", "Senior Manager", "Customer Support Manager",
                "Operations Manager", "Contact Center Manager", "Service Delivery Manager",
                "Consultant", "Consultancy", "BPO", "Business Process Outsourcing",

                #Tier 2 (20 pts) => Important but less accessible than managers.
                "Director", "VP", "Vice President", "Senior Director",
                "Managing Director", "Regional Director", "Executive Manager",
                "Country Director", "Director of Operations", "Customer Support Director",
                "VP of Global Services", "Director of IT Services", "Lead",

                #Tier 3 (15 pts) => Low win rate. Often delegate
                "Founder", "CEO", "CTO", "COO", "CFO", "Chief Executive Officer",
                "Chief Operations Officer", "Chief Technology Officer",
                "Chief Financial Officer",

                #Tier 4 (10 pts) => Rarely decision makers.
                "Specialist", "Coordinator"
            }
        }
        self.fallback_icp = {"job_titles": services.icp_scores.job_title_score.DEFAULT_JOB_TITLES}  # triggers DEFAULT_JOB_TITLES

    def test_founder_like_title(self):
        #Test C-Suite titles. Score = 15 points
        self.assertEqual(score_job_title("Chief Technology Officer", self.mock_icp), 15)
        self.assertEqual(score_job_title("Founder", self.mock_icp), 15)

    def test_director_like_title(self):
        #Test director level titles. Score = 20 points
        self.assertEqual(score_job_title("Operations Director", self.mock_icp), 20)
        self.assertEqual(score_job_title("VP of Sales", self.mock_icp), 20)

    def test_manager_title(self):
        #Test manager level titles. Score = 25 points
        self.assertEqual(score_job_title("Marketing Manager", self.mock_icp), 25)
        self.assertEqual(score_job_title("Head of Customer Support", self.mock_icp), 25)

    def test_specialist_title(self):
        #Test specialist/coordinator level titles
        self.assertEqual(score_job_title("Customer Service Specialist", self.mock_icp), 10)

    def test_default_icp_score(self):
        #Test fallback to DEFAULT_JOB_TITLES
        self.assertEqual(score_job_title("Service Delivery Manager", self.fallback_icp),25)
        self.assertEqual(score_job_title("Director of IT", self.fallback_icp),20)

    def test_no_matching_title(self):
        #Test non-decision makers. Score = 0
        self.assertEqual(score_job_title("Intern", self.mock_icp), 0)
        self.assertEqual(score_job_title("Receptionist", self.mock_icp), 0)

    def test_low_fuzzy_score(self):
        #Test low fuzzy scores. SCore = 0
        self.assertEqual(score_job_title("Totally Random Title", self.mock_icp), 0)

    def test_edge_cases(self):
        #Test empty/none inputs
        self.assertEqual(score_job_title("", self.mock_icp), 0)
        self.assertEqual(score_job_title(None, self.mock_icp), 0)
        self.assertEqual(score_job_title("CEO", None), 0)

    def test_fuzzy_matching_variations(self):
        #Test title variations still match
        self.assertEqual(score_job_title("Sr. Manager of Ops", self.mock_icp), 25)
        self.assertEqual(score_job_title("Vice Pres. of Sales", self.mock_icp), 20)
        self.assertEqual(score_job_title("Chief Tech Officer", self.mock_icp), 15)

if __name__ == '__main__':
    unittest.main()
