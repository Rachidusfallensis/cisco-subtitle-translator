from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=ANTHROPIC_API_KEY)

def refine_subtitles(english_subtitles, french_subtitles):
    """Refine French subtitles using Claude 3.5 Sonnet with English context."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in environment variables")
    
    refined_subtitles = []
    for eng, fr in zip(english_subtitles, french_subtitles):
        prompt = (
            f"Given the English transcription '{eng['text']}' and the translated French subtitle '{fr['text']}', "
            "refine the French text to match the technical context of a Cisco course video. Ensure natural phrasing and accuracy."
        )
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            refined_text = response.content[0].text
        except Exception as e:
            print(f"⚠️ Refinement error: {e}")
            refined_text = fr["text"]  # Fallback to unrefined text
        refined_subtitles.append({"start": fr["start"], "end": fr["end"], "text": refined_text})
    print("✅ Refinement completed with Claude 3.5")
    return refined_subtitles