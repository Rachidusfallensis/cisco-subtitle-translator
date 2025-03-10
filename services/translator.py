import os
import json
import time
import logging
from typing import Dict, List, Tuple, Optional
import requests
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for handling translations using DeepL and Anthropic Claude."""
    
    def __init__(self):
        self.deepl_api_key = os.getenv('DEEPL_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.anthropic = Anthropic(api_key=self.anthropic_api_key)
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> Tuple[str, Optional[Dict]]:
        """Translate text using DeepL with retry mechanism."""
        errors = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    'https://api-free.deepl.com/v2/translate',
                    headers={'Authorization': f'DeepL-Auth-Key {self.deepl_api_key}'},
                    data={
                        'text': text,
                        'source_lang': source_lang,
                        'target_lang': target_lang,
                        'preserve_formatting': 1
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result['translations'][0]['text'], None
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Translation attempt {attempt + 1} failed: {str(e)}")
                errors = {'type': 'api_error', 'message': str(e)}
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
                
        return text, errors
    
    def refine_translation(self, original: str, translation: str) -> Tuple[str, Optional[Dict]]:
        """Refine translation using Anthropic Claude."""
        try:
            prompt = (
                f"{HUMAN_PROMPT}Please review and refine this translation from English to French. "
                f"Maintain the meaning while ensuring natural, fluent French.\n\n"
                f"Original English:\n{original}\n\n"
                f"Current French Translation:\n{translation}\n\n"
                f"Please provide the refined French translation only."
                f"{AI_PROMPT}"
            )
            
            completion = self.anthropic.completions.create(
                model="claude-2",
                prompt=prompt,
                max_tokens_to_sample=1000,
                temperature=0.3
            )
            
            return completion.completion.strip(), None
            
        except Exception as e:
            logger.error(f"Refinement error: {str(e)}")
            return translation, {'type': 'refinement_error', 'message': str(e)}
    
    def analyze_quality(self, original: str, translation: str) -> Dict:
        """Analyze translation quality using various metrics."""
        try:
            # Basic metrics
            orig_words = len(original.split())
            trans_words = len(translation.split())
            length_ratio = trans_words / orig_words if orig_words > 0 else 0
            
            # Use Claude to evaluate quality
            prompt = (
                f"{HUMAN_PROMPT}Please analyze this translation from English to French and provide "
                f"a quality score (0-100) with brief explanation.\n\n"
                f"Original English:\n{original}\n\n"
                f"French Translation:\n{translation}\n\n"
                f"Provide the response in JSON format with 'score' and 'explanation' fields."
                f"{AI_PROMPT}"
            )
            
            completion = self.anthropic.completions.create(
                model="claude-2",
                prompt=prompt,
                max_tokens_to_sample=500,
                temperature=0.3
            )
            
            try:
                quality_data = json.loads(completion.completion)
            except json.JSONDecodeError:
                quality_data = {'score': 70, 'explanation': 'Quality analysis format error'}
            
            return {
                'length_ratio': length_ratio,
                'quality_score': quality_data.get('score', 70),
                'explanation': quality_data.get('explanation', 'No explanation provided'),
                'word_count': {
                    'original': orig_words,
                    'translation': trans_words
                }
            }
            
        except Exception as e:
            logger.error(f"Quality analysis error: {str(e)}")
            return {
                'length_ratio': 1.0,
                'quality_score': 50,
                'explanation': f'Quality analysis failed: {str(e)}',
                'word_count': {
                    'original': orig_words,
                    'translation': trans_words
                }
            } 