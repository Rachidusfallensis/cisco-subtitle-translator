import argparse
import os
import re
from translation import translate_to_french
from refinement import refine_subtitles

def parse_srt(input_file):
    """Parse an SRT file into a list of subtitle dictionaries."""
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read().strip().split("\n\n")
    
    subtitles = []
    for block in content:
        lines = block.strip().split("\n")
        if len(lines) >= 2 and re.match(r"^\d+$", lines[0]):
            timestamp = lines[1]
            start, end = timestamp.split(" --> ")
            text = "\n".join(lines[2:]).strip()
            subtitles.append({"start": start, "end": end, "text": text})
    return subtitles

def srt_time_to_seconds(srt_time):
    """Convert SRT timestamp (HH:MM:SS,MMM) to seconds."""
    # Split into time and milliseconds parts
    time_part, millis_part = srt_time.replace(" ", "").split(",")
    h, m, s = time_part.split(":")
    hours = int(h)
    minutes = int(m)
    seconds = int(s)
    millis = int(millis_part)
    return hours * 3600 + minutes * 60 + seconds + millis / 1000

def srt_to_list(subtitles):
    """Convert SRT format timestamps to seconds for processing."""
    return [{"start": srt_time_to_seconds(s["start"]), "end": srt_time_to_seconds(s["end"]), "text": s["text"]}
            for s in subtitles]

def list_to_srt(subtitles):
    """Convert subtitle list back to SRT format."""
    def seconds_to_srt_time(seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int((secs % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millis:03d}"
    
    srt_content = []
    for i, sub in enumerate(subtitles, 1):
        start_time = seconds_to_srt_time(sub["start"])
        end_time = seconds_to_srt_time(sub["end"])
        srt_content.append(f"{i}\n{start_time} --> {end_time}\n{sub['text']}\n")
    return "\n".join(srt_content)

def translate_srt(input_file, target_lang="fr", refine=False):
    """Translate an SRT file using DeepL and optionally refine with Claude."""
    output_file = os.path.join("output/srt", f"{os.path.splitext(os.path.basename(input_file))[0]}_{target_lang}.srt")
    os.makedirs("output/srt", exist_ok=True)

    # Parse SRT
    subtitles = parse_srt(input_file)
    original_subs = srt_to_list(subtitles)  # For refinement
    
    # Translate to French with DeepL
    translated_subs = translate_to_french(original_subs)
    
    # Optionally refine with Claude
    if refine:
        translated_subs = refine_subtitles(original_subs, translated_subs)
    
    # Write to SRT
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(list_to_srt(translated_subs))
    print(f"✅ Translated SRT saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Translate an SRT file to French with DeepL and optional Claude refinement.")
    parser.add_argument("input_srt", help="Path to the input SRT file")
    parser.add_argument("--no-refine", action="store_true", help="Skip refinement with Claude")
    args = parser.parse_args()
    
    translate_srt(args.input_srt, refine=not args.no_refine)

if __name__ == "__main__":
    main()