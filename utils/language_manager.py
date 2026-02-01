import json
import os

LANG_DIR = 'languages'
DEFAULT_LANG = 'en'

class LanguageManager:
    _current_lang = DEFAULT_LANG
    _cache = {}

    @classmethod
    def load_language(cls, lang_code):
        if lang_code in cls._cache:
            return cls._cache[lang_code]
        
        file_path = os.path.join(LANG_DIR, f'{lang_code}.json')
        if not os.path.exists(file_path):
            return {}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._cache[lang_code] = data
                return data
        except Exception:
            return {}
            
    @classmethod
    def t(cls, key, **kwargs):
        # Try current language
        lang_data = cls.load_language(cls._current_lang)
        text = lang_data.get(key)
        
        # Fallback to default if missing
        if not text and cls._current_lang != DEFAULT_LANG:
            default_data = cls.load_language(DEFAULT_LANG)
            text = default_data.get(key)
            
        if not text:
            return key
            
        # Format string
        try:
            return text.format(**kwargs)
        except:
            return text

    @classmethod
    def set_language(cls, lang_code):
        if os.path.exists(os.path.join(LANG_DIR, f'{lang_code}.json')):
            cls._current_lang = lang_code
            return True
        return False

    @classmethod
    def get_language(cls):
        return cls._current_lang

    @classmethod
    def get_available_languages(cls):
        if not os.path.exists(LANG_DIR):
            return []
        files = [f[:-5] for f in os.listdir(LANG_DIR) if f.endswith('.json')]
        return files
