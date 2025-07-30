# 📰 Multilingual News Bias Detector with Political Leaning

A full-stack web app that lets users analyze the **bias, tone, and political leaning** of multilingual news articles (English & Hindi supported). It offers detailed visualizations and human-friendly summaries of tone, bias, and sentiment — with support for manual text input, file uploads, and source reliability scoring.

---

## 🔍 Features

✅ **Multilingual Support** (English + Hindi)  
✅ **News URL Extraction & Translation**  
✅ **Manual Input & File Upload (.txt / .pdf)**  
✅ **Bias Detection** (Polarity + Subjectivity)  
✅ **Sentence-wise Tone & Political Leaning**  
✅ **Party-wise Summary & Filtering (BJP, Congress, AAP)**  
✅ **Visual Gauges, Bar & Pie Charts**  
✅ **Source Reliability Score**  
✅ **API-Frontend Architecture** (Flask + Streamlit)

---

## 🧠 How It Works

1. **You provide** a news article (URL / pasted / file).
2. **The backend** extracts the content, detects the language, and translates if needed.
3. It runs **tone + bias + political analysis** using transformer models.
4. The frontend **displays results visually**, with explanation & interaction.

---

## 📸 Screenshots

| Bias Analysis + Gauges         | Sentence-Level Breakdown              |
| ------------------------------ | ------------------------------------- |
| ![Bias](assets/bias_gauge.png) | ![Tone](assets/sentence_analysis.png) |

> _(Add your actual screenshots in the `assets/` folder.)_

---

## 📁 Folder Structure

```bash
news-bias-detector/
├── app/
│   └── main.py           # Flask backend API
├── dashboard/
│   └── app.py            # Streamlit frontend
├── utils/
│   └── news_utils.py     # Article extraction & NLP
├── assets/               # Images for README
├── requirements.txt
├── README.md
└── venv/                 # (your virtual environment)

Prerequisites
Python 3.11+

macOS/Linux/Windows

pip and virtualenv installed

Installation
bash
Copy
Edit
# Clone the repo
git clone https://github.com/yourusername/news-bias-detector.git
cd news-bias-detector

# Create a virtual environment
python3.11 -m venv venv
source venv/bin/activate     # Use venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
🧪 Run the Project
1. Start Backend (Flask API)
bash
Copy
Edit
cd app
python main.py
2. Start Frontend (Streamlit Dashboard)
In a new terminal:

bash
Copy
Edit
cd dashboard
streamlit run app.py
By default, Streamlit runs at: http://localhost:8501

🧰 Tech Stack
Frontend: Streamlit + Plotly + Python

Backend: Flask + newspaper3k + langdetect + transformers (HuggingFace)

ML Models: Sentiment & political tone using cardiffnlp/twitter-roberta-base-sentiment

NLP Libraries: TextBlob, NLTK, PyPDF2, Googletrans

📦 APIs Used
All APIs are free and open source:

newspaper3k – article extraction

langdetect – language detection

googletrans – translation

textblob / transformer – sentiment

Optional: add your own source database for reliability scoring

📊 Interpretation Guide
Polarity: -1 (strongly left/negative) → +1 (strongly right/positive)

Subjectivity: 0 (factual/objective) → 1 (opinionated/subjective)

Bias Labels:

🟥 Left-Leaning: polarity < -0.3

🟦 Right-Leaning: polarity > 0.3

🟩 Moderate / Center: between extremes

🟨 Neutral: low subjectivity

🛡️ License
This project is licensed under the MIT License.

👨‍💻 Author
Harshvardhan Rawat
🚀 LinkedIn • 🌐 Portfolio • 🐙 GitHub

🙏 Acknowledgements
HuggingFace Transformers

CardiffNLP for sentiment models

Streamlit & Plotly community

Google Translate (via googletrans)

News sources used for testing

⭐️ Show Your Support!
If you found this useful:

⭐ Star this repo

🐦 Share on Twitter

🧠 Fork for your own use

yaml
Copy
Edit

---

Let me know if you'd like a **PDF version**, a **case study summary**, or even a **video
```
