import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_URL = "https://api-free.deepl.com/v2/translate"

def translate_to_french(subtitles):
    """Translate English subtitles to French using DeepL."""
    if not DEEPL_API_KEY:
        raise ValueError("DEEPL_API_KEY not set in environment variables")
    
    french_subtitles = []
    for subtitle in subtitles:
        response = requests.post(
            DEEPL_URL,
            data={"auth_key": DEEPL_API_KEY, "text": subtitle["text"], "target_lang": "FR"}
        )
        if response.status_code == 200:
            translated_text = response.json()["translations"][0]["text"]
        else:
            print(f"⚠️ Translation error: {response.text}")
            translated_text = subtitle["text"]  # Fallback to original text
        french_subtitles.append({"start": subtitle["start"], "end": subtitle["end"], "text": translated_text})
    print("✅ Translation to French completed")
    return french_subtitles