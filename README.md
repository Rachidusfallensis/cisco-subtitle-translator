# Cisco Subtitle Translator

This project automates the generation of French subtitles for Cisco course videos. It extracts audio from videos, transcribes it to English, translates to French using DeepL, refines the translation with Anthropic's Claude 3.5, and generates SRT files.

## Prerequisites
- Python 3.8+
- API keys for:
  - [DeepL](https://www.deepl.com/pro-api) (translation)
  - [Anthropic](https://www.anthropic.com) (refinement)

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cisco-subtitle-translator.git
   cd cisco-subtitle-translator