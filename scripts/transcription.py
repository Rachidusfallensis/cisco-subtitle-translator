import speech_recognition as sr
from pydub import AudioSegment
import os

def transcribe_audio(audio_path):
    """Transcribe audio to English text with timestamps."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_wav(audio_path)
    chunk_length_ms = 10000  # 1 minute
    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
    
    subtitles = []
    for i, chunk in enumerate(chunks):
        chunk_file = f"output/audio/chunk_{i}.wav"
        chunk.export(chunk_file, format="wav")
        
        with sr.AudioFile(chunk_file) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                start_time = i * 60
                end_time = (i + 1) * 60 if (i + 1) * 60 < len(audio) / 1000 else len(audio) / 1000
                subtitles.append({"start": start_time, "end": end_time, "text": text})
            except Exception as e:
                print(f"⚠️ Chunk {i}: Transcription failed - {e}")
                subtitles.append({"start": i * 60, "end": (i + 1) * 60, "text": "[Transcription failed]"})
        os.remove(chunk_file)  # Clean up
    print("✅ Transcription completed")
    return subtitles