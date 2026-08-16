import streamlit as st
from google import genai
from google.genai import types
import pypdf

st.set_page_config(page_title="A/L Business Studies AI Tutor", page_icon="📚")

# UI Translations Dictionary
translations = {
    "English": {
        "title": "📚 A/L Business Studies AI Tutor",
        "settings": "Settings",
        "choose_lang": "Choose Language",
        "api_key": "Enter Gemini API Key",
        "admin_area": "🔑 Admin Area",
        "admin_pass": "Admin Password",
        "access_granted": "Admin Access Granted",
        "upload_pdf": "Upload NIE Teacher Guide (PDF)",
        "chat_placeholder": "Ask a question from Business Studies...",
        "api_error": "Please enter a valid Gemini API Key in the sidebar or Streamlit Secrets.",
        "pages_loaded": "Loaded {} pages into syllabus context!"
    },
    "Sinhala": {
        "title": "📚 උසස් පෙළ ව්‍යාපාර අධ්‍යයනය AI උපකාරකය",
        "settings": "සැකසුම්",
        "choose_lang": "භාෂාව තෝරන්න",
        "api_key": "Gemini API යතුර ඇතුළත් කරන්න",
        "admin_area": "🔑 පරිපාලන කලාපය",
        "admin_pass": "පරිපාලන මුරපදය",
        "access_granted": "පරිපාලන ප්‍රවේශය තහවුරු විය",
        "upload_pdf": "ගුරු මාර්ගෝපදේශය (PDF) එක් කරන්න",
        "chat_placeholder": "ව්‍යාපාර අධ්‍යයනය විෂයෙන් ප්‍රශ්නයක් අහන්න...",
        "api_error": "කරුණාකර නිවැරදි API යතුර ඇතුළත් කරන්න හෝ Secrets හි සකසන්න.",
        "pages_loaded": "පිටු {} ක් සාර්ථකව පද්ධතියට එක් කරන ලදී!"
    },
    "Tamil": {
        "title": "📚 A/L வணிகக் கல்வி AI பயிற்றுவிப்பாளர்",
        "settings": "அமைப்புகள்",
        "choose_lang": "மொழியைத் தேர்ந்தெடுக்கவும்",
        "api_key": "Gemini API சாவி உள்ளிடவும்",
        "admin_area": "🔑 நிர்வாக பகுதி",
        "admin_pass": "நிர்வாக கடவுச்சொல்",
        "access_granted": "நிர்வாக அணுகல் அனுமதிக்கப்பட்டது",
        "upload_pdf": "ஆசிரியர் வழிகாட்டியைப் பதிவேற்றவும் (PDF)",
        "chat_placeholder": "வணிகக் கல்வியில் ஒரு கேள்வியைக் கேளுங்கள்...",
        "api_error": "தயவுசெய்து செல்லுபடியாகும் API சாவியை உள்ளிடவும்.",
        "pages_loaded": "பக்கங்கள் {} வெற்றிகரமாக ஏற்றப்பட்டன!"
    }
}

# --- SIDEBAR: SETTINGS & LANGUAGE ---
st.sidebar.header("Settings")
language = st.sidebar.selectbox("Choose Language / භාෂාව / மொழி", ["Sinhala", "English", "Tamil"])
t = translations[language]

st.title(t["title"])

# Fetch key from Streamlit Secrets if configured
default_key = st.secrets.get("GEMINI_API_KEY", "") if "GEMINI_API_KEY" in st.secrets else ""
api_key = st.sidebar.text_input(t["api_key"], value=default_key, type="password")

# Admin PDF Upload Section
st.sidebar.markdown("---")
st.sidebar.header(t["admin_area"])
admin_pass = st.sidebar.text_input(t["admin_pass"], type="password")

if admin_pass == "admin123":
    st.sidebar.success(t["access_granted"])
    uploaded_pdf = st.sidebar.file_uploader(t["upload_pdf"], type=["pdf"])
    
    if uploaded_pdf:
        reader = pypdf.PdfReader(uploaded_pdf)
        extracted = ""
        for page in reader.pages:
            extracted += page.extract_text() or ""
        st.session_state["context_pdf"] = extracted
        st.sidebar.info(t["pages_loaded"].format(len(reader.pages)))

context_data = st.session_state.get("context_pdf", "")

# --- SYSTEM PROMPT ---
SYSTEM_INSTRUCTION = f"""
You are an expert Sri Lankan G.C.E. A/L Business Studies AI Tutor following the National Institute of Education (NIE) syllabus.
Always respond in {language}.
Keep responses clear, concise, exam-focused, and direct.

Syllabus Content Context:
{context_data[:150000]}

At the end of every answer, offer a brief choice for deeper learning (e.g., past paper practice).
"""

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(t["chat_placeholder"]):
    clean_key = api_key.strip() if api_key else ""
    if not clean_key:
        st.error(t["api_error"])
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = genai.Client(api_key=clean_key)
        
        with st.chat_message("assistant"):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                ),
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"Error calling Gemini API: {str(e)}")
