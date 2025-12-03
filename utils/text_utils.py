import re
from typing import List

def clean_text(text: str) -> str:
    """Очищення тексту від зайвих символів"""
    # Видалення множинних пробілів
    text = re.sub(r'\s+', ' ', text)
    # Видалення пробілів на початку/кінці
    text = text.strip()
    return text

def truncate_text(text: str, max_length: int = 500) -> str:
    """Обрізання тексту до максимальної довжини"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def split_into_sentences(text: str) -> List[str]:
    """Розбиття тексту на речення"""
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]
