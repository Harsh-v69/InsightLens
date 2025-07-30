from newspaper import Article
from langdetect import detect
from googletrans import Translator
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

# Load model and tokenizer globally (load once, fast)
tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
labels = ['Negative', 'Neutral', 'Positive']

def extract_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return {
            "title": article.title,
            "text": article.text,
            "language": detect(article.text)
        }
    except Exception as e:
        return {"error": f"Failed to extract article: {str(e)}"}

def translate_to_english(text, src_lang):
    if not text or not isinstance(text, str):
        return "Translation error: No valid text to translate."

    if src_lang == "en":
        return text

    try:
        translator = Translator()
        translated = translator.translate(text, src=src_lang, dest='en')
        return translated.text
    except Exception as e:
        return f"Translation error: {str(e)}"


def analyze_bias(text):
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
            scores = torch.nn.functional.softmax(outputs.logits, dim=1).squeeze().numpy()

        label = labels[np.argmax(scores)]
        polarity = scores[2] - scores[0]  # Positive - Negative
        subjectivity = 1.0 - scores[1]    # 1 - Neutral score

        # Bias label based on polarity thresholds
        if subjectivity < 0.4:
            bias = "Neutral"
        elif polarity < -0.3:
            bias = "Left-Leaning"
        elif polarity > 0.3:
            bias = "Right-Leaning"
        else:
            bias = "Moderate / Center"

        return {
                "label": label,
                "polarity": float(round(polarity, 2)),
                "subjectivity": float(round(subjectivity, 2)),
                "bias": bias
               }


    except Exception as e:
        return {"error": f"Bias analysis failed: {str(e)}"}

import re

def sentence_tone_breakdown(text):
    try:
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 5]
        results = []

        # Define party keywords
        parties = {
                "Bharatiya Janata Party": ["BJP", "Modi", "Hindutva","Bharatiya Janata Party"],
                "Indian National Congress": ["Congress", "Rahul Gandhi", "UPA","Indian National Congress"],
                "Aam Aadmi Party": ["AAP", "Arvind Kejriwal", "Anti-corruption","Aam Aadmi Party"],
                "All India Trinamool Congress": ["TMC", "Mamata Banerjee", "Mamata Didi","All India Trinamool Congress"],
                "Dravida Munnetra Kazhagam": ["DMK", "M.K. Stalin", "Dravidian politics"],
                "Bahujan Samaj Party": ["BSP", "Mayawati", "Dalit"],
                "All India Anna Dravida Munnetra Kazhagam": ["AIADMK", "Jayalalithaa", "Amma"],
                "Samajwadi Party": ["SP", "Akhilesh Yadav", "Samajwadi Party"],
                "Rashtriya Janata Dal": ["RJD", "Lalu Prasad","Rashtriya Janata Dal"],
                "Nationalist Congress Party": ["NCP", "Sharad Pawar","Nationalist Congress Party"],
                "Janata Dal (United)": ["JD(U)", "Nitish Kumar", "Coalition politics","Janata Dal (United)"],
                "Communist Party of India (Marxist)": ["CPI(M)", "Left-wing", "Communism","Communist Party of India"],
                "Telugu Desam Party": ["TDP", "Chandrababu Naidu", "Telugu pride"],
                "Shiv Sena": ["Shiv Sena", "Thackeray", "Marathi pride"],
                "National People's Party": ["NPP", "Conrad Sangma", "Regionalism","National People's Party"]
            }

        for sentence in sentences:
            # Transformer-based classification
            inputs = tokenizer(sentence, return_tensors="pt", truncation=True)
            with torch.no_grad():
                outputs = model(**inputs)
                scores = torch.nn.functional.softmax(outputs.logits, dim=1).squeeze().numpy()

            label = labels[np.argmax(scores)]
            polarity = scores[2] - scores[0]  # positive - negative
            subjectivity = 1.0 - scores[1]    # inverse of neutral

            # Party mention detection
            mentions = []
            for party, keywords in parties.items():
                if any(re.search(rf"\b{kw}\b", sentence, re.IGNORECASE) for kw in keywords):
                    mentions.append(party)

            results.append({
                "sentence": sentence,
                "polarity": float(round(polarity, 2)),
                "subjectivity": float(round(subjectivity, 2)),
                "label": label,
                "mentions": mentions
            })

        return results

    except Exception as e:
        return [{"error": str(e)}]

from urllib.parse import urlparse

def get_source_reliability_score(url):
    if not url:
        return {"score": 50, "label": "Unknown"}

    domain_reliability = {
    "thehindu.com": {"score": 85, "label": "High"},
    "indianexpress.com": {"score": 82, "label": "High"},
    "ndtv.com": {"score": 75, "label": "Medium"},
    "bbc.com": {"score": 90, "label": "High"},
    "reuters.com": {"score": 88, "label": "High"},
    "livemint.com": {"score": 80, "label": "High"},
    "thewire.in": {"score": 78, "label": "Medium"},
    "scroll.in": {"score": 76, "label": "Medium"},
    "hindustantimes.com": {"score": 70, "label": "Medium"},
    "timesofindia.indiatimes.com": {"score": 68, "label": "Medium"},
    "indiatoday.in": {"score": 65, "label": "Medium"},
    "firstpost.com": {"score": 60, "label": "Medium"},
    "news18.com": {"score": 55, "label": "Medium"},
    "timesnownews.com": {"score": 45, "label": "Low"},
    "republicworld.com": {"score": 25, "label": "Low"}
}

    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "").strip()

    return domain_reliability.get(domain, {"score": 40, "label": "Not Rated"})

