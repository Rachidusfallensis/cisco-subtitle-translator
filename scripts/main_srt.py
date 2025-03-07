import sys
import os
import argparse
from srt_translator_copy import translate_srt, parse_srt, srt_to_list

def main():
    parser = argparse.ArgumentParser(description="Translate French subtitles from SRT files in input_srt/ directory.")
    parser.add_argument("srt_file", help="Name of the SRT file in input_srt/ (e.g., 1.0.3_Definition_of_AI.srt)")
    parser.add_argument("--no-refine", action="store_true", help="Skip refinement with Claude")
    
    args = parser.parse_args()
    
    srt_path = os.path.join("input_srt", args.srt_file)
    if not os.path.exists(srt_path):
        print(f"Error: SRT file not found at {srt_path}")
        sys.exit(1)
    
    # Translate and refine
    translate_srt(srt_path, refine=not args.no_refine)
    
    # Show refinement changes
    if not args.no_refine:
        original_subs = srt_to_list(parse_srt(srt_path))
        translated_path = os.path.join("output/srt", f"{os.path.splitext(args.srt_file)[0]}_fr.srt")
        refined_subs = srt_to_list(parse_srt(translated_path))
        for orig, refined in zip(original_subs, refined_subs):
            if orig["text"] != refined["text"]:
                print(f"Refined: '{orig['text']}' -> '{refined['text']}'")

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    main()