import sys
import os
from audio_extraction import extract_audio
from transcription import transcribe_audio
from translation import translate_to_french
from refinement import refine_subtitles
from srt_generator import generate_srt

def main(video_path):
    """Main function to process a video and generate French subtitles."""
    print(f"Starting subtitle generation for {video_path}...")
    
    # Extract audio
    audio_file = extract_audio(video_path)
    
    # Transcribe to English
    english_subtitles = transcribe_audio(audio_file)
    
    # Translate to French
    french_subtitles = translate_to_french(english_subtitles)
    
    # Refine with Claude 3.5
    refined_subtitles = refine_subtitles(english_subtitles, french_subtitles)
    
    # Generate SRT file with video-specific name
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    srt_filename = f"{video_name}_fr.srt"
    generate_srt(refined_subtitles, filename=srt_filename)
    
    print("✅ Process completed!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <video_path>")
        sys.exit(1)
    video_path = sys.argv[1]
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        sys.exit(1)
    main(video_path)