import json
import os

THEME_FILE = 'theme.json'

class ThemeManager:
    @staticmethod
    def get_theme():
        if not os.path.exists(THEME_FILE):
            return {"primary": "#5865F2", "accent": "#EB459E", "error": "#ED4245"}
        
        try:
            with open(THEME_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading theme: {e}")
            return {"primary": "#5865F2", "accent": "#EB459E", "error": "#ED4245"}

    @staticmethod
    def set_theme(theme_data):
        # Validate keys
        required = ['primary', 'accent', 'error']
        if not all(k in theme_data for k in required):
            return False
            
        try:
            with open(THEME_FILE, 'w') as f:
                json.dump(theme_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving theme: {e}")
            return False
