# app/main.py
from langdetect import detect
import sys
import os
import re
from textblob import TextBlob


# Add project root (parent of app/) to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify
from utils.news_utils import extract_article, translate_to_english, analyze_bias,sentence_tone_breakdown, get_source_reliability_score


app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        
        # 📝 Check if manual input
        if data.get("manual"):
            text = data.get("text", "")
            title = data.get("title", "Untitled")
            if not text.strip():
                return jsonify({"error": "No text provided."}), 400
            lang = detect(text)
            if text and lang != "en":
                translated_text = translate_to_english(text, lang)
            else:
                translated_text = text or "No text available for translation."
            bias_data = analyze_bias(translated_text)
            political_scores = detect_political_leaning(translated_text)
        else:
            # 🔗 Handle normal URL flow
            url = data.get("url")
            if not url:
                return jsonify({"error": "URL is required"}), 400

            article_data = extract_article(url)
            if not article_data.get("text"):
                return jsonify({"error": "Article extraction failed"}), 500

            text = article_data["text"]
            title = article_data["title"]
            lang = article_data["language"]
            translated_text = translate_to_english(text, lang)

        bias_data = analyze_bias(translated_text)
        political_scores = detect_political_leaning(translated_text)
        url = data.get("url")  # safely get it (could be None)

        if url:
            score_info = get_source_reliability_score(url)
        else:
            score_info = {"score": "N/A", "label": "N/A"}  # fallback for manual mode

        tone_data = sentence_tone_breakdown(translated_text)

        return jsonify({
            "title": title,
            "language": lang,
            "text": text,
            "translated_text": translated_text if lang != "en" else None,
            "bias_analysis": bias_data,
            "tone_breakdown": tone_data,
            "source_reliability": score_info,
            "political_leaning": political_scores,
        })

    except Exception as e:
        print("Error in /analyze:", e)
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

def detect_political_leaning(text):
    """
    Detect sentiment polarity toward political parties/entities.
    """
    parties = {
        "BJP": ["BJP", "Modi", "NDA", "RSS"],
        "Congress": ["Congress", "Rahul Gandhi", "UPA"],
        "AAP": ["Aam Aadmi Party", "AAP", "Arvind Kejriwal"]
    }

    results = {}
    for party, keywords in parties.items():
        matched_sentences = []
        for keyword in keywords:
            matches = re.findall(rf"([^.]*\b{keyword}\b[^.]*)", text, re.IGNORECASE)
            matched_sentences.extend(matches)

        if matched_sentences:
            avg_polarity = sum(TextBlob(sentence).sentiment.polarity for sentence in matched_sentences) / len(matched_sentences)
            results[party] = round(avg_polarity, 3)

    return results




# 🔥 This line is critical — without it, nothing will run
if __name__ == "__main__":
    print("Flask server starting...")
    app.run(debug=True)
