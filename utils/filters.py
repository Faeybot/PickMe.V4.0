import re

# Daftar kata kasar/sensitif
PROFANITY_LIST = [
    "anjing", "bangsat", "kontol", "memek", "ngentot", 
    "jembut", "goblok", "tolol", "open bo", "vcs", "judi"
]

def clean_text(text: str) -> bool:
    """Mengembalikan True jika teks aman, False jika kotor"""
    if not text:
        return True
    
    text_lower = text.lower()
    for word in PROFANITY_LIST:
        if word in text_lower:
            return False
    return True
  
