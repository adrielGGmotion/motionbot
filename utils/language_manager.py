import json
import os

LANG_DIR = 'languages'
CUSTOM_STRINGS_PATH = 'custom/strings.json'
LANGUAGE_SETTINGS_PATH = 'settings/language.json'
DEFAULT_LANG = 'en'

class LanguageManager:
    _current_lang = DEFAULT_LANG
    _cache = {}
    _custom_strings = {}

    @classmethod
    def load_settings(cls):
        # Load current language from settings
        if os.path.exists(LANGUAGE_SETTINGS_PATH):
            try:
                with open(LANGUAGE_SETTINGS_PATH, 'r') as f:
                    data = json.load(f)
                    cls._current_lang = data.get('language', DEFAULT_LANG)
            except:
                pass
        
        # Load custom strings
        if os.path.exists(CUSTOM_STRINGS_PATH):
            try:
                with open(CUSTOM_STRINGS_PATH, 'r', encoding='utf-8') as f:
                    cls._custom_strings = json.load(f)
            except:
                pass

    @classmethod
    def save_settings(cls):
        os.makedirs(os.path.dirname(LANGUAGE_SETTINGS_PATH), exist_ok=True)
        try:
            with open(LANGUAGE_SETTINGS_PATH, 'w') as f:
                json.dump({'language': cls._current_lang}, f, indent=4)
        except:
            pass

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
        # 1. Custom string override
        text = cls._custom_strings.get(key)
        
        # 2. Try current language
        if not text:
            lang_data = cls.load_language(cls._current_lang)
            text = lang_data.get(key)
        
        # 3. Fallback to default if missing
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
            cls.save_settings()
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

# Initialize on import
LanguageManager.load_settings()
