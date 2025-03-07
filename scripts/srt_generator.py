import os

def seconds_to_srt_time(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,MMM)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def generate_srt(subtitles, output_dir="output/srt", filename="course_fr.srt"):
    """Generate an SRT file from subtitles."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, filename)
    with open(output_file, "w", encoding="utf-8") as f:
        for i, subtitle in enumerate(subtitles, 1):
            start_time = seconds_to_srt_time(subtitle["start"])
            end_time = seconds_to_srt_time(subtitle["end"])
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{subtitle['text']}\n\n")
    print(f"✅ SRT file generated: {output_file}")
    return output_file