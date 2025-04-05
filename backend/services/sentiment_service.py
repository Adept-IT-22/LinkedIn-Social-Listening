import logging
from config import logging_config
from transformers import pipeline, AutoTokenizer

def sentiment_analysis(text, keywords):
    #perform sentiment analysis of each post
    model = "siebert/sentiment-roberta-large-english"
    sentiment_analyzer = pipeline(task="sentiment-analysis", model=model)

    try:
        #tokenize the text
        tokenizer = AutoTokenizer.from_pretrained(model)
        tokens = tokenizer(
            text,
            truncation = True,
            max_length = 4096,
        )
        truncated_text = tokenizer.decode(tokens["input_ids"])

        #analyze the text
        analysis = sentiment_analyzer(truncated_text)[0] #analyze the 1st 4096 tokens

        #return the results
        return {
            "text": text,
            "sentiment" : analysis["label"],
            "score" : analysis["score"],
            "words_found" : (keyword in text.lower() for keyword in keywords),
            "truncated": len(tokens["input_ids"]) >= 4096
        }

    except Exception as e:
        logging.error("Analysis failed for text (first 50 characters): %s | Error %s", text[:50], str(e))
        return None
    