import argparse
import os
import re
from scripts.translation import translate_to_french

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
    """Convert SRT timestamp to seconds."""
    # Split timestamp into hours, minutes, seconds (with milliseconds)
    timestamp_parts = srt_time.strip().split(':')
    if len(timestamp_parts) != 3:
        raise ValueError(f"Invalid timestamp format: {srt_time}")
    
    hours = int(timestamp_parts[0])
    minutes = int(timestamp_parts[1])
    seconds_parts = timestamp_parts[2].replace(',', '.').split('.')
    seconds = float(f"{seconds_parts[0]}.{seconds_parts[1]}" if len(seconds_parts) > 1 else seconds_parts[0])
    
    return hours * 3600 + minutes * 60 + seconds

def seconds_to_srt_time(seconds):
    """Convert seconds to SRT timestamp format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    millis = int((secs % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millis:03d}"

def translate_srt(input_file, refine=False):
    """Translate an SRT file from English to French."""
    # Parse SRT
    subtitles = parse_srt(input_file)
    
    # Convert timestamps to seconds for processing
    for subtitle in subtitles:
        try:
            subtitle["start"] = srt_time_to_seconds(subtitle["start"])
            subtitle["end"] = srt_time_to_seconds(subtitle["end"])
        except ValueError as e:
            print(f"⚠️ Error parsing timestamp: {e}")
            continue
    
    # Translate to French
    translated_subs = translate_to_french(subtitles)
    
    # Generate output filename
    output_file = input_file.replace(".srt", "_fr.srt")
    if "/" in output_file:
        output_file = "output/srt/" + output_file.split("/")[-1]
    
    # Write translated SRT
    with open(output_file, "w", encoding="utf-8") as f:
        for i, sub in enumerate(translated_subs, 1):
            start_time = seconds_to_srt_time(sub["start"])
            end_time = seconds_to_srt_time(sub["end"])
            f.write(f"{i}\n{start_time} --> {end_time}\n{sub['text']}\n\n")
    
    print(f"✅ Translated SRT saved to: {output_file}")
    return output_file

def main():
    parser = argparse.ArgumentParser(description="Translate an SRT file to French with DeepL.")
    parser.add_argument("input_srt", help="Path to the input SRT file")
    args = parser.parse_args()
    
    translate_srt(args.input_srt)

if __name__ == "__main__":
    main()