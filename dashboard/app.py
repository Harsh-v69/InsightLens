import streamlit as st
import requests
import PyPDF2
import plotly.graph_objects as go

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="InsightLens: News Bias Detector",
    layout="centered",
    initial_sidebar_state="expanded", # Sidebar starts expanded
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': "https://www.example.com/bug",
        'About': "# This is a **News Bias Detector** app. Learn more at [Our Website](https://www.example.com)."
    }
)

api_url = "http://127.0.0.1:5000/analyze"

# --- Custom CSS for Blue + White Theme ---
custom_css = """
<style>
    /* Overall Page Background (Blue) */
    .stApp {
        background-color: #003366; /* Darker Blue for main background */
        color: #F0F2F6; /* Light grey text on blue background for general elements */
    }

    /* Main Content Area (White Card) */
    .main .block-container {
        background-color: #FFFFFF; /* White background for the main content block */
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
        color: #26272B; /* Dark text inside the white card */
        margin-top: 20px;
        margin-bottom: 20px;
    }

    /* Sidebar Background (Lighter Blue) */
    .stSidebar {
        background-color: #004080; /* Slightly lighter blue for sidebar */
        color: #FFFFFF; /* White text on sidebar */
        padding-top: 30px;
    }
    .stSidebar .stRadio > label {
        color: #FFFFFF; /* White text for radio button labels in sidebar */
        font-weight: bold;
    }
    .stSidebar .stRadio div[role="radiogroup"] label span { /* For specific radio option text */
        color: #E0F2F7;
    }


    /* Headers and Subheaders on the main blue background (like app title, initial description, and section titles before the white card) */
    h1, h2, /* General H1 and H2 - app title and analysis type title */
    .stMarkdown h3 /* Headers like 'Bias Analysis' if they appear outside the white card as per screenshot */
    {
        color: #FFFFFF !important; /* Force White for these top-level headers for visibility on blue */
    }

    /* Headers and Subheaders within the white content area (most analysis sub-sections) */
    .main h3, .main h4, .main h5, .main h6 {
        color: #003366 !important; /* Darker blue for headings inside the white card */
    }

    /* Text inputs and text areas (editable) */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #F8F8F8; /* Light grey background */
        border: 1px solid #ADD8E6; /* Light blue border */
        color: #26272B; /* Dark text */
        border-radius: 5px;
        padding: 8px 12px;
    }
    .stTextInput > label, .stTextArea > label {
        color: #003366; /* Dark blue label for clarity on white card */
        font-weight: bold;
    }

    /* --- IMPORTANT FIX FOR TEXT IN DISABLED TEXTAREAS (ARTICLE VIEW) --- */
    /* This targets the disabled textarea and its content wrapper to ensure white text on dark blue background */
    .stTextArea > div > div > textarea[disabled],
    .stTextArea > div > div > div[data-baseweb="textarea"] { /* Target the inner container of the textarea */
        background-color: #004d80 !important; /* Force a consistent dark blue background */
        color: white !important; /* Force white text for visibility */
        -webkit-text-fill-color: white !important; /* Specific for webkit browsers for disabled text */
        opacity: 1 !important; /* Ensure no fading effect */
    }
    /* Also for disabled text input fields, if any */
    .stTextInput > div > div > input[disabled] {
        background-color: #004d80 !important;
        color: white !important;
        -webkit-text-fill-color: white !important;
        opacity: 1 !important;
    }

    /* --- IMPORTANT FIX FOR METRIC LABELS (BIAS, POLARITY, SUBJECTIVITY) --- */
    /* These labels appear on the main dark blue background in your screenshot */
    [data-testid="stMetricLabel"] {
        color: #FFFFFF !important; /* Force white labels for visibility on dark blue background */
        font-size: 1.1em; /* Slightly adjusted size */
        font-weight: bold; /* Make labels bold for prominence */
    }
    /* Metric Values (already set to blue, will stand out on blue background) */
    [data-testid="stMetricValue"] {
        color: #1E90FF !important; /* Ensure values are also visible */
        font-size: 2.5em; /* Make metrics larger */
    }
    [data-testid="stMetricDelta"] {
        color: #28a745 !important; /* Green for delta */
    }


    /* --- NEW FIX: RADIO BUTTON LABELS IN ARTICLE VIEW SECTION --- */
    /* These labels appear on a white background, so they need dark blue text */
    .main .stRadio div[role="radiogroup"] label {
        color: #003366 !important; /* Darker blue for radio options on white card */
        font-weight: normal; /* Keep normal weight for labels */
    }
    .main .stRadio div[role="radiogroup"] label span {
        color: #003366 !important; /* Make the actual text darker blue for visibility on white */
    }
    /* Fragile selector for *selected* radio button text in main content */
    .main .stRadio div[role="radiogroup"] label.css-1e5z8ev span {
        color: #1E90FF !important; /* Highlight selected radio button text with primary blue */
    }

    /* Alert boxes (info, success, warning, error) */
    .stAlert {
        border-left: 5px solid;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        color: #26272B !important; /* Ensure text is dark inside alerts */
    }
    .stAlert.info {
        background-color: #E0F2F7; /* Light blue for info */
        border-color: #2196F3; /* Blue border */
    }
    .stAlert.success {
        background-color: #E6FFE6; /* Light green for success */
        border-color: #4CAF50; /* Green border */
    }
    .stAlert.warning {
        background-color: #FFF3E0; /* Light orange for warning */
        border-color: #FF9800; /* Orange border */
    }
    .stAlert.error {
        background-color: #FFE0E6; /* Light red for error */
        border-color: #F44336; /* Red border */
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #E0F2F7; /* Light blue background for expander header */
        color: #003366 !important; /* Dark blue text */
        border-radius: 8px;
        padding: 12px;
        border: 1px solid #ADD8E6;
        font-weight: bold;
        transition: background-color 0.2s ease;
    }
    .streamlit-expanderHeader:hover {
        background-color: #CEEAF5; /* Slightly darker on hover */
    }
    .streamlit-expanderContent {
        background-color: #F8F8F8; /* Very light grey content background */
        border: 1px solid #E0F2F7;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 15px;
        color: #26272B !important; /* Dark text inside expander content */
    }

    /* Horizontal Rules */
    hr {
        border-top: 1px solid #ADD8E6; /* Light blue border for HR */
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    /* Markdown text color for general content */
    .main p, .main li, .main blockquote {
        color: #26272B !important; /* Dark text for general content in main area (on white card) */
    }

    /* Footer styling */
    .footer {
        text-align: center;
        color: #B0C4DE; /* Light steel blue for footer on blue background */
        padding: 20px 0;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# --- Application Title and Description (On the Blue Background) ---
st.title("📰 InsightLens: News Bias Detector")
st.markdown("Unlock the truth behind news articles. Simply provide a URL or paste text below to analyze its **bias**, **political leaning**, and **source reliability**. Supports Hindi and English!")

st.markdown("---")

# --- Sidebar for Navigation ---
st.sidebar.title("🚀 Navigation")
input_mode = st.sidebar.radio(
    "Choose Input Mode:",
    ["🔗 Analyze from URL", "📝 Paste Your Own Text"],
    index=0, # Default to URL
    key="sidebar_input_mode", # Unique key for radio button
)
st.sidebar.markdown("---")
st.sidebar.info("Select an option above to get started!")


# --- Main Content Area (Conditional on Input Mode) ---
if input_mode == "🔗 Analyze from URL":
    st.markdown("### 🔗 Analyze a News Article from URL") # This subheader is on the blue background
    url = st.text_input("Enter News Article URL:", "")

    if url:
        with st.spinner("Analyzing news article... This may take a moment."):
            try:
                response = requests.post(api_url, json={"url": url})
                data = response.json()
                if "error" in data:
                    st.error(f"❌ Error: {data['error']}")
                else:
                    st.success("Analysis Complete! ✅")

                    # These elements are expected to be on the blue background, as per your screenshots
                    st.header(data.get("title", "News Article Analysis")) # This header is on the blue background
                    st.info(f"**Detected Language**: `{data.get('language', 'unknown').upper()}`") # This info box will be on blue background

                    st.markdown("---")
                    
                    st.subheader("🧠 Bias Analysis") # This subheader is on the blue background
                    bias = data.get("bias_analysis", {})
                    
                    # Metrics should now have white labels on the blue background (as per screenshot)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="Bias", value=bias.get('bias', 'N/A'))
                    with col2:
                        st.metric(label="Polarity", value=f"{bias.get('polarity', 0):.2f}", delta_color="off")
                    with col3:
                        st.metric(label="Subjectivity", value=f"{bias.get('subjectivity', 0):.2f}", delta_color="off")

                    st.markdown("---") # This horizontal line will also be on the main blue background

                    # Start of the white content block for detailed analysis results
                    # Everything inside this 'with st.container()' will appear on the white card
                    with st.container():
                        st.markdown("<h3>🔍 Understanding Your Bias Scores</h3>", unsafe_allow_html=True) # Custom HTML header for styling
                        st.markdown("""
                        - **Bias Label**: Our AI categorizes the article's overall slant (e.g., Left-Leaning, Neutral).
                        - **Polarity**: Measures the emotional tone, ranging from -1 (very negative/left) to +1 (very positive/right).
                        - **Subjectivity**: Indicates how opinionated the text is, from 0 (highly objective, factual) to 1 (very subjective, opinion-based).
                        """)

                        st.markdown("---")
                        
                        st.markdown("<h3>🏛️ Political Sentiment Analysis</h3>", unsafe_allow_html=True)
                        political = data.get("political_leaning", {})
                        if not political:
                            st.warning("No prominent political party mentions detected in this article.")
                        else:
                            st.write("Sentiment towards mentioned political parties:")
                            leaning_summary = ""
                            for party, polarity in political.items():
                                if polarity > 0.2:
                                    sentiment = "🟢 Positive"
                                elif polarity < -0.2:
                                    sentiment = "🔴 Negative"
                                else:
                                    sentiment = "🟡 Neutral"
                                st.markdown(f"- **{party}**: `{polarity:.2f}` → **{sentiment}**")
                            
                            if political:
                                max_party = max(political, key=lambda x: abs(political[x]))
                                max_score = political[max_party]
                                if abs(max_score) < 0.2:
                                    leaning_summary = "🟨 **Overall:** The article does not strongly lean toward any single political party."
                                elif max_score > 0:
                                    leaning_summary = f"🟩 **Overall:** The article shows **positive sentiment toward {max_party}**."
                                else:
                                    leaning_summary = f"🟥 **Overall:** The article shows **negative sentiment toward {max_party}**."

                                st.success(leaning_summary)

                        st.markdown("---")
                        
                        st.markdown("<h3>🌐 Source Reliability Assessment</h3>", unsafe_allow_html=True)
                        reliability = data.get("source_reliability", {})
                        rel_score = reliability.get("score")
                        rel_label = reliability.get("label", "Unknown")

                        if isinstance(rel_score, (int, float)):
                            st.metric(label="Reliability Score", value=f"{rel_score}", delta=f"({rel_label})")
                            st.markdown("<h4>📊 Source Credibility Gauge</h4>", unsafe_allow_html=True)
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=rel_score,
                                title={"text": "Source Reliability Index", "font": {"size": 18, "color": "#003366"}},
                                gauge={
                                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#003366"},
                                    'bar': {'color': "#1E90FF"},
                                    'steps': [
                                        {'range': [0, 49], 'color': "#FF6347"},
                                        {'range': [50, 79], 'color': "#FFD700"},
                                        {'range': [80, 100], 'color': "#3CB371"}
                                    ],
                                    'threshold': {
                                        'line': {'color': "#DC143C", 'width': 4},
                                        'thickness': 0.75,
                                        'value': rel_score
                                    }
                                }
                            ))
                            fig.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.warning("⚠️ Source reliability score is not available for this domain. We continually expand our database!")

                        st.markdown("---")
                        
                        st.markdown("<h4>🎨 Bias Category Legend</h4>", unsafe_allow_html=True)
                        st.markdown("""
                        - 🟥 **Left-Leaning**: Indicates a progressive or liberal viewpoint (Polarity < -0.3)
                        - 🟦 **Right-Leaning**: Suggests a conservative or traditional viewpoint (Polarity > 0.3)
                        - 🟨 **Neutral**: Minimal emotional or opinionated language (Subjectivity < 0.4)
                        - 🟩 **Moderate / Center**: Balanced views, falling between extremes.
                        """)

                        st.markdown("<h3>📊 Visual Bias Gauges</h3>", unsafe_allow_html=True)
                        fig_gauges = go.Figure()

                        fig_gauges.add_trace(go.Indicator(
                            mode="gauge+number+delta",
                            value=bias["polarity"],
                            domain={'x': [0, 0.48], 'y': [0, 1]},
                            title={'text': "Polarity (Sentiment)", 'font': {"size": 18, "color": "#003366"}},
                            delta={'reference': 0, 'increasing': {'color': "#1E90FF"}, 'decreasing': {'color': "#DC143C"}},
                            gauge={
                                'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': "#003366"},
                                'bar': {'color': "lightgray"},
                                'steps': [
                                    {'range': [-1, -0.3], 'color': '#FF6347'},
                                    {'range': [-0.3, 0.3], 'color': '#ADD8E6'},
                                    {'range': [0.3, 1], 'color': '#4169E1'}
                                ],
                                'threshold': {
                                    'line': {'color': "#DC143C", 'width': 3},
                                    'thickness': 0.75,
                                    'value': bias["polarity"]
                                }
                            }
                        ))

                        fig_gauges.add_trace(go.Indicator(
                            mode="gauge+number",
                            value=bias["subjectivity"],
                            domain={'x': [0.52, 1], 'y': [0, 1]},
                            title={'text': "Subjectivity (Opinionated)", 'font': {"size": 18, "color": "#003366"}},
                            gauge={
                                'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "#003366"},
                                'bar': {'color': "lightgray"},
                                'steps': [
                                    {'range': [0, 0.4], 'color': '#90EE90'},
                                    {'range': [0.4, 1], 'color': '#FFD700'}
                                ],
                                'threshold': {
                                    'line': {'color': "#DC143C", 'width': 3},
                                    'thickness': 0.75,
                                    'value': bias["subjectivity"]
                                }
                            }
                        ))
                        fig_gauges.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
                        st.plotly_chart(fig_gauges, use_container_width=True)

                        st.markdown("---")
                        
                        with st.expander("🧠 Sentence-by-Sentence Tone Breakdown", expanded=False):
                            tone_data = data.get("tone_breakdown", [])

                            if not tone_data:
                                st.info("No detailed sentence-level tone data available for this article.")
                            else:
                                st.write("Explore the sentiment of individual sentences:")
                                for i, item in enumerate(tone_data):
                                    sentence = item.get("sentence", "")
                                    polarity = item.get("polarity", 0)
                                    subjectivity = item.get("subjectivity", 0)
                                    mentions = item.get("mentions", [])

                                    if polarity < -0.3:
                                        tone_label = "🔴 Negative"
                                        color = "#FFE0E6"
                                    elif polarity > 0.3:
                                        tone_label = "🟢 Positive"
                                        color = "#E6FFE6"
                                    else:
                                        tone_label = "🟡 Neutral"
                                        color = "#FFFFE0"

                                    mention_text = ""
                                    if mentions:
                                        mention_text = f"<br><span style='font-size: 0.85em; color: #6A5ACD;'>🏛️ Mentioned: {', '.join(mentions)}</span>"

                                    st.markdown(
                                        f"""
                                        <div style="background-color: {color}; padding: 12px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #ADD8E6;">
                                            <p style="font-size: 1.1em; margin-bottom: 5px; color: #003366;"><strong>{tone_label}</strong></p>
                                            <p style="font-size: 1.0em; color: #26272B; margin-bottom: 5px;">{sentence}</p>
                                            <p style="font-size: 0.9em; color: #555; margin-bottom: 0;'>
                                                📈 Polarity: <code>{polarity:.2f}</code> | 📊 Subjectivity: <code>{subjectivity:.2f}</code>
                                            </p>
                                            {mention_text}
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                    if i < len(tone_data) - 1:
                                        st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)

                        st.markdown("---")

                        st.markdown("<h3>🗣️ What This Analysis Means for You</h3>", unsafe_allow_html=True)
                        bias_label = bias.get("bias", "Unknown")
                        polarity = bias.get("polarity", 0)
                        subjectivity = bias.get("subjectivity", 0)

                        explanation = ""
                        if bias_label == "Left-Leaning":
                            explanation += "🟥 This article demonstrates a **left-leaning** perspective, often characterized by a critical stance towards conservative viewpoints or a focus on social equality and collective welfare.\n\n"
                        elif bias_label == "Right-Leaning":
                            explanation += "🟦 This article exhibits a **right-leaning** perspective, typically showing support for conservative policies, traditional values, or individual liberties.\n\n"
                        elif bias_label == "Neutral":
                            explanation += "🟨 This article appears largely **neutral and factual**, presenting information with minimal overt emotional language or strong opinions.\n\n"
                        elif bias_label == "Moderate / Center":
                            explanation += "🟩 This article maintains a **moderately balanced** tone, incorporating some opinions but avoiding extreme bias in any particular direction.\n\n"

                        if polarity < -0.3:
                            explanation += f"- The tone is distinctly **negative** (Polarity: `{polarity:.2f}`), which may indicate a critical or skeptical approach to the subject matter.\n"
                        elif polarity > 0.3:
                            explanation += f"- The tone is notably **positive** (Polarity: `{polarity:.2f}`), suggesting endorsement, praise, or an optimistic outlook.\n"
                        else:
                            explanation += f"- The tone is **fairly balanced** (Polarity: `{polarity:.2f}`), without strong positive or negative emotional emphasis.\n"

                        if subjectivity < 0.3:
                            explanation += f"- The language used is **predominantly objective** (Subjectivity: `{subjectivity:.2f}`), focusing on verifiable facts and data rather than personal opinions."
                        elif subjectivity > 0.6:
                            explanation += f"- The language is **highly subjective** (Subjectivity: `{subjectivity:.2f}`), frequently expressing personal viewpoints, feelings, or interpretations rather than purely factual information."
                        else:
                            explanation += f"- The article presents a **mix of factual information and subjective opinions** (Subjectivity: `{subjectivity:.2f}`)."

                        st.info(explanation)
                        
                        st.markdown("---")
                        
                        with st.expander("📄 View Full Article Text", expanded=False):
                            original = data.get("text")
                            translated = data.get("translated_text")
                            lang = data.get("language", "unknown")

                            language_flags = {
                                "en": "🇺🇸 English", "hi": "🇮🇳 Hindi", "fr": "🇫🇷 French",
                                "es": "🇪🇸 Spanish", "de": "🇩🇪 German", "zh-cn": "🇨🇳 Chinese (Simplified)",
                                "ja": "🇯🇵 Japanese"
                            }
                            language_label = language_flags.get(lang, f"🌐 {lang.upper()}")

                            if not original:
                                st.warning("No article text could be retrieved.")
                            else:
                                if lang != "en" and translated:
                                    option = st.radio(
                                        "Choose text version:",
                                        [f"🌐 Translated to English 🇺🇸", f"📝 Original ({language_label})"],
                                        index=0,
                                        horizontal=True,
                                        key="text_display_url"
                                    )
                                    # Text area for translated/original text with white text
                                    if "Translated" in option:
                                        st.text_area("Translated Text", value=translated, height=400, disabled=True)
                                    else:
                                        st.text_area(f"Original Text ({language_label})", value=original, height=400, disabled=True)
                                else:
                                    st.text_area(f"Original Text ({language_label})", value=original, height=400, disabled=True)
                    # End of the white content block for analysis results
            except requests.exceptions.ConnectionError:
                st.error("❌ Could not connect to the analysis service. Please ensure the backend server is running.")
            except requests.exceptions.Timeout:
                st.error("⏰ The request timed out. The server might be busy or the URL is taking too long to respond.")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ An error occurred during the request: {str(e)}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

else: # Manual Text Input Mode
    st.markdown("### 📝 Enter Your News Article Manually") # This subheader is on the blue background
    title = st.text_input("📚 Article Title (Optional):", "")

    st.markdown("#### Option 1: Paste article text below")
    pasted_text = st.text_area("Paste your news article content here:", height=250)

    st.markdown("#### Option 2: Upload a .txt or .pdf file")
    uploaded_file = st.file_uploader("Upload a .txt or .pdf file:", type=["txt", "pdf"])

    extracted_text = ""
    if uploaded_file is not None:
        with st.spinner("Extracting text from file..."):
            try:
                if uploaded_file.type == "text/plain":
                    extracted_text = uploaded_file.read().decode("utf-8")
                elif uploaded_file.type == "application/pdf":
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text()
                
                if not extracted_text.strip():
                    st.error("❌ Could not extract text from the file. Please ensure it contains readable text.")
                else:
                    st.success("✅ Text successfully extracted from file.")
                    pasted_text = st.text_area("Extracted Text (You can edit this)", value=extracted_text, height=300)

            except Exception as e:
                st.error(f"❌ Failed to read file: {str(e)}. Please try another file or paste text directly.")
    
    final_text_to_analyze = pasted_text.strip() if pasted_text.strip() else extracted_text.strip()

    st.markdown("---")
    if st.button("📊 Analyze Pasted/Uploaded Text", type="primary"):
        if not final_text_to_analyze:
            st.warning("Please provide text either by pasting it directly or uploading a .txt/.pdf file to analyze.")
        else:
            with st.spinner("Analyzing your text... This may take a moment."):
                try:
                    manual_data = {
                        "manual": True,
                        "text": final_text_to_analyze,
                        "title": title if title else "Untitled Article"
                    }
                    response = requests.post(api_url, json=manual_data)
                    
                    if response.ok:
                        data = response.json()
                        st.success("Analysis Complete! ✅")

                        # Start of the white content block for analysis results
                        with st.container():
                            st.header(data.get("title", "Text Analysis Results"))
                            st.info(f"**Detected Language**: `{data.get('language', 'unknown').upper()}`")

                            st.markdown("---")
                            
                            st.subheader("🧠 Bias Analysis")
                            bias = data.get("bias_analysis", {})
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric(label="Bias", value=bias.get('bias', 'N/A'))
                            with col2:
                                st.metric(label="Polarity", value=f"{bias.get('polarity', 0):.2f}", delta_color="off")
                            with col3:
                                st.metric(label="Subjectivity", value=f"{bias.get('subjectivity', 0):.2f}", delta_color="off")

                            st.markdown("---")
                            
                            st.markdown("<h3>🔍 Understanding Your Bias Scores</h3>", unsafe_allow_html=True)
                            st.markdown("""
                            - **Bias Label**: Our AI categorizes the article's overall slant (e.g., Left-Leaning, Neutral).
                            - **Polarity**: Measures the emotional tone, ranging from -1 (very negative/left) to +1 (very positive/right).
                            - **Subjectivity**: Indicates how opinionated the text is, from 0 (highly objective, factual) to 1 (very subjective, opinion-based).
                            """)

                            st.markdown("---")
                            
                            st.markdown("<h3>🏛️ Political Sentiment Analysis</h3>", unsafe_allow_html=True)
                            political = data.get("political_leaning", {})
                            if not political:
                                st.warning("No prominent political party mentions detected in this article.")
                            else:
                                st.write("Sentiment towards mentioned political parties:")
                                leaning_summary = ""
                                for party, polarity in political.items():
                                    if polarity > 0.2:
                                        sentiment = "🟢 Positive"
                                    elif polarity < -0.2:
                                        sentiment = "🔴 Negative"
                                    else:
                                        sentiment = "🟡 Neutral"
                                    st.markdown(f"- **{party}**: `{polarity:.2f}` → **{sentiment}**")
                                
                                if political:
                                    max_party = max(political, key=lambda x: abs(political[x]))
                                    max_score = political[max_party]
                                    if abs(max_score) < 0.2:
                                        leaning_summary = "🟨 **Overall:** The article does not strongly lean toward any single political party."
                                    elif max_score > 0:
                                        leaning_summary = f"🟩 **Overall:** The article shows **positive sentiment toward {max_party}**."
                                    else:
                                        leaning_summary = f"🟥 **Overall:** The article shows **negative sentiment toward {max_party}**."

                                    st.success(leaning_summary)

                            st.markdown("---")
                            
                            st.info("🌐 Source reliability assessment is only available for articles analyzed directly from a URL.")

                            st.markdown("---")
                            
                            st.markdown("<h4>🎨 Bias Category Legend</h4>", unsafe_allow_html=True)
                            st.markdown("""
                            - 🟥 **Left-Leaning**: Indicates a progressive or liberal viewpoint (Polarity < -0.3)
                            - 🟦 **Right-Leaning**: Suggests a conservative or traditional viewpoint (Polarity > 0.3)
                            - 🟨 **Neutral**: Minimal emotional or opinionated language (Subjectivity < 0.4)
                            - 🟩 **Moderate / Center**: Balanced views, falling between extremes.
                            """)

                            st.markdown("<h3>📊 Visual Bias Gauges</h3>", unsafe_allow_html=True)
                            fig_gauges_manual = go.Figure()

                            fig_gauges_manual.add_trace(go.Indicator(
                                mode="gauge+number+delta",
                                value=bias["polarity"],
                                domain={'x': [0, 0.48], 'y': [0, 1]},
                                title={'text': "Polarity (Sentiment)", 'font': {"size": 18, "color": "#003366"}},
                                delta={'reference': 0, 'increasing': {'color': "#1E90FF"}, 'decreasing': {'color': "#DC143C"}},
                                gauge={
                                    'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "#003366"},
                                    'bar': {'color': "lightgray"},
                                    'steps': [
                                        {'range': [-1, -0.3], 'color': '#FF6347'},
                                        {'range': [-0.3, 0.3], 'color': '#ADD8E6'},
                                        {'range': [0.3, 1], 'color': '#4169E1'}
                                    ],
                                    'threshold': {
                                        'line': {'color': "#DC143C", 'width': 3},
                                        'thickness': 0.75,
                                        'value': bias["polarity"]
                                    }
                                }
                            ))

                            fig_gauges_manual.add_trace(go.Indicator(
                                mode="gauge+number",
                                value=bias["subjectivity"],
                                domain={'x': [0.52, 1], 'y': [0, 1]},
                                title={'text': "Subjectivity (Opinionated)", 'font': {"size": 18, "color": "#003366"}},
                                gauge={
                                    'axis': {'range': [0, 1], 'tickwidth': 1, 'tickcolor': "#003366"},
                                    'bar': {'color': "lightgray"},
                                    'steps': [
                                        {'range': [0, 0.4], 'color': '#90EE90'},
                                        {'range': [0.4, 1], 'color': '#FFD700'}
                                    ],
                                    'threshold': {
                                        'line': {'color': "#DC143C", 'width': 3},
                                        'thickness': 0.75,
                                        'value': bias["subjectivity"]
                                    }
                                }
                            ))
                            fig_gauges_manual.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
                            st.plotly_chart(fig_gauges_manual, use_container_width=True)

                            st.markdown("---")
                            
                            with st.expander("🧠 Sentence-by-Sentence Tone Breakdown", expanded=False):
                                tone_data = data.get("tone_breakdown", [])

                                if not tone_data:
                                    st.info("No detailed sentence-level tone data available for this article.")
                                else:
                                    st.write("Explore the sentiment of individual sentences:")
                                    for i, item in enumerate(tone_data):
                                        sentence = item.get("sentence", "")
                                        polarity = item.get("polarity", 0)
                                        subjectivity = item.get("subjectivity", 0)
                                        mentions = item.get("mentions", [])

                                        if polarity < -0.3:
                                            tone_label = "🔴 Negative"
                                            color = "#FFE0E6"
                                        elif polarity > 0.3:
                                            tone_label = "🟢 Positive"
                                            color = "#E6FFE6"
                                        else:
                                            tone_label = "🟡 Neutral"
                                            color = "#FFFFE0"

                                        mention_text = ""
                                        if mentions:
                                            mention_text = f"<br><span style='font-size: 0.85em; color: #6A5ACD;'>🏛️ Mentioned: {', '.join(mentions)}</span>"

                                        st.markdown(
                                            f"""
                                            <div style="background-color: {color}; padding: 12px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #ADD8E6;">
                                                <p style="font-size: 1.1em; margin-bottom: 5px; color: #003366;"><strong>{tone_label}</strong></p>
                                                <p style="font-size: 1.0em; color: #26272B; margin-bottom: 5px;">{sentence}</p>
                                                <p style="font-size: 0.9em; color: #555; margin-bottom: 0;'>
                                                    📈 Polarity: <code>{polarity:.2f}</code> | 📊 Subjectivity: <code>{subjectivity:.2f}</code>
                                                </p>
                                                {mention_text}
                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )
                                        if i < len(tone_data) - 1:
                                            st.markdown("<div style='height: 5px;'></div>", unsafe_allow_html=True)
                            
                            st.markdown("---")
                            
                            st.markdown("<h3>🗣️ What This Analysis Means for You</h3>", unsafe_allow_html=True)
                            bias_label = bias.get("bias", "Unknown")
                            polarity = bias.get("polarity", 0)
                            subjectivity = bias.get("subjectivity", 0)

                            explanation = ""
                            if bias_label == "Left-Leaning":
                                explanation += "🟥 This article demonstrates a **left-leaning** perspective, often characterized by a critical stance towards conservative viewpoints or a focus on social equality and collective welfare.\n\n"
                            elif bias_label == "Right-Leaning":
                                explanation += "🟦 This article exhibits a **right-leaning** perspective, typically showing support for conservative policies, traditional values, or individual liberties.\n\n"
                            elif bias_label == "Neutral":
                                explanation += "🟨 This article appears largely **neutral and factual**, presenting information with minimal overt emotional language or strong opinions.\n\n"
                            elif bias_label == "Moderate / Center":
                                explanation += "🟩 This article maintains a **moderately balanced** tone, incorporating some opinions but avoiding extreme bias in any particular direction.\n\n"

                            if polarity < -0.3:
                                explanation += f"- The tone is distinctly **negative** (Polarity: `{polarity:.2f}`), which may indicate a critical or skeptical approach to the subject matter.\n"
                            elif polarity > 0.3:
                                explanation += f"- The tone is notably **positive** (Polarity: `{polarity:.2f}`), suggesting endorsement, praise, or an optimistic outlook.\n"
                            else:
                                explanation += f"- The tone is **fairly balanced** (Polarity: `{polarity:.2f}`), without strong positive or negative emotional emphasis.\n"

                            if subjectivity < 0.3:
                                explanation += f"- The language used is **predominantly objective** (Subjectivity: `{subjectivity:.2f}`), focusing on verifiable facts and data rather than personal opinions."
                            elif subjectivity > 0.6:
                                explanation += f"- The language is **highly subjective** (Subjectivity: `{subjectivity:.2f}`), frequently expressing personal viewpoints, feelings, or interpretations rather than purely factual information."
                            else:
                                explanation += f"- The article presents a **mix of factual information and subjective opinions** (Subjectivity: `{subjectivity:.2f}`)."

                            st.info(explanation)
                            
                            st.markdown("---")
                            
                            with st.expander("📄 View Full Provided Text", expanded=False):
                                original = data.get("text")
                                translated = data.get("translated_text")
                                lang = data.get("language", "unknown")

                                language_flags = {
                                    "en": "🇺🇸 English", "hi": "🇮🇳 Hindi",
                                }
                                language_label = language_flags.get(lang, f"🌐 {lang.upper()}")

                                if not original:
                                    st.warning("No text available for display.")
                                else:
                                    if lang != "en" and translated:
                                        option = st.radio(
                                            "Choose text version:",
                                            [f"🌐 Translated to English 🇺🇸", f"📝 Original ({language_label})"],
                                            index=0,
                                            horizontal=True,
                                            key="text_display_manual"
                                        )
                                        # Text area for translated/original text with white text
                                        if "Translated" in option:
                                            st.text_area("Translated Text", value=translated, height=400, disabled=True)
                                        else:
                                            st.text_area(f"Original Text ({language_label})", value=original, height=400, disabled=True)
                                    else:
                                        st.text_area(f"Original Text ({language_label})", value=original, height=400, disabled=True)
                        # End of the white content block for analysis results
                    else:
                        st.error(f"❌ Analysis failed. Server responded with an error: {response.status_code} - {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to the analysis service. Please ensure the backend server is running.")
                except requests.exceptions.Timeout:
                    st.error("⏰ The request timed out. The server might be busy.")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ An error occurred during the request: {str(e)}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

# --- Footer (placed directly at the end of the script) ---
st.markdown("""
<div class="footer">
    <p>Powered by Advanced NLP & Machine Learning. Your feedback helps us improve!</p>
    <p>© 2025 InsightLens. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)