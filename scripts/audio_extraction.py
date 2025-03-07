from moviepy.editor import VideoFileClip
import os

def extract_audio(video_path, output_dir="output/audio"):
    """Extract audio from a video file and save as WAV."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    os.makedirs(output_dir, exist_ok=True)
    audio_output = os.path.join(output_dir, "audio.wav")
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_output)
    print(f"✅ Audio extracted: {audio_output}")
    return audio_output