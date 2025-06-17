#This module tests the sentiment analysis

import unittest
from unittest.mock import patch, MagicMock
from services.sentiment_service import sentiment_analysis

class TestSentimentAnalysis(unittest.TestCase):

    @patch("services.sentiment_service.pipeline")
    @patch("services.sentiment_service.AutoTokenizer")
    def test_sentiment_analysis_success(self, mock_tokenizer_class, mock_pipeline):
        # Mock tokenizer
        mock_tokenizer = MagicMock()
        mock_tokenizer.return_value = {
            "input_ids": [101, 2009, 2001, 2204, 102],
            "length": [5],
            "attention_mask": [1, 1, 1, 1, 1]
        }

        #Add comparison support for model_max_length
        mock_tokenizer.model_max_length = 512
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        # Mock sentiment analysis model
        mock_sentiment = MagicMock()
        mock_sentiment.return_value = [{"label": "POSITIVE", "score": 0.98}]
        mock_pipeline.return_value = mock_sentiment

        text = "This service was amazing!"
        keywords = ["amazing", "bad", "support"]

        result = sentiment_analysis(text, keywords)

        self.assertIsNotNone(result)
        self.assertEqual(result["sentiment"], "POSITIVE")
        self.assertAlmostEqual(result["score"], 0.98)
        self.assertTrue(any(result["words_found"]))
        self.assertFalse(result["truncated"])

    @patch("services.sentiment_service.pipeline")
    @patch("services.sentiment_service.AutoTokenizer")
    def test_sentiment_analysis_failure(self, mock_tokenizer_class, mock_pipeline):
        # Mock tokenizer to raise exception
        mock_tokenizer = MagicMock()
        mock_tokenizer.side_effect = Exception("Tokenizer error")
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        result = sentiment_analysis("Some text", ["word"])
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()


