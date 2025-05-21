import logging
from backend.config import logging_config
from transformers import pipeline, AutoTokenizer

#initialize module logger
logger = logging.getLogger(__name__)

def sentiment_analysis(text, keywords):
    #set up pipeline with model and tokenizer
    model = "siebert/sentiment-roberta-large-english"
    tokenizer = AutoTokenizer.from_pretrained(model)
    sentiment_analyzer = pipeline(task="sentiment-analysis", model=model, tokenizer=tokenizer)

    try:
        #split text into tokens
        tokens = tokenizer(
            text,
            truncation = True,
            return_length = True
        )
        
        #check if text was too long and got cut
        truncated = tokens["length"][0] > tokenizer.model_max_length

        #analyze the text
        analysis = sentiment_analyzer(text)[0] #analyze the 1st 4096 tokens

        #return the results
        return {
            "text": text,
            "sentiment" : analysis["label"],
            "score" : analysis["score"],
            "words_found" : (keyword in text.lower() for keyword in keywords),
            "truncated": truncated 
        }

    except Exception as e:
        logging.error("Analysis failed for text (first 50 characters): %s | Error %s", text[:50], str(e))
        return None
    