"""Translation quality analysis and monitoring module."""
import re
import time
from typing import Dict, Any

class QualityAnalyzer:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {}

    def analyze_translation(self, original_text: str, translated_text: str) -> Dict[str, Any]:
        """Analyze translation quality metrics."""
        metrics = {
            'length_ratio': self._calculate_length_ratio(original_text, translated_text),
            'preserved_placeholders': self._check_preserved_placeholders(original_text, translated_text),
            'confidence_score': self._calculate_confidence_score(original_text, translated_text),
            'processing_time': time.time() - self.start_time
        }
        self.metrics = metrics
        return metrics

    def _calculate_length_ratio(self, original: str, translated: str) -> float:
        """Calculate the length ratio between original and translated text."""
        if not original:
            return 0.0
        return len(translated) / len(original)

    def _check_preserved_placeholders(self, original: str, translated: str) -> bool:
        """Check if placeholders (numbers, timestamps, etc.) are preserved."""
        original_placeholders = set(re.findall(r'\{.*?\}|\[.*?\]|\d+:\d+:\d+,\d+', original))
        translated_placeholders = set(re.findall(r'\{.*?\}|\[.*?\]|\d+:\d+:\d+,\d+', translated))
        return original_placeholders == translated_placeholders

    def _calculate_confidence_score(self, original: str, translated: str) -> float:
        """Calculate a confidence score for the translation."""
        score = 1.0
        
        # Length ratio penalty
        length_ratio = self._calculate_length_ratio(original, translated)
        if length_ratio < 0.5 or length_ratio > 2.0:
            score *= 0.8
        
        # Placeholder preservation
        if not self._check_preserved_placeholders(original, translated):
            score *= 0.7
        
        # Additional checks can be added here
        
        return max(0.0, min(1.0, score))

    def get_quality_summary(self) -> Dict[str, Any]:
        """Get a summary of translation quality metrics."""
        if not self.metrics:
            return {"error": "No analysis performed yet"}
        
        quality_level = "high" if self.metrics['confidence_score'] > 0.8 else \
                       "medium" if self.metrics['confidence_score'] > 0.6 else "low"
        
        return {
            "quality_level": quality_level,
            "confidence_score": self.metrics['confidence_score'],
            "processing_time": f"{self.metrics['processing_time']:.2f}s",
            "length_ratio": f"{self.metrics['length_ratio']:.2f}",
            "placeholders_preserved": self.metrics['preserved_placeholders']
        } 